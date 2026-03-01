import base64
import codecs


# Step 1: Base64 -> Morse Code
def base64_to_morse(base64_data: str) -> str:
    # Add padding to ensure correct Base64 decoding
    padding_needed = len(base64_data) % 4
    if padding_needed:
        base64_data += '=' * (4 - padding_needed)
    
    decoded_bytes = base64.b64decode(base64_data)  # Decode the base64
    decoded_string = decoded_bytes.decode('utf-8')  # Convert bytes to string
    
    # Morse Code Dictionary for English Letters and Numbers
    morse_code_dict = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
        'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
        'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
        '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.'
    }

    # Convert each character in the string to Morse code
    morse_code = ' '.join(morse_code_dict.get(char.upper(), '') for char in decoded_string)
    return morse_code


# Step 2: Morse Code -> Binary
def morse_to_binary(morse_code: str) -> str:
    binary_str = ''
    for char in morse_code:
        if char == '.':
            binary_str += '0'
        elif char == '-':
            binary_str += '1'
        # Adding space for word separation
        elif char == ' ':
            binary_str += ' '  # Maintain spaces between words
    return binary_str


# Step 3: Binary -> ROT47 (Custom ROT47 Logic)
def binary_to_rot47(binary_str: str) -> str:
    # Remove spaces from binary string before converting to ASCII
    binary_str = binary_str.replace(" ", "")  # Remove all spaces

    # Convert binary string to ASCII characters
    ascii_str = ''
    for i in range(0, len(binary_str), 8):
        byte = binary_str[i:i + 8]
        if len(byte) == 8:
            ascii_str += chr(int(byte, 2))

    # Apply custom ROT47 logic
    decoded_message = []
    for char in ascii_str:
        # Check if the character is within the printable ASCII range (33-126)
        if 33 <= ord(char) <= 126:
            decoded_char = chr(33 + ((ord(char) - 33 + 47) % 94))  # Apply the ROT47 shift
            decoded_message.append(decoded_char)
        else:
            decoded_message.append(char)  # Non-printable characters remain unchanged

    return ''.join(decoded_message)


# Step 4: ROT47 -> Decimal
def rot47_to_decimal(rot47_str: str) -> str:
    decimal_values = ' '.join(str(ord(c)) for c in rot47_str)
    return decimal_values


# Main function to process the transformations
def main():
    # Base64 data (can be replaced with file reading logic)
    base64_data = "LS0tLS0gLi0tLS0gLi0tLS0gLS0tLS0gLS0tLS0gLi0tLS0gLi0tLS0gLS0tLS0KLS0tLS0gLi0tLS0gLi0tLS0gLS0tLS0gLS0tLS0gLi0tLS0gLS0tLS0gLi0tLS0KLS0tLS0gLS0tLS0gLi0tLS0gLS0tLS0gLS0tLS"

    # Base64 -> Morse Code
    morse_code = base64_to_morse(base64_data)
    print("Morse Code: ", morse_code)

    # Morse Code -> Binary
    binary_code = morse_to_binary(morse_code)
    print("Binary Code: ", binary_code)

    # Binary -> ROT47 (Custom Logic)
    rot47_code = binary_to_rot47(binary_code)
    print("Rot47 Encoded: ", rot47_code)

    # ROT47 -> Decimal
    decimal_code = rot47_to_decimal(rot47_code)
    print("Decimal Values: ", decimal_code)


if __name__ == "__main__":
    main()
