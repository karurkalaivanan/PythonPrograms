import serial
import binascii
import time

# === CONFIGURATION ===
PORT = "COM3"       # Change this to your serial port
BAUD = 9600         # Common for DLMS meters
TIMEOUT = 2

# === DLMS/COSEM Frames ===
SNRM = bytes.fromhex("7EA00A000200CB21937BBE7E")
AARQ = bytes.fromhex("7EA03A000200CB2110A2DEE6E6006029A109060760857405080101A60A040852454E3030303030BE10040E01000000065F1F040040B81FFFFFAC587E")
GET_SERIAL = bytes.fromhex("7EA01C000200CB2132FCE7E6E600C001C100010000600100FF020089A07E")
DISC = bytes.fromhex("7EA00A000200CB215377787E")

SNRM2 = bytes.fromhex("7EA00A000200CD2193A2687E")
AARQ2 = bytes.fromhex("7EA03A000200CD21107B08E6E6006029A109060760857405080101A60A040852454E3030303030BE10040E01000000065F1F040040B81FFFFFAC587E") 
GET_SERIAL2 = bytes.fromhex("7EA01C000200CD21322531E6E600C001C100010000600100FF020089A07E")
DISC2 = bytes.fromhex("7EA00A000200CD2153AEAE7E")
# === SERIAL SETUP ===
ser = serial.Serial(PORT, BAUD, bytesize=8, parity='N', stopbits=1, timeout=TIMEOUT)

def print_bytes(prefix, data):
    """Pretty print byte data in uppercase hex format"""
    hex_str = " ".join([f"{b:02X}" for b in data])
    print(f"{prefix} ({len(data)} bytes): {hex_str}")

def send_and_receive(frame, description=""):
    """Send a DLMS frame and return received data"""
    print(f"\n>>> Sending {description}")
    print_bytes("TX", frame)
    ser.write(frame)
    ser.flush()
    time.sleep(0.4)

    response = ser.read(256)
    if response:
        print_bytes("RX", response)
    else:
        print("RX: No response.")
    return response

def extract_serial_number(rx_bytes):
    """Extract serial number (ASCII) from GetResponseNormal frame"""
    try:
        data_hex = binascii.hexlify(rx_bytes).decode().upper()
        idx = data_hex.find("090C")
        if idx != -1:
            serial_hex = data_hex[idx + 4 : idx + 4 + (12 * 2)]  # 12 bytes
            serial_ascii = bytes.fromhex(serial_hex).decode("ascii").strip()
            return serial_ascii
    except Exception as e:
        print("Error decoding serial number:", e)
    return None

# === MAIN ===
print("Opening serial port...")
time.sleep(1)

send_and_receive(SNRM, "SNRM (COSEM_Open_Request)")
send_and_receive(AARQ, "AARQ (Application Association Request)")
response = send_and_receive(GET_SERIAL, "GET Request (Meter Serial Number)")

serial_num = extract_serial_number(response)
if serial_num:
    print(f"\n✅ Meter Serial Number 1: {serial_num}")
else:
    print("\n❌ Could not find serial number in Meter 1.")

send_and_receive(DISC, "DISC (Disconnect)")
#Read Meter 2
send_and_receive(SNRM2, "SNRM (COSEM_Open_Request)")
send_and_receive(AARQ2, "AARQ (Application Association Request)")
response = send_and_receive(GET_SERIAL2, "GET Request (Meter Serial Number)")

serial_num = extract_serial_number(response)
if serial_num:
    print(f"\n✅ Meter Serial Number 2: {serial_num}")
else:
    print("\n❌ Could not find serial number in Meter 2.")

send_and_receive(DISC2, "DISC (Disconnect)")

ser.close()
print("\nConnection closed.")
