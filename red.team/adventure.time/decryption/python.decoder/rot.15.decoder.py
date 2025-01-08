import argparse
from pathlib import Path


def add_arguments() -> argparse.Namespace:
    """
    Adds command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments containing the file path.
    """
    parser = argparse.ArgumentParser(description="Decode Rot15 from a file into plain text.")
    parser.add_argument(
        "-f", "--file",
        type=Path,
        required=True,
        help="Path to the Rot15-encoded file to be decoded."
    )
    return parser.parse_args()


def read_data(file_path: Path) -> str:
    """
    Reads data from the specified file.

    Args:
        file_path (Path): Path to the file to read.

    Returns:
        str: Content of the file.
    """
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error while reading file: {e}")
        exit(1)  # Exit on failure


def decode_rot15(encoded_data: str) -> str:
    """
    Decodes a Rot15-encoded string into its plain-text equivalent.

    Args:
        encoded_data (str): Rot15-encoded string.

    Returns:
        str: Decoded string.
    """
    decoded_chars = []
    for char in encoded_data:
        if 'a' <= char <= 'z':
            decoded_chars.append(chr(((ord(char) - ord('a') - 15) % 26) + ord('a')))
        elif 'A' <= char <= 'Z':
            decoded_chars.append(chr(((ord(char) - ord('A') - 15) % 26) + ord('A')))
        else:
            decoded_chars.append(char)  # Non-alphabet characters remain unchanged
    return ''.join(decoded_chars)


def main() -> None:
    args = add_arguments()
    data_path = args.file

    encoded_data = read_data(data_path)
    print(encoded_data)

    try:
        decoded_data = decode_rot15(encoded_data)
        print(f"The Decoded data is: {decoded_data}")
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()
