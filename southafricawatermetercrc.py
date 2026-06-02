def crc16_modbus(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF

data = bytes.fromhex("FEFEFE6820AAAAAAAAAAAAAA190B25110041542B4353510D0A")  # replace with exact covered bytes
crc = crc16_modbus(data)
print(f"{crc:04X}")                 # numeric CRC
print(f"{crc & 0xFF:02X}{crc>>8:02X}")  # little-endian bytes