#!/usr/bin/env python3

"""
The encoding used here is HTML character references,
where each character is represented as
&#<decimal-code>;
based on its ASCII or Unicode value.

To decode it using Python,
you can use the html.unescape
function from the html module.
"""

import html
from pathlib import Path
import argparse


def add_arguments() -> argparse.Namespace:
    """
    Adds command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments containing the file path.
    """
    parser = argparse.ArgumentParser(description="Decode HTML character references from a file.")
    parser.add_argument(
        "-f", "--file",
        type=str,
        required=True,
        help="Path to the encoded file to be decoded."
    )
    return parser.parse_args()


def read_data(file_path: str) -> str:
    """
    Reads data from the specified file.

    Args:
        file_path (str): Path to the file to read.

    Returns:
        str: Content of the file.
    """
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error while reading file: {e}")
        return ""


def decode_data(encoded_data: str) -> str:
    """
    Decodes HTML character references in a string.

    Args:
        encoded_data (str): HTML encoded string.

    Returns:
        str: Decoded string.
    """
    try:
        return html.unescape(encoded_data)
    except Exception as e:
        print(f"Error while decoding: {e}")
        return ""

def main() -> None:
    args = add_arguments()
    data_path = Path(args.file)

    encoded_data = read_data(data_path)

    if encoded_data:
        decoded_data = decode_data(encoded_data)
        print(f"The Decoded data is : {decoded_data}")
    else:
        print("No encoded data to decode.")


if __name__ == "__main__":
    main()
