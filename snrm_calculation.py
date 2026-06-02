def reflect_bits(data, bits=8):
    """Reflect the bit order of a byte or word."""
    reflection = 0
    for i in range(bits):
        if data & (1 << i):
            reflection |= 1 << (bits - 1 - i)
    return reflection

def crc16_ibm_sdlc(data):
    """
    Calculate CRC-16/IBM-SDLC (used in DLMS HDLC frames).
    Polynomial: 0x1021, Init: 0xFFFF, RefIn: True, RefOut: True, XorOut: 0xFFFF
    """
    crc = 0xFFFF
    for byte in data:
        byte = reflect_bits(byte, 8)
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    crc = reflect_bits(crc, 16) ^ 0xFFFF
    return crc

def build_dlms_frame(input_hex):
    """
    Build a DLMS HDLC frame:
    - Compute CRC16/IBM-SDLC
    - Swap CRC bytes (low byte first)
    - Add 0x7E start and end flags
    """
    data = [int(x, 16) for x in input_hex.split()]
    crc = crc16_ibm_sdlc(data)

    # Swap high/low bytes
    low = crc & 0xFF
    high = (crc >> 8) & 0xFF

    full_frame = [0x7E] + data + [low, high] + [0x7E]
    return " ".join(f"{b:02X}" for b in full_frame)

# Example
# input_hex = "A0 0A 00 02 00 CB 21 93"
input_hex = "A0 1C 03 41 32 6D D3 E6 E6 00 C1 01 C1 00 17 00 00 16 00 00 FF 09 00 12 27 0E"
frame = build_dlms_frame(input_hex)
print("Final DLMS Frame:", frame)
