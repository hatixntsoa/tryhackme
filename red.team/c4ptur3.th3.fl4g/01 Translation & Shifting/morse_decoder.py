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


def decode_rot13(morse_code: str) -> str:
    """
    Decodes a Morse code string into plain text.

    Args:
        morse_code (str): The encoded Morse code string.

    Returns:
        str: Decoded plain text string.
    """
 
    try:
        morse_dict = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G',
            '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N',
            '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T', '..-': 'U',
            '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z', '-----': '0', '.----': '1',
            '..---': '2', '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
            '---..': '8', '----.': '9', '/': ' '  # Slash is used for word separation
        }
        
        words = morse_code.strip().split('   ')  # Morse code words are separated by 3 spaces
        decoded_message = []

        for word in words:
            letters = word.split()  # Morse code letters are separated by a space
            decoded_word = ''.join([morse_dict.get(letter, '') for letter in letters])
            decoded_message.append(decoded_word)

        return ' '.join(decoded_message)
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
