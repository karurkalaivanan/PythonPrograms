from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from binascii import hexlify

######################################################################
def mid(string, start, length):
    return string[start-1:start-1+length]
    
received_byte = '0001000100400067db0843505335353339365c30000000002930a3b1e475401145469ad16caa4f52452d351da1ba28cffa829df465b2402ff9ca6b42695634fa00e525a55886a0e21c5d6c57367b9246043aaa5ce514ef6bd3350eb4182f9c2197980c044d3f9f0c57c1717be97049'
# Example usage:
start_index = 49
substring_length = len(received_byte)

result = mid(received_byte, start_index, substring_length)

######################################################################

def encrypt_aes_gcm(key, iv, plaintext):
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, plaintext, None)
    return ciphertext, aesgcm

authentication_key = 'bbbbbbbbbbbbbbbb' 
system_title = 'CPS55396'
iv_counter = '00000000'
key_hex = ''.join([hex(byte)[2:].zfill(2) for byte in authentication_key.encode()])
key = bytes.fromhex(key_hex)
iv_hex = ''.join([hex(byte)[2:].zfill(2) for byte in system_title.encode()]) + iv_counter
iv = bytes.fromhex(iv_hex)
plaintext = bytes.fromhex(result)

ciphertext, aesgcm = encrypt_aes_gcm(key, iv, plaintext)

print("Plaintext:", hexlify(plaintext).decode())
print("Encrypted Data (hex):", hexlify(ciphertext).decode())

if(ciphertext[0] != 0x0f):
    print("Wrong packet received")
       
start_index1 = 41
substring_length1 = len(hexlify(ciphertext).decode())
message = mid(hexlify(ciphertext).decode(), start_index1, substring_length1)
print(message)

if(message[1] == 'a' or message[1] == '9'): 
    start_index1 = 5
    substring_length1 = 24
    message1 = mid(message, start_index1, substring_length1)
    print(message1)
    ascii_string = bytes.fromhex(message1).decode('utf-8')
    print(f"Device ID : {ascii_string}")

   
# Get the authentication tag
#tag = aesgcm.decrypt(iv, ciphertext, None)
#print("Auth Tag (hex):", hexlify(tag).decode())













