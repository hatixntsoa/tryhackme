import argparse
from pathlib import Path
import base64
import re


class SecretDecoder:
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def read_data(self) -> str:
        """
        Reads data from the specified file.

        Returns:
            str: Content of the file.
        """
        try:
            with open(self.file_path, 'r') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error while reading file: {e}")
            exit(1)  # Exit on failure

    def detect_encoding(self, encoded_data: str):
        """
        Detects whether the encoded string is Base32, Base64, Hex, Caesar cipher, Morse code, ASCII, or Base64 URL-safe.

        Args:
            encoded_data (str): The encoded string.

        Returns:
            tuple: A tuple containing the detected encoding type and the decoded string.
        """
        encoded_data = encoded_data.strip()

        # Try Base32
        try:
            decoded_base32 = base64.b32decode(encoded_data).decode('utf-8')
            print("The string is Base32 encoded.")
            return "Base32", decoded_base32
        except Exception:
            pass

        # Try Base64
        try:
            decoded_base64 = base64.b64decode(encoded_data).decode('utf-8')
            print("The string is Base64 encoded.")
            return "Base64", decoded_base64
        except Exception:
            pass

        # Try Base64 URL-safe (Base64 encoding but using - and _ instead of + and /)
        try:
            decoded_base64_urlsafe = base64.urlsafe_b64decode(encoded_data).decode('utf-8')
            print("The string is Base64 URL-safe encoded.")
            return "Base64 URL-safe", decoded_base64_urlsafe
        except Exception:
            pass

        # Try Hex decoding
        if re.match(r'^[0-9a-fA-F\s]+$', encoded_data):  # Check if hex-like (spaces between hex digits)
            try:
                decoded_hex = bytes.fromhex(encoded_data.replace(" ", "")).decode('utf-8')
                print("The string is Hex encoded.")
                return "Hex", decoded_hex
            except ValueError:
                pass

        # Try Morse code
        if re.match(r'^[.\- /\n]+$', encoded_data):  # Check if Morse code-like
            decoded_morse = self.decode_morse(encoded_data)
            print("The string is Morse code encoded.")
            return "Morse Code", decoded_morse

        # Try ASCII codes
        if re.match(r'^(\d+\s)*\d+$', encoded_data):  # Check if ASCII codes-like
            decoded_ascii = self.decode_ascii(encoded_data)
            print("The string is ASCII code encoded.")
            return "ASCII", decoded_ascii

        # Try Caesar cipher (ROT13 detection)
        if self.is_rot13_possible(encoded_data):  # Check if it looks like ROT13
            decoded_rot13 = self.decode_rot13(encoded_data)
            print("The string seems to be Caesar cipher encoded (ROT13).")
            return "Caesar Cipher (ROT13)", decoded_rot13

        # If none of the above, raise an error
        raise ValueError("The string is neither valid Base32, Base64, Base64 URL-safe, Hex, Morse code, ASCII, nor Caesar cipher.")

    def is_rot13_possible(self, text: str) -> bool:
        """
        Checks if the text is likely to be ROT13 encoded.

        Args:
            text (str): The encoded string.

        Returns:
            bool: True if the text is likely ROT13, else False.
        """
        # A simple heuristic is to check if the string contains alphabetic characters
        # (with or without spaces) and if it's a reasonable length.
        return bool(re.match(r'^[A-Za-z\s!?.,:;]*$', text))

    def decode_rot13(self, text: str) -> str:
        """
        Decodes a string encoded with the ROT13 cipher (Caesar cipher with a shift of 13).

        Args:
            text (str): The encoded string.

        Returns:
            str: Decoded string.
        """
        # Python doesn't have a built-in ROT13 encoding/decoding method in the standard library.
        # We can use the `codecs` module for a simpler approach to decode ROT13.
        import codecs
        return codecs.decode(text, 'rot_13')

    def decode_morse(self, morse_code: str) -> str:
        """
        Decodes a Morse code string into plain text.

        Args:
            morse_code (str): The encoded Morse code string.

        Returns:
            str: Decoded plain text string.
        """
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

    def decode_ascii(self, ascii_codes: str) -> str:
        """
        Decodes a space-separated ASCII code string into plain text.

        Args:
            ascii_codes (str): The ASCII codes string.

        Returns:
            str: Decoded plain text string.
        """
        ascii_values = ascii_codes.split()
        decoded_message = ''.join([chr(int(code)) for code in ascii_values])
        return decoded_message

    def decode(self) -> None:
        """
        Main decoding function that reads the file, detects encoding,
        and decodes the content.
        """
        encoded_data = self.read_data()

        try:
            encoding_type, decoded_data = self.detect_encoding(encoded_data)
            print(f"Encoding Type: {encoding_type}")
            print(f"The Decoded data is: {decoded_data}")
        except ValueError as e:
            print(e)


def add_arguments() -> argparse.Namespace:
    """
    Adds command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments containing the file path.
    """
    parser = argparse.ArgumentParser(
        description="Decode any secret by detecting its encoding type first and then decoding."
    )
    parser.add_argument(
        "-f", "--file",
        type=Path,
        required=True,
        help="Path to the encoded file to be decoded."
    )
    return parser.parse_args()


def main() -> None:
    args = add_arguments()
    decoder = SecretDecoder(args.file)
    decoder.decode()


if __name__ == "__main__":
    main()
