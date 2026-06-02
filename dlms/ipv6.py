import socket
import struct
import asyncio
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from binascii import hexlify

def mid(string, start, length):
    return string[start-1:start-1+length]

async def delayed_task():
    print("Start of the task")
    await asyncio.sleep(1)  # Introduce a delay of 2 seconds
    print("End of the task")
    
def readipaddress(addressipv6):    
    TCP_IP = '2401:4900:84BD:64F3::2' 
    TCP_PORT = 4059      
    BUFFER_SIZE = 1024
    MESSAGE = "00010020000100486046A109060760857405080103A60A04085A454E30353038308A0207808B0760857405080201AC07800568656C6C6FBE17041521132000000001B48888F3E9ABF822CE47652210CA"
    MESSAGE = "00010020000100546052A109060760857405080103A60A04085A454E30353038308A0207808B0760857405080201AC07800568656C6C6FBE230421211F30000000005812BBB083220FBDF18772ED25F7679E3684E4304D6B34AB756E"
    byte_data = bytes.fromhex(MESSAGE)
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    print(f"Connected to {TCP_IP, TCP_PORT}")
    print("Sending AARQ request")
    for byte in byte_data:
        s.sendall(byte.to_bytes(1, byteorder='big'))
    data = s.recv(BUFFER_SIZE)
    print(data)
    # MESSAGE = "000100100001000DC001C100010000600100FF0200"
    # byte_data = bytes.fromhex(MESSAGE)
    # print("Reading Serial Number")
    # for byte in byte_data:
    #     s.sendall(byte.to_bytes(1, byteorder='big'))
    # data1 = s.recv(BUFFER_SIZE)

    # MESSAGE = "00010010000100056203800100"
    # byte_data = bytes.fromhex(MESSAGE)
    # print("Dicsonnecting")
    # for byte in byte_data:
    #     s.sendall(byte.to_bytes(1, byteorder='big'))
    # data = s.recv(BUFFER_SIZE)
    
    # start_index1 = 15
    # substring_length1 = 9
    # message1 = mid(data1, start_index1, substring_length1)
    # print("Meter Serial Number")
    # print(message1)
    s.close()
    print("Client Closed")
    
readipaddress('2401:4900:84bd:6ad9::2')
