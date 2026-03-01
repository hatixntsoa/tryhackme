import argparse
from pathlib import Path


def add_arguments() -> argparse.Namespace:
    """
    Adds command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments containing the file path.
    """
    parser = argparse.ArgumentParser(description="Encode ASCII into Binary and save it to a file.")
    parser.add_argument(
        "-f", "--file",
        type=Path,
        required=True,
        help="Path to the file containing the text to be encoded."
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


def encode_to_binary(text: str) -> str:
    """
    Encodes ASCII characters into Binary.

    Args:
        text (str): ASCII string to encode.

    Returns:
        str: Binary encoded string.
    """
    if not text:
        return "No data to encode."

    binary_representation = []
    for char in text:
        # Convert each character to its binary equivalent, padded to 8 bits
        binary_representation.append(f"{ord(char):08b}")
    
    # Join the binary representations with spaces for readability
    return ' '.join(binary_representation)


def main() -> None:
    args = add_arguments()
    data_path = args.file

    text_data = read_data(data_path)

    try:
        binary_data = encode_to_binary(text_data)
        print(f"The Encoded data is: {binary_data}")
    except ValueError as e:
        print(f"Error encoding text data: {e}")


if __name__ == "__main__":
    main()
