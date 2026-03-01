import argparse
from pathlib import Path


def add_arguments() -> argparse.Namespace:
    """
    Adds command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments containing the file path.
    """
    parser = argparse.ArgumentParser(description="Decode Binary from a file into ASCII.")
    parser.add_argument(
        "-f", "--file",
        type=Path,
        required=True,
        help="Path to the encoded file to be decoded."
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


def decode_binary(binaries: str) -> str:
    """
    Decodes Binary character into ASCII.

    Args:
        binaries (str): Binary encoded string.

    Returns:
        str: Decoded string.
    """
    # Remove spaces from the binary input
    binaries = binaries.replace(" ", "")

    if not binaries:
        return "No data to decode."

    if not all(c in '01' for c in binaries):
        raise ValueError("Input data contains invalid binary characters.")

    # Split the binary string into groups of 8 bits
    binary_groups = [binaries[i:i+8] for i in range(0, len(binaries), 8)]
    ascii_characters = []
    for binary in binary_groups:
        decimal = int(binary, 2)
        if 0 <= decimal <= 127:  # Ensure within ASCII range
            ascii_characters.append(chr(decimal))
        else:
            raise ValueError(f"Binary value {binary} is out of ASCII range.")

    return ''.join(ascii_characters)


def main() -> None:
    args = add_arguments()
    data_path = args.file

    encoded_data = read_data(data_path)

    try:
        decoded_data = decode_binary(encoded_data)
        print(f"The Decoded data is: {decoded_data}")
    except ValueError as e:
        print(f"Error decoding binary data: {e}")


if __name__ == "__main__":
    main()
