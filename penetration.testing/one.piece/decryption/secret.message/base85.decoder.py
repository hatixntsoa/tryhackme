#!/usr/bin/env python3

import argparse
import base64
import sys

def decode_base85_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            encoded_data = f.read()
        decoded_data = base64.b85decode(encoded_data)
        print(decoded_data.decode('utf-8', errors='replace'))
    except FileNotFoundError:
        print(f"[!] File not found: {file_path}", file=sys.stderr)
    except Exception as e:
        print(f"[!] Error decoding file: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Decode Base85-encoded file content")
    parser.add_argument('-f', '--file', required=True, help="Path to the Base85-encoded file")
    args = parser.parse_args()

    decode_base85_file(args.file)

if __name__ == "__main__":
    main()
