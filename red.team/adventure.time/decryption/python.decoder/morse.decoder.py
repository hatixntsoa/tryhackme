import argparse
from pathlib import Path


def add_arguments() -> argparse.Namespace:
    """
    Adds command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments containing the file path.
    """
    parser = argparse.ArgumentParser(description="Decode Morse from a file into ASCII.")
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


# Morse code decoding function
def decode_morse(morse_code: str) -> str:
    """
    Decodes Morse code into ASCII text.

    Args:
        morse_code (str): Morse code string.

    Returns:
        str: Decoded text.
    """
    morse_dict = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G', '....': 'H',
        '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P',
        '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
        '-.--': 'Y', '--..': 'Z', '-----': '0', '.----': '1', '..---': '2', '...--': '3', '....-': '4',
        '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9',
        '.-.-.-': '.', '--..--': ',', '..--..': '?', '.----.': "'", '-.-.--': '!', '-.-.-.': ';', '-...-': '=',
        '.-..-.': '"', '.-.-.': '+', '-....-': '-', '..--.-': '_', '.-.-..': ':', '-.-.-': '.', '.-..-': '/',
        '-..-.': '&', '-.--.': '(', '-.--.-': ')', '.--.-.': '@', '---...': ':', '-.-.-.': ';', '.--.-.': '@',
        '.----.': "'", '-..--..': '~', '...-..-': '$'
    }

    # Replace underscore '_' with dash '-'
    morse_code = morse_code.replace('_', '-')  # Treat underscore as dash

    # Replace backslash with a space to indicate space between words
    morse_code = morse_code.replace('\\', ' ')  # Treat backslash as space between words

    # Split the input into words based on the backslash acting as a space
    words = morse_code.split(' ')  # Split words by space (backslash replaced by space)
    decoded_message = []

    for word in words:
        # Split each word by the slash delimiter (to get Morse letters)
        letters = word.split('/')  # Split letters by '/'
        
        decoded_word = []
        for letter in letters:
            if letter in morse_dict:
                decoded_word.append(morse_dict[letter])
            else:
                decoded_word.append('?')  # If the letter is not in the dict, append '?'
                print(f"Invalid Morse code: {letter}")  # Print invalid morse symbols

        decoded_message.append(''.join(decoded_word))

    return ' '.join(decoded_message)


def main() -> None:
    args = add_arguments()
    data_path = args.file

    encoded_data = read_data(data_path)

    decoded_data = decode_morse(encoded_data)
    print(f"The Decoded Morse data is: {decoded_data}")


if __name__ == "__main__":
    main()
