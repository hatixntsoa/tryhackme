import argparse
from pathlib import Path


def add_arguments() -> argparse.Namespace:
    """
    Adds command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments containing the ASCII file path.
    """
    parser = argparse.ArgumentParser(description="Decode ASCII-encoded data into plain text.")
    parser.add_argument(
        "-f", "--file",
        type=Path,
        required=True,
        help="Path to the ASCII-encoded file to be decoded."
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


def decode_ascii(encoded_data: str) -> str:
    """
    Decodes a series of ASCII-encoded values (separated by spaces) into plain-text.

    Args:
        encoded_data (str): A string of ASCII values separated by spaces.

    Returns:
        str: Decoded plain-text string.
    """
    try:
        # Split the input string into individual ASCII values
        ascii_values = encoded_data.split()
        
        # Convert each ASCII value to its corresponding character and join them into a string
        decoded_message = ''.join(chr(int(value)) for value in ascii_values)
        return decoded_message
    except Exception as e:
        raise ValueError(f"Error decoding ASCII data: {e}")


def main() -> None:
    args = add_arguments()
    data_path = args.file

    encoded_data = read_data(data_path)
    print(f"Encoded Data: {encoded_data}")

    try:
        decoded_data = decode_ascii(encoded_data)
        print(f"The Decoded data is: {decoded_data}")
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()
