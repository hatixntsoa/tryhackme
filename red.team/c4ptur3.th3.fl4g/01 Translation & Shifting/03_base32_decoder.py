import argparse
from pathlib import Path
import base64


def add_arguments() -> argparse.Namespace:
    """
    Adds command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments containing the file path.
    """
    parser = argparse.ArgumentParser(description="Decode Base32 from a file into plain text.")
    parser.add_argument(
        "-f", "--file",
        type=Path,
        required=True,
        help="Path to the Base32-encoded file to be decoded."
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


def decode_base32(encoded_data: str) -> str:
    """
    Decodes a Base32-encoded string into its plain-text equivalent.

    Args:
        encoded_data (str): Base32-encoded string.

    Returns:
        str: Decoded string.
    """
    # Clean input to remove invalid characters
    encoded_data = encoded_data.replace("\n", "").replace(" ", "").strip()
 
    try:
        # Decode the Base32 string
        decoded_bytes = base64.b32decode(encoded_data)
        return decoded_bytes.decode('utf-8')  # Convert to string assuming UTF-8
    except Exception as e:
        raise ValueError(f"Error decoding Base32 data: {e}")


def main() -> None:
    args = add_arguments()
    data_path = args.file

    encoded_data = read_data(data_path)
    print(encoded_data)

    try:
        decoded_data = decode_base32(encoded_data)
        print(f"The Decoded data is: {decoded_data}")
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()
