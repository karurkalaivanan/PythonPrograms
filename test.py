def encode_hdlc_address_2bytes(address):
    lower_7 = (address & 0x7F) << 1 | 0x01  # Last byte (LSB = 1)
    upper_7 = ((address >> 7) & 0x7F) << 1  # More bytes (LSB = 0)
    return [upper_7, lower_7]

addr = 9999
encoded = encode_hdlc_address_2bytes(addr)

# Print as hex with spaces
hex_string = ' '.join(f'{b:02X}' for b in encoded)
print(f"{hex_string}")
