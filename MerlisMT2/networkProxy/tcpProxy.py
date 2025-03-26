import socket
import threading

# Configuration
LOCAL_HOST = '127.0.0.1'
LOCAL_PORT = 12102  # Port where the game will connect
REMOTE_HOST = '5.135.208.208'  # Replace with actual game server IP
REMOTE_PORT = 12102  # Replace with actual game server port
BUFFER_SIZE = 4096

def handle_client(client_socket, remote_host, remote_port):
    # Connect to the remote server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((remote_host, remote_port))

    # Handle data exchange between client and server
    while True:
        try:
            # Receive data from the game client
            client_data = client_socket.recv(BUFFER_SIZE)
            if not client_data:
                break
            
            # Optional: Inspect or modify the client data here
            print(f"[Client -> Server] {client_data}")

            # Forward the data to the game server
            server_socket.sendall(client_data)

            # Receive data from the game server
            server_data = server_socket.recv(BUFFER_SIZE)
            if not server_data:
                break

            # Optional: Inspect or modify the server data here
            print(f"[Server -> Client] {server_data}")

            # Send the data back to the game client
            client_socket.sendall(server_data)

        except Exception as e:
            print(f"Connection error: {e}")
            break

    client_socket.close()
    server_socket.close()

def start_proxy(local_host, local_port, remote_host, remote_port):
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind((local_host, local_port))
    proxy_socket.listen(5)
    print(f"[*] Proxy listening on {local_host}:{local_port}")

    while True:
        client_socket, addr = proxy_socket.accept()
        print(f"[+] Accepted connection from {addr}")
        # Start a new thread to handle the client connection
        client_thread = threading.Thread(
            target=handle_client,
            args=(client_socket, remote_host, remote_port)
        )
        client_thread.start()

if __name__ == "__main__":
    start_proxy(LOCAL_HOST, LOCAL_PORT, REMOTE_HOST, REMOTE_PORT)
