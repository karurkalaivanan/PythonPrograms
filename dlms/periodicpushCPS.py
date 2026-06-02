from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from binascii import hexlify
authentication_key = 'bbbbbbbbbbbbbbbb' 
########################################################
def mid(string, start, length):
    return string[start-1:start-1+length]
    
received_byte = '0001000100400081db08435053353533393676300000000280a66ae3600d345259427a7fec120cae2206b0cee9d0b58a33100fbafc7955e926cbc2c3ccf9ff1a2e750e196c0cd0638e51a707a8a4d59016b08f82f65d06e89850cb74169cfc869e6e5e0f6200f33ee9f3b4d6bdcb397095acc6b9b13a2807d328275a93b3c8ab2e62a26762a7549eeb'
# Example usage:
start_index = 49
substring_length = len(received_byte)
result = mid(received_byte, start_index, substring_length)
system_title = mid(received_byte, (10*2+1), 16)
print(system_title )
iv_counter = mid(received_byte, (20*2+1), 8)
print(iv_counter)
######################################################

def encrypt_aes_gcm(key, iv, plaintext):
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, plaintext, None)
    return ciphertext, aesgcm

system_title = '4142433132333435'
iv_counter = "00000001"
key_hex = ''.join([hex(byte)[2:].zfill(2) for byte in authentication_key.encode()])
key = bytes.fromhex(key_hex)
iv_hex = system_title + iv_counter
iv = bytes.fromhex(iv_hex)
plaintext = bytes.fromhex(result)

ciphertext, aesgcm = encrypt_aes_gcm(key, iv, plaintext)

print("Plaintext:", hexlify(plaintext).decode())
print("Encrypted Data (hex):", hexlify(ciphertext).decode())

if(ciphertext[0] != 0x0f):
    print("Wrong packet received")

length = 2
substring_length1 = len(hexlify(ciphertext).decode())
received1 = mid(hexlify(ciphertext).decode(), length + 1, substring_length1)
print("packet received")
print(received1)       

length = length + 6 # Dummy code  
substring_length1 = len(hexlify(ciphertext).decode())
received1 = mid(hexlify(ciphertext).decode(), length + 1, substring_length1)
print("packet received")
print(received1)
     
array_size = mid(hexlify(ciphertext).decode(), length + 1, 2)  
received1 = mid(hexlify(ciphertext).decode(), length + 1, substring_length1)
print("array_size ")
print(array_size)

length = length + 2 # array size

para_length = mid(hexlify(ciphertext).decode(), length + 1, 2) 
length = length + 2 # array size
received1 = mid(hexlify(ciphertext).decode(), length + 1, substring_length1)
print("para_length ")
print(para_length) 

print("packet received ")
print(received1) 
 
para_length = mid(hexlify(ciphertext).decode(), length + 1, (int(para_length,16)* 2)) 

final_frame = mid(hexlify(ciphertext).decode(), length + 1, (int(para_length,16)* 2))
print("Date and Time ")
print(para_length)
# start_index1 = 41
# substring_length1 = len(hexlify(ciphertext).decode())
# message = mid(hexlify(ciphertext).decode(), start_index1, substring_length1)
# print(message)



# if(message[1] == 'a' or message[1] == '9'): 
#     start_index1 = 5
#     substring_length1 = 24
#     message1 = mid(message, start_index1, substring_length1)
#     print(message1)
#     ascii_string = bytes.fromhex(message1).decode('utf-8')
#     print(f"Device ID : {ascii_string}")

   
# Get the authentication tag
#tag = aesgcm.decrypt(iv, ciphertext, None)
#print("Auth Tag (hex):", hexlify(tag).decode())s