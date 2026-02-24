# Function to decode numbers from a single line in a file
def decode_numbers_from_file(file_path):
    # Read the single line of numbers from the file
    with open(file_path, 'r') as file:
        # Read the line, split by spaces, and convert to integers
        numbers = [int(num) for num in file.readline().split()]
    
    # Decode the numbers
    decoded_chars = []
    for num in numbers:
        if 32 <= num <= 126:  # Valid ASCII range for printable characters
            decoded_chars.append(chr(num))
        else:
            decoded_chars.append(f"({num})")  # Place non-printable characters in parentheses
    
    # Join the characters to form the decoded message
    decoded_message = ''.join(decoded_chars)
    
    return decoded_message

# File path to the ASCII values file
file_path = 'secret_ascii_data'

# Decode the numbers and print the result
decoded_message = decode_numbers_from_file(file_path)
print(decoded_message)
