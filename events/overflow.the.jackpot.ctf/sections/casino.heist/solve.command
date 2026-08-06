Script started on 2026-09-26 23:59:10+03:00 [COMMAND="python3 solve.py stolen_jackpot.pcapng" TERM="xterm-256color" TTY="/dev/pts/2" COLUMNS="119" LINES="29"]
[*] Reading stolen_jackpot.pcapng ...
[*] 701 packets loaded

[*] Step 1: Extracting binary from HTTP stream ...
    [+] Binary saved to: extracted_binary (20561767 bytes)

[*] Step 2: Unpacking with pyinstxtractor-ng ...
    [+] Unpacked successfully

[*] Step 3: Reassembling exfil TCP streams ...
    [*] Looking for streams to 172.20.0.3:4444
    [+] Found 2 stream(s):
        Stream 0: 172.20.0.1:49496 -> 172.20.0.3:4444  (1 packets, 61 bytes)
        Stream 1: 172.20.0.1:49500 -> 172.20.0.3:4444  (1 packets, 29 bytes)

    [*] Stream 0 reassembled (61 bytes):
    0000  66 6c 61 67 2e 6a 61 63 6b 70 6f 74 0a 9b cc 34   |flag.jackpot...4|
    0010  1f 83 74 f7 d0 31 a5 a0 ee 46 63 50 13 13 b1 54   |..t..1...FcP...T|
    0020  66 b1 84 e3 3a 3f 29 5e fd 0c d1 b4 f5 c6 4b 48   |f...:?)^......KH|
    0030  dd 83 1b bc a7 ec 44 23 e3 78 2f 8f e5            |......D#.x/..|

    [*] Stream 1 reassembled (29 bytes):
    0000  66 6c 61 67 2e 6a 61 63 6b 70 6f 74 0a e2 4e d3   |flag.jackpot..N.|
    0010  e2 b8 99 1e 1c 81 e6 71 47 f1 f8 60 f4            |.......qG..`.|

[*] Step 4: Decrypting flag ...
    [*] AES Key: 4a34636b7030744834636b33724b6579 (16 bytes)
    [*] AES IV:  49765f466f725f457866316c74723821 (16 bytes)
    [*] Mode:    AES-128-CBC

    [+] Found 'flag.jackpot' in stream 0
    [+] Filename header: flag.jackpot
    [+] Ciphertext length: 48 bytes
    [+] Ciphertext mod 16: 0
    [+] Ciphertext hex:
        0000  9b cc 34 1f 83 74 f7 d0 31 a5 a0 ee 46 63 50 13   |..4..t..1...FcP.|
        0010  13 b1 54 66 b1 84 e3 3a 3f 29 5e fd 0c d1 b4 f5   |..Tf...:?)^.....|
        0020  c6 4b 48 dd 83 1b bc a7 ec 44 23 e3 78 2f 8f e5   |.KH......D#.x/..|
    [+] Decrypted (before unpad): 48 bytes
        0000  54 48 4d 7b 4a 40 63 6b 50 30 35 5f 52 30 62 62   |THM{J@ckP05_R0bb|
        0010  33 72 79 5f 56 49 41 5f 70 59 74 68 30 6e 4e 7d   |3ry_VIA_pYth0nN}|
        0020  10 10 10 10 10 10 10 10 10 10 10 10 10 10 10 10   |................|

==================================================
FLAG: THM{J@ckP05_R0bb3ry_VIA_pYth0nN}
==================================================

Script done on 2026-09-26 23:59:13+03:00 [COMMAND_EXIT_CODE="0"]
