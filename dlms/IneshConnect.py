# 2401:4900:402c:F593::2,4059
import socket
import time

server_address = ('2401:4900:402c:F593::2', 4059)

client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

def relay_connect():
    try:
        # Connect to the server
        client_socket.connect(server_address)
        print(f"Connected to {server_address}")
        print("Relay Connect")
        # Send the CONNECT string
        connect_string = "*CONNE# / HTTP/1.1\r\n\r\n"
        client_socket.sendall(connect_string.encode())
        # Receive and print response
        response = client_socket.recv(1024)
        print(response.decode())
        
    finally:
        # Clean up the connection
        client_socket.close()
        print("Connection closed")
        
def relay_disconnect():
    try:
        # Connect to the server
        client_socket.connect(server_address)  
        print(f"Connected to {server_address}")
        print("Relay Disconnect")
        # Send the CONNECT string
        connect_string = "*DCONN# / HTTP/1.1\r\n\r\n"
        client_socket.sendall(connect_string.encode())

        # Receive and print response
        response = client_socket.recv(1024)
        print(response.decode())
        
    finally:
        # Clean up the connection
        client_socket.close()
        print("Connection closed")
        

# relay_disconnect()

relay_connect()