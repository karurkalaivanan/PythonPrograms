import socket

def tcp_client():
    # Server address and port
    server_address = ('2401:4900:84bd:6398::2', 4001)

    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server
        client_socket.connect(server_address)
        print(f"Connected to {server_address}")

        # Send data to the server
        message = "00 01 00 10 00 01 00 1F 60 1D A1 09 06 07 60 85 74 05 08 01 01 BE 10 04 0E 01 00 00 00 06 5F 1F 04 00 00 1E 5D FF FF"
        client_socket.sendall(message.encode('utf-8'))
        print(f"Sent: {message}")

        # Receive data from the server
        data = client_socket.recv(1024)
        print(f"Received: {data.decode('utf-8')}")

    finally:
        # Clean up the connection
        client_socket.close()
        print("Connection closed")

if __name__ == "__main__":
    tcp_client()