#!/usr/bin/env python3
import string

# Target string, CHANGE ME
target = "NoWaYIcanF0rGetThis123"

# Open a file to write the results
with open("wordlist.txt", "w") as f:
    # Loop through all printable characters and prepend them to the target string
    for char in string.printable:
        result = char + target
        f.write(result + "\n")

print("Wordlist generated and written to wordlist.txt")
