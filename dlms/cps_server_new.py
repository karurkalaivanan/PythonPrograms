from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from binascii import hexlify
from datetime import datetime
import socket
import select

# Server address and port
server_address = ('2401:4900:84bd:6e9d::2', 4001)
# server_address = ('2401:4900:84bd:6e21::2', 4001)
# Create a TCP/IP socket
client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
authentication_key = 'bbbbbbbbbbbbbbbb' 
system_title = 'CPS00003'
iv_counter = '0000001F'
server_title = ""

key_hex = ''.join([hex(byte)[2:].zfill(2) for byte in authentication_key.encode()])
key = bytes.fromhex(key_hex)
iv_hex = ''.join([hex(byte)[2:].zfill(2) for byte in system_title.encode()]) + iv_counter
iv = bytes.fromhex(iv_hex)

def encrypt_aes_gcm(key, iv, plaintext):
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, plaintext, None)
    return ciphertext, aesgcm
  
plaintext = bytes.fromhex("C2 B7 52 36 B2 9A 1B 31 E7 97 27 5D 21 8E B3 68 D2 5A AF DB FA FC 24 D8 12 5F")


ciphertext, aesgcm = encrypt_aes_gcm(key, iv, plaintext)

print("Plaintext:", hexlify(plaintext).decode())
print("Encrypted Data (hex):", hexlify(ciphertext).decode())

# Get the authentication tag
tag = aesgcm.decrypt(iv, ciphertext, None)
print("Auth Tag (hex):", hexlify(tag).decode())
##############################################################################################
def print_time():
  # Get the current time
  current_time = datetime.now()
  # Print the current time with seconds in two digits
  print("Current time:", current_time.strftime("%Y-%m-%d %H:%M:%S"))

def connect_tcp_server():
  try:     
    # Connect to the server
    client_socket.connect(server_address)
    print(f"Connected to {server_address}")
  except ValueError:
    print("Connection closed")
        

def disconnect_tcp_server():
  client_socket.close()
  print("Connection closed")
 
def send_aarq():
  message = "00 01 00 20 00 01 00 49 60 47 A1 09 06 07 60 85 74 05 08 01 03 A6 0A 04 08 71 77 65 72 74 79 75 69 8A 02 07 80 8B 07 60 85 74 05 08 02 01 AC 08 80 06 31 32 33 34 35 36 BE 17 04 15 21 13 20 00 00 00 00 92 E1 A1 A2 6E FF 58 2F 0D 13 D3 00 C7 7B"
  byte_data = bytes.fromhex(message)
  print(f"Sent: {message}")
  for byte in byte_data:
      client_socket.sendall(byte.to_bytes(1, byteorder='big'))
  data = client_socket.recv(1024)
  print(f"Received: {data}")
  if(data[22] == 0x03 and data[23] == 0x02 and data[24] == 0x01 and data[25] == 0x00):
    server_title = chr(data[37]) + chr(data[38]) + chr(data[39]) + chr(data[40]) + chr(data[41]) + chr(data[42]) + chr(data[43]) + chr(data[44]) 
    print(server_title)
    print("Authentication PASSED")
  else:
    print("Authentication FAILED")
    # print(f"Received: {data[22]},{data[23]},{data[24]},{data[25]}")
    # print(f"Received: {data[29]},{data[30]},{data[31]},{data[32]}")

def send_instant_data():
  message = "00 01 00 20 00 01 00 05 62 03 80 01 00"
  byte_data = bytes.fromhex(message)
  print(f"Sent: {message}")
  for byte in byte_data:
      client_socket.sendall(byte.to_bytes(1, byteorder='big'))
  data = client_socket.recv(1024)
  print(f"Received: {data}")
  
def send_disconnect():
  message = "00 01 00 20 00 01 00 05 62 03 80 01 00"
  byte_data = bytes.fromhex(message)
  print(f"Sent: {message}")
  for byte in byte_data:
      client_socket.sendall(byte.to_bytes(1, byteorder='big'))
  data = client_socket.recv(1024)
  print(f"Received: {data}")
 






# connect_tcp_server()
# send_aarq()
# send_instant_data()
# send_disconnect()
# disconnect_tcp_server()


