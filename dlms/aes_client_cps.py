from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from binascii import hexlify

received_byte = '01 00 00 00 06 5f 1f 04 00 62 1e 5d ff ff'
# received_byte = '43 a7 b1 b5 18 26 96 fe fe 4b 6c 65 78 74 d7 40'
def encrypt_aes_gcm(key, iv, plaintext):
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, plaintext, None)
    return ciphertext, aesgcm

authentication_key = 'bbbbbbbbbbbbbbbb' 
# authentication_key = 'wwwwwwwwwwwwwwww'
system_title = 'qwertyui'
iv_counter = '00000137'
key_hex = ''.join([hex(byte)[2:].zfill(2) for byte in authentication_key.encode()])
key = bytes.fromhex(key_hex)
iv_hex = ''.join([hex(byte)[2:].zfill(2) for byte in system_title.encode()]) + iv_counter
iv = bytes.fromhex(iv_hex)
plaintext = bytes.fromhex(received_byte)


ciphertext, aesgcm = encrypt_aes_gcm(key, iv, plaintext)

print("Plaintext:", hexlify(plaintext).decode())
print("Encrypted Data (hex):", hexlify(ciphertext).decode())

# Get the authentication tag
tag = aesgcm.decrypt(iv, ciphertext, None)
print("Auth Tag (hex):", hexlify(tag).decode())





