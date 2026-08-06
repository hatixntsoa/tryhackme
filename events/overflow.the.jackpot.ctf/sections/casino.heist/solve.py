#!/usr/bin/env python3
"""
Overflow The Jackpot - Casino Heist solver
Run: python3 solve.py stolen_jackpot.pcapng
"""

import subprocess
import sys
import os
from pathlib import Path

from scapy.all import rdpcap, TCP, IP, Raw
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

KEY = b'J4ckp0tH4ck3rKey'
IV  = b'Iv_For_Exf1ltr8!'
EXFIL_HOST = '172.20.0.3'
EXFIL_PORT = 4444


def hexdump(data, prefix="    "):
    """Pretty hex dump with ASCII sidebar."""
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"{prefix}{i:04x}  {hex_part:<48s}  |{ascii_part}|")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 solve.py <pcap_file>")
        sys.exit(1)

    pcap_file = sys.argv[1]
    if not os.path.exists(pcap_file):
        print(f"[-] File not found: {pcap_file}")
        sys.exit(1)

    print(f"[*] Reading {pcap_file} ...")
    pkts = rdpcap(pcap_file)
    print(f"[*] {len(pkts)} packets loaded")

    # --- 1. Extract binary from HTTP stream ---
    print("\n[*] Step 1: Extracting binary from HTTP stream ...")
    http_payload = b""
    for pkt in pkts:
        if TCP in pkt and Raw in pkt:
            payload = pkt[Raw].load
            if b'Content-Type' in payload or b'Content-Length' in payload:
                if b'\r\n\r\n' in payload:
                    http_payload += payload.split(b'\r\n\r\n', 1)[1]
                else:
                    http_payload += payload
            elif http_payload:
                http_payload += payload

    if not http_payload:
        print("    [!] No HTTP body found inline, trying tshark ...")
        os.makedirs("objects", exist_ok=True)
        subprocess.run(
            ["tshark", "-r", pcap_file, "--export-objects", "http", "objects"],
            check=True, capture_output=True
        )
        bin_files = list(Path("objects").glob("*"))
        if not bin_files:
            print("[-] Could not extract binary")
            sys.exit(1)
        binary_path = str(bin_files[0])
    else:
        binary_path = "extracted_binary"
        with open(binary_path, "wb") as f:
            f.write(http_payload)

    print(f"    [+] Binary saved to: {binary_path} ({len(http_payload) if http_payload else 'unknown'} bytes)")

    # --- 2. Unpack with pyinstxtractor-ng ---
    print("\n[*] Step 2: Unpacking with pyinstxtractor-ng ...")
    subprocess.run(
        ["pyinstxtractor-ng", binary_path],
        check=True, capture_output=True
    )
    print("    [+] Unpacked successfully")

    # --- 3. Reassemble exfil TCP streams (separate by 4-tuple) ---
    print("\n[*] Step 3: Reassembling exfil TCP streams ...")
    print(f"    [*] Looking for streams to {EXFIL_HOST}:{EXFIL_PORT}")

    # Group packets by (src_ip, src_port, dst_ip, dst_port)
    streams = {}
    for pkt in pkts:
        if TCP in pkt and IP in pkt and Raw in pkt:
            src, dst = pkt[IP].src, pkt[IP].dst
            sport, dport = pkt[TCP].sport, pkt[TCP].dport
            if dst == EXFIL_HOST and dport == EXFIL_PORT:
                key = (src, sport, dst, dport)
                if key not in streams:
                    streams[key] = []
                streams[key].append((pkt[TCP].seq, pkt[Raw].load))

    if not streams:
        print("    [!] No streams to exfil host, trying any stream to port 4444 ...")
        for pkt in pkts:
            if TCP in pkt and IP in pkt and Raw in pkt and pkt[TCP].dport == EXFIL_PORT:
                key = (pkt[IP].src, pkt[TCP].sport, pkt[IP].dst, pkt[TCP].dport)
                if key not in streams:
                    streams[key] = []
                streams[key].append((pkt[TCP].seq, pkt[Raw].load))

    if not streams:
        print("[-] No exfil stream found")
        sys.exit(1)

    print(f"    [+] Found {len(streams)} stream(s):")
    for i, (key, pkts_in_stream) in enumerate(streams.items()):
        total_len = sum(len(p) for _, p in pkts_in_stream)
        print(f"        Stream {i}: {key[0]}:{key[1]} -> {key[2]}:{key[3]}  "
              f"({len(pkts_in_stream)} packets, {total_len} bytes)")

    # Reassemble each stream by seq offset
    exfil_candidates = []
    for i, (key, stream_pkts) in enumerate(streams.items()):
        # Sort by seq number
        stream_pkts.sort(key=lambda x: x[0])
        min_seq = stream_pkts[0][0]

        # Offset-based reassembly (handles retransmissions)
        buffer = bytearray()
        for seq, payload in stream_pkts:
            offset = seq - min_seq
            # Extend buffer if needed
            if offset + len(payload) > len(buffer):
                buffer.extend(b'\x00' * (offset + len(payload) - len(buffer)))
            buffer[offset:offset+len(payload)] = payload

        data = bytes(buffer)
        exfil_candidates.append(data)

        print(f"\n    [*] Stream {i} reassembled ({len(data)} bytes):")
        hexdump(data)

    # --- 4. Find the stream with "flag.jackpot" and decrypt ---
    print("\n[*] Step 4: Decrypting flag ...")
    print(f"    [*] AES Key: {KEY.hex()} ({len(KEY)} bytes)")
    print(f"    [*] AES IV:  {IV.hex()} ({len(IV)} bytes)")
    print(f"    [*] Mode:    AES-128-CBC")

    flag_found = False
    for i, data in enumerate(exfil_candidates):
        if b'flag.jackpot' not in data:
            continue

        print(f"\n    [+] Found 'flag.jackpot' in stream {i}")

        if b'\n' in data:
            header, enc = data.split(b'\n', 1)
        else:
            header, enc = b"", data

        print(f"    [+] Filename header: {header.decode(errors='replace')}")
        print(f"    [+] Ciphertext length: {len(enc)} bytes")
        print(f"    [+] Ciphertext mod 16: {len(enc) % 16}")
        print(f"    [+] Ciphertext hex:")
        hexdump(enc, prefix="        ")

        if len(enc) % 16 != 0:
            print(f"    [-] Ciphertext length {len(enc)} is NOT a multiple of 16. Skipping.")
            continue

        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        decrypted = cipher.decrypt(enc)
        print(f"    [+] Decrypted (before unpad): {len(decrypted)} bytes")
        hexdump(decrypted, prefix="        ")

        try:
            flag = unpad(decrypted, 16).decode()
        except ValueError:
            print("    [-] PKCS7 unpadding failed, trying raw decode ...")
            flag = decrypted.decode(errors='replace')

        print(f"\n{'='*50}")
        print(f"FLAG: {flag}")
        print(f"{'='*50}")
        flag_found = True
        break

    if not flag_found:
        print("\n[-] No valid flag found in any stream.")
        print("    [!] Try verifying with tshark:")
        print(f"        tshark -r {pcap_file} -q -z follow,tcp,raw,4")
        sys.exit(1)


if __name__ == "__main__":
    main()   
