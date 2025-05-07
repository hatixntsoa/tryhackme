#!/usr/bin/env python3

import argparse


def hex_to_ascii(hex_str):
    hex_str = hex_str.strip().lower().replace("0x", "")

    # Convert to bytes
    try:
        byte_data = bytes.fromhex(hex_str)
        # Reverse for little endian
        little_endian_bytes = byte_data[::-1]
        return little_endian_bytes.decode('ascii')
    except ValueError as e:
        return f"Error: {e}"


def main():
    parser = argparse.ArgumentParser(
        description="Convert hex to ASCII from file.")
    parser.add_argument('-f', '--file', required=True,
                        help='Path to file containing hex string')
    args = parser.parse_args()

    try:
        with open(args.file, 'r') as f:
            hex_data = f.read().strip()
        ascii_output = hex_to_ascii(hex_data)
        print(f"ASCII Output: {ascii_output}")
    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
