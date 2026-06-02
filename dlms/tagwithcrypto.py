def get_ghash(value, h):
    # Y = bytearray(b'\x00' * 16)
    Y = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    for pos in range(0, len(value), 16):
        X = value[pos:pos+16]
        X += bytearray(b'\x00' * (16 - len(X)))  # Pad X with zeroes if necessary
        xor_bytes(Y, X)
        multiply_h(Y, h)
    return bytes(Y)

def xor_bytes(a, b):
    for i in range(len(a)):
        a[i] ^= b[i]

def shift_right(block):
    for i in range(len(block) - 1, 0, -1):
        block[i] >>= 1
        if block[i - 1] & 1:
            block[i] |= 0x80
    block[0] >>= 1

def multiply_h(y, h):
    tmp = bytearray(h)
    z = bytearray([0] * 16)
    # Loop every byte.
    for i in range(16):
        # Loop every bit.
        for j in range(8):
            if y[i] & (1 << (7 - j)) != 0:
                xor_bytes(z, tmp)
            # If last bit.
            if tmp[15] & 0x01 != 0:
                shift_right(tmp)
                tmp[0] ^= 0xe1
            else:
                shift_right(tmp)
    y[:] = z

# Example usage:
# value = b'\x01\x23\x45\x67\x89\xAB\xCD\xEF\x00\x11\x22\x33\x44\x55\x66\x77'
value_hex = (
    "30 62 62 62 62 62 62 62 62 62 62 62 62 62 62 62 "
    "62 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
    "f9 fb d1 35 77 c6 96 25 9d c9 cb 7d df b5 00 00 "
    "00 00 00 00 00 00 00 88 00 00 00 00 00 00 00 70"
)

# Convert the string of hexadecimal values into bytes
value = bytes.fromhex(value_hex.replace(' ', ''))

# h = b'\xAA' * 16  # Example value for _H

h_hex = (
    "6f 7a eb 9d 52 90 35 03 9d 01 "
    "77 5e 7f 6d f1 88"
)

# Convert the string of hexadecimal values into bytes
h = bytes.fromhex(h_hex.replace(' ', ''))

ghash = get_ghash(value, h)
print(ghash.hex())
