# Define the binary string
b = '100010101100001011100110111010001100101011100100010000000110001001101110011101000100000010101000100100001001101011110110110101000110101010111110110101000110101010111110110101100110011011100000101111101100100001100110110001100110000011001000011001101111101'

# Convert binary to decimal
d = int(b, 2)
print(d)  # Print the decimal representation

# Convert decimal to hexadecimal
h = hex(d)[2:]
print(h)  # Print the hexadecimal representation

# Convert hexadecimal to ASCII
ascii_text = bytes.fromhex(h).decode('ASCII')

# Print the ASCII representation
print(ascii_text)
