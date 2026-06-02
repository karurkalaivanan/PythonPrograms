from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from binascii import hexlify
import socket
import binascii
import random

received_byte = '3bcb2f5ffe29fce837ac16d7dce2e83f505fb72ff4f0b94999125e3073c2fbafbf82ca7fc09653453293fe'
tempiv = 0;

def generate_challenge(authentication, size):
    r = random.Random()  # Initialize a random number generator
    length = size  # Set the length of the challenge to the specified size

    result = bytearray()  # Create a byte array to store the challenge

    # Populate the byte array with random byte values
    for _ in range(length):
        result.append(r.randint(0, 121))  # Random byte value between 0 and 121 (inclusive)

    return result  # Return the generated challenge byte array

def mid(string, start, length):
    return string[start-1:start-1+length]

def encrypt_aes_gcm(key, iv, plaintext):
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, plaintext, None)
    return ciphertext, aesgcm

def tcp_client():
    # Server address and port
    server_address = ('2401:4900:402c:F591::2', 4001)

    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    try:
        # Connect to the server
        client_socket.connect(server_address)
        print(f"Connected to {server_address}")
        print("PC AARQ")
        message = "00 01 00 10 00 01 00 1F 60 1D A1 09 06 07 60 85 74 05 08 01 01 BE 10 04 0E 01 00 00 00 06 5F 1F 04 00 00 1E 5D FF FF"
        byte_data = bytes.fromhex(message)
        print(f"Sent: {message}")
        for byte in byte_data:
            client_socket.sendall(byte.to_bytes(1, byteorder='big'))
        data = client_socket.recv(1024)
        print("Response")
        print(' '.join([f'{byte:02x}' for byte in data]))
        
        print("PC INVOCATION")
        message = "00 01 00 10 00 01 00 0D C0 01 C1 00 01 00 00 2B 01 03 FF 02 00"
        byte_data = bytes.fromhex(message)
        print(f"Sent: {message}")
        for byte in byte_data:
            client_socket.sendall(byte.to_bytes(1, byteorder='big'))
        data = client_socket.recv(1024)
        print("Response")
        print(' '.join([f'{byte:02x}' for byte in data]))
        # 00 01 00 01 00 10 00 09 C4 01 C1 00 06 00 00 00 A8
        if(data[12] == 0x06): 
            # Step 1: Extract the last four bytes
            last_four_bytes = data[-4:]                 
            # Step 2: Convert the bytes to an integer
            integer_value = int.from_bytes(last_four_bytes, byteorder='big')
            # Step 3: Add 1 to the integer value
            integer_value += 1
            # Optionally, convert the result back to bytes or hexadecimal representation if needed
            new_last_four_bytes = integer_value.to_bytes(4, byteorder='big')
            new_hex_representation = new_last_four_bytes.hex()
            new_formatted_hex = ' '.join(new_hex_representation[i:i+2] for i in range(0, len(new_hex_representation), 2))
            print("New value (integer):", integer_value)
            print("New last four bytes in hexadecimal:", new_formatted_hex)
        
        print("Disconnect")
        message = "00 01 00 10 00 01 00 05 62 03 80 01 00"
        byte_data = bytes.fromhex(message)
        print(f"Sent: {message}")
        for byte in byte_data:
            client_socket.sendall(byte.to_bytes(1, byteorder='big'))
        data = client_socket.recv(1024)
        print("Response")
        print(' '.join([f'{byte:02x}' for byte in data]))
        
        print("US AARQ")
        encription_text = "01 00 00 00 06 5f 1f 04 00 00 1e 5d ff ff"
        authentication_key = 'bbbbbbbbbbbbbbbb' 
        system_title = 'qwertyui'
        iv_counter = new_hex_representation
        key_hex = ''.join([hex(byte)[2:].zfill(2) for byte in authentication_key.encode()])
        key = bytes.fromhex(key_hex)
        iv_hex = ''.join([hex(byte)[2:].zfill(2) for byte in system_title.encode()]) + iv_counter
        iv = bytes.fromhex(iv_hex)
        plaintext = bytes.fromhex(encription_text)

        ciphertext, aesgcm = encrypt_aes_gcm(key, iv, plaintext)

        print("Plaintext:", hexlify(plaintext).decode().upper())
        print("Encrypted Data (hex):", hexlify(ciphertext).decode().upper())
        first_14_bytes = ciphertext[:14]
        # Convert the first 26 bytes to their hexadecimal representation
        hex_representation = binascii.hexlify(first_14_bytes).decode()
        # Insert space after every two characters
        formatted_hex = ' '.join(hex_representation[i:i+2] for i in range(0, len(hex_representation), 2))
        print("Formatted hexadecimal representation of the first 26 bytes:", formatted_hex)

        ########################################################################################
        
        # Generate a challenge of size 16 for HighECDSA authentication
        challenge = generate_challenge(1, 16)

        secure_password = ' '.join([f'{byte:02X}' for byte in challenge])
        # Print the challenge bytes with space between each byte
        print(secure_password)
        
        ######################################################################################
        
        message = "00 01 00 30 00 01 00 5F 60 5D A1 09 06 07 60 85 74 05 08 01 03 A6 0A 04 08 71 77 65 72 74 79 75 69 8A 02 07 80 8B 07 60 85 74 05 08 02 02 AC 12 80 10 " + secure_password + " BE 23 04 21 21 1F 30 " + new_formatted_hex + " " + formatted_hex + " 87 07 8E BF 0D 41 B0 94 D9 10 7E C8"
        # message = "00 01 00 30 00 01 00 5F 60 5D A1 09 06 07 60 85 74 05 08 01 03 A6 0A 04 08 71 77 65 72 74 79 75 69 8A 02 07 80 8B 07 60 85 74 05 08 02 02 AC 12 80 10 48 3A 56 15 30 6D 60 4B 08 4A 74 08 16 79 3A 1B BE 23 04 21 21 1F 30 00 00 00 F6 75 74 B7 CC FA 24 FC C1 FA 50 C5 43 99 53 B7 3B AD DA 6C 58 7F 2D F6 C1 08 D3"
        byte_data = bytes.fromhex(message)
        print(f"Sent: {message}")
        for byte in byte_data:
            client_socket.sendall(byte.to_bytes(1, byteorder='big'))
        data = client_socket.recv(1024)
        print("Response")
        print(' '.join([f'{byte:02x}' for byte in data]))
        
    finally:
        # Clean up the connection
        client_socket.close()
        print("Connection closed")

if __name__ == "__main__":
    tcp_client()



