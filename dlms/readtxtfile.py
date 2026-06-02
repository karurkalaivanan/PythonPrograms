import threading
import time
import socket
import struct
import asyncio
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from binascii import hexlify
from pathlib import Path

file_path = Path('MeterList.csv')
#file_path = "MeterList.csv"  # Change this to the path of your file

# Number of threads
num_threads = 2
# Create an array to hold thread instances
threads = []

def mid(string, start, length):
    return string[start-1:start-1+length]

def start_ipv6(addressipv6):
  TCP_IP = addressipv6
  TCP_PORT = 4001      
  BUFFER_SIZE = 1024
  MESSAGE = "000100100001001F601DA109060760857405080101BE10040E01000000065F1F0400001E5DFFFF"
  byte_data = bytes.fromhex(MESSAGE)
  s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
  s.connect((TCP_IP, TCP_PORT))
  print(f"Connected to {TCP_IP, TCP_PORT}")
  print("Sending AARQ request")
  for byte in byte_data:
      s.sendall(byte.to_bytes(1, byteorder='big'))
  data = s.recv(BUFFER_SIZE)

  MESSAGE = "000100100001000DC001C100010000600100FF0200"
  byte_data = bytes.fromhex(MESSAGE)
  print("Reading Serial Number")
  for byte in byte_data:
      s.sendall(byte.to_bytes(1, byteorder='big'))
  data1 = s.recv(BUFFER_SIZE)

  MESSAGE = "00010010000100056203800100"
  byte_data = bytes.fromhex(MESSAGE)
  print("Dicsonnecting")
  for byte in byte_data:
      s.sendall(byte.to_bytes(1, byteorder='big'))
  data = s.recv(BUFFER_SIZE)
  s.close()
  start_index1 = 15
  substring_length1 = 9
  message1 = mid(data1, start_index1, substring_length1)
  print("Meter Serial Number")
  print(message1)
  print("Client Closed")


# Open the file in read mode
with open(file_path, 'r') as file:
    # Read all lines into a list
    lines = file.readlines()

# Process the list of lines
for line in lines:
    csv_data = line.strip().split(',')
    #print(line.strip())
    print("IP")
    print(csv_data[0])
    print("MeterNo")
    print(csv_data[1])
    start_ipv6('2401:4900:84bd:66BB::2')
    #for i in range(num_threads):
    #  thread = threading.Thread(target=start_ipv6, args=(csv_data[0]))
    #  threads.append(thread)
    #thread = threading.Thread(target=start_ipv6, args=(csv_data[0]))
    # Start all threads
    #for thread in threads:
    #thread.start()

    # Wait for all threads to finish
    #for thread in threads:
    #thread.join()

    
print("All threads have finished.")