import os
import re
import struct
import subprocess
from pathlib import Path

from scapy.all import rdpcap, TCP

PCAP_FILE = "security-footage-1648933966395.pcap"
BOUNDARY = b"--BoundaryString"
FRAME_DIR = Path("frames")
FRAME_DIR.mkdir(exist_ok=True)

def extract_tcp_payloads(pcap_path):
    packets = rdpcap(pcap_path)
    tcp_data = bytearray()

    for pkt in packets:
        if TCP in pkt:
            tcp_payload = bytes(pkt[TCP].payload)
            if tcp_payload:
                tcp_data.extend(tcp_payload)
    return tcp_data

def extract_mjpeg_frames(buffer, boundary=BOUNDARY):
    frame_count = 0
    offset = 0

    while True:
        start = buffer.find(boundary, offset)
        if start == -1:
            break
        end = buffer.find(boundary, start + len(boundary))
        if end == -1:
            break

        part = buffer[start:end]
        match = re.search(b"Content-Length:\s*(\d+)", part, re.IGNORECASE)
        if not match:
            offset = end
            continue

        content_length = int(match.group(1))
        header_end = part.find(b"\r\n\r\n")
        if header_end == -1:
            offset = end
            continue

        jpeg_start = start + header_end + 4
        jpeg_end = jpeg_start + content_length
        jpeg_data = buffer[jpeg_start:jpeg_end]

        filename = FRAME_DIR / f"frame_{frame_count:04d}.jpg"
        with open(filename, "wb") as f:
            f.write(jpeg_data)
        print(f"Saved frame {frame_count}")
        frame_count += 1
        offset = end

    return frame_count

def create_video_from_frames(fps=10, output="output_video.mp4"):
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(FRAME_DIR / "frame_%04d.jpg"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FFmpeg error:\n{result.stderr}")
    else:
        print(f"Video created successfully: {output}")

def main():
    print("Reading PCAP and extracting TCP data...")
    tcp_data = extract_tcp_payloads(PCAP_FILE)

    print("Extracting MJPEG frames...")
    frame_count = extract_mjpeg_frames(tcp_data)
    print(f"Extraction complete: {frame_count} frames saved.")

    print("Creating video from frames...")
    create_video_from_frames()

if __name__ == "__main__":
    main()
