import argparse
from pathlib import Path
import codecs


def add_arguments() -> argparse.Namespace:
    """
    Adds command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments containing the file path.
    """
    parser = argparse.ArgumentParser(description="Decode Rot13 from a file into plain text.")
    parser.add_argument(
        "-f", "--file",
        type=Path,
        required=True,
        help="Path to the Rot13-encoded file to be decoded."
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


def decode_rot13(encoded_data: str) -> str:
    """
    Decodes a Rot13-encoded string into its plain-text equivalent.

    Args:
        encoded_data (str): Rot13-encoded string.

    Returns:
        str: Decoded string.
    """
 
    try:
        # Python doesn't have a built-in ROT13 encoding/decoding method in the standard library.
        # We can use the `codecs` module for a simpler approach to decode ROT13.
        return codecs.decode(encoded_data, 'rot_13')
    except Exception as e:
        raise ValueError(f"Error decoding Rot13 data: {e}")


def main() -> None:
    args = add_arguments()
    data_path = args.file

    encoded_data = read_data(data_path)
    print(encoded_data)

    try:
        decoded_data = decode_rot13(encoded_data)
        print(f"The Decoded data is: {decoded_data}")
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()
