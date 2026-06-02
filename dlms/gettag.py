import math

_authenticationKey = bytearray([0x62] * 16)
_H = bytearray()

def shift_right(array):
    carry = 0
    for i in range(len(array) - 1, -1, -1):
        temp = array[i] & 1
        array[i] >>= 1
        array[i] |= carry << 7
        carry = temp
        
def multiply_h(y, h):
    tmp = bytearray(16)
    z = bytearray(16)
    tmp[:len(h)] = h

    for i in range(16):
        for j in range(8):
            if y[i] & (1 << (7 - j)) != 0:
                xor(z, tmp)
            if tmp[15] & 0x01 != 0:
                shift_right(tmp)
                tmp[0] ^= 0xe1
            else:
                shift_right(tmp)

    y[:len(z)] = z
 
def xor(block, value):
    for pos in range(16):
        block[pos] ^= value[pos]
            
def get_ghash(value):
    Y = bytearray(16)

    for pos in range(0, len(value), 16):
        X = bytearray(16)
        cnt = min(len(value) - pos, 16)
        X[:cnt] = value[pos:pos+cnt]
        xor(Y, X)
        multiply_h(Y, _H)
    print(Y)
    return Y
  
def get_tag(tag, plain_text, ciphered_data):
    zero = bytearray(16)
    bb = bytearray()

    # Length of the crypted data.
    len_c = 8 * len(ciphered_data) if ciphered_data is not None else 0
    # Length of the authenticated data.
    len_a = (1 + len(_authenticationKey)) * 8
    if ciphered_data is None:
        # If data is not ciphered.
        len_a += 8 * len(plain_text)
    v = int(128 * math.ceil(len_a / 128) - len_a)
    u = int(128 * math.ceil(len_c / 128) - len_c)
    
    bb.append(tag)
    bb.extend(_authenticationKey)
    
    if ciphered_data is None:
        bb.extend(plain_text)
    # Fill with zeroes.
    bb.extend(zero[:v // 8])
    # Write Ciphered data.
    if ciphered_data is not None:
        bb.extend(ciphered_data)
        # Fill with zeroes.
        bb.extend(zero[:u // 8])
    # Write length of the authenticated data in bits.
    bb.extend(len_a.to_bytes(8, 'big'))
    # Write length of the crypted data.
    bb.extend(len_c.to_bytes(8, 'big'))
    
    # tmp = bytearray([0x30, 0x62, 0x62, 0x62, 0x62, 0x62, 0x62, 0x62, 0x62, 0x62, 0x62, 0x62, 0x62, 0x62, 0x62, 0x62,
    # 0x62, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    # 0x34, 0x69, 0x6E, 0x7E, 0x1F, 0x93, 0x97, 0x5A, 0x7D, 0x5E, 0xC2, 0x57, 0x45, 0xD1, 0x00, 0x00,
    # 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    # 0x70])
    
    getvalue = get_ghash(bb)
    
    return getvalue[:12]

text = bytearray([0x01, 0x00, 0x00, 0x00, 0x06, 0x5f, 0x1f, 0x04, 0x00, 0x62, 0x1e, 0x5d, 0xff, 0xff])
text2 = bytearray([0x34, 0x69, 0x6e, 0x7e, 0x1f, 0x93, 0x97, 0x5a, 0x7d, 0x5e, 0xc2, 0x57, 0x45, 0xd1])

tagvalue = get_tag(0x03, text, text2)
print(tagvalue)