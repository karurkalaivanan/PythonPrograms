from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from binascii import hexlify

########################################################
def mid(string, start, length):
    return string[start-1:start-1+length]
    
received_byte = '29 2B 84 6A 32 81 7C'

byte_array = bytes.fromhex(received_byte.replace(' ', ''))

# Find the length of the byte array
length = len(byte_array)

######################################################

def encrypt_aes_gcm(key, iv, plaintext):
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, plaintext, None)
    return ciphertext, aesgcm

# authentication_key = '0123456789ABCDEF' 
# authentication_key = 'bbbbbbbbbbbbbbbb' 
authentication_key = 'NSI_Globalkey_EA'
# system_title = 'ISE00001'
# system_title = 'ZEN05080'
system_title = 'NSI00000'
# system_title = 'CPS00003'
iv_counter = '00 00 00 06'
key_hex = ''.join([hex(byte)[2:].zfill(2) for byte in authentication_key.encode()])
key = bytes.fromhex(key_hex)
iv_hex = ''.join([hex(byte)[2:].zfill(2) for byte in system_title.encode()]) + iv_counter
iv = bytes.fromhex(iv_hex)
plaintext = bytes.fromhex(received_byte)

ciphertext, aesgcm = encrypt_aes_gcm(key, iv, plaintext)

print("Plaintext:", hexlify(plaintext).decode())
print("Encrypted Data (hex):", hexlify(ciphertext).decode())
# num_bytes = length
# selected_bytes = hexlify[:num_bytes]
# print("Encrypted Data (hex):", hexlify(ciphertext).decode())
# if(ciphertext[0] != 0x0f):
#     print("Wrong packet received")
       
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
#print("Auth Tag (hex):", hexlify(tag).decode())













