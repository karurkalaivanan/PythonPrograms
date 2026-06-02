
import serial
import time

AARQ_LNT = "7EA04C0341106B04E6E600603EA109060760857405080101A60A040852454E30303030308A0207808B0760857405080201AC0680046C6E7431BE10040E01000000065F1F040040B81FFFFFFB267E"
AARQ_SECURE = "7EA044034110B3E1E6E6006036A1090607608574050801018A0207808B0760857405080201AC0A80084142434430303031BE10040E01000000065F1F0400621E5DFFFF50C77E"
# Serial port settings
SEND_AARQ = AARQ_SECURE
PORT = 'COM14'  # Adjust this if needed
BAUDRATE = 9600
TIMEOUT = 0.5  # Seconds

device_id = 108
high_byte = (device_id >> 8) & 0xFF
low_byte = device_id & 0xFF
device_hex = f"{high_byte:02X} {low_byte:02X}"
# print(device_hex)

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

input_hex = "A0 1C 03 41 32 6D D3 E6 E6 00 C1 01 C1 00 17 00 00 16 00 00 FF 09 00 12 " + device_hex
frame = build_dlms_frame(input_hex)
# print("Final DLMS Frame:", frame)

# //////////////////////////////////////////////////////////////////////

# DLMS frame commands
commands = {
    "Sending SNRM": "7EA0070341935A647E",
    "COSEM_Open_Request": SEND_AARQ,
    "GETRequestNormal": frame,
    "Sending DISC": "7EA00703415356A27E"
}

def hex_str_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

try:
    with serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT) as ser:
        ser.flushInput()

        for label, hex_command in commands.items():
            print(f"\n--- {label} ---")
            print(f"Sending: {hex_command}")

            # Send the command
            ser.write(hex_str_to_bytes(hex_command))
            time.sleep(0.5)

            # Read response
            response = b''
            start_time = time.time()
            while time.time() - start_time < TIMEOUT:
                if ser.in_waiting:
                    response += ser.read(ser.in_waiting)
                else:
                    time.sleep(0.1)

            # Print the received bytes
            if response:
                print(f"Received: {response.hex().upper()}")

                # Extra: handle GETRequestNormal response
                if label == "GETRequestNormal" and len(response) >= 18:
                    if response[14] == 0:
                        print("Write Successfull")
                    else:
                        print("Write UnSuccessfull")
            else:
                print("No response")

except serial.SerialException as e:
    print(f"Serial error: {e}")
