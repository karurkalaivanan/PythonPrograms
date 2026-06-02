import os
import re
import struct

# ==============================
# Step 1: Read File (same folder as python file)
# ==============================
path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(path, "input.txt")

with open(file_path, "r") as f:
    raw_data = f.read()

# ==============================
# Step 2: Extract HDLC Frame
# ==============================
match = re.search(r'7e.*?7e', raw_data, re.IGNORECASE)

if not match:
    print("No HDLC frame found")
    exit()

hex_frame = match.group()
hex_clean = hex_frame.replace(" ", "")
frame = bytes.fromhex(hex_clean)

print("HDLC Frame Length:", len(frame))

# ==============================
# Step 3: Parse Profile Generic
# ==============================

def parse_profile_generic(frame):

    print("\n---- PROFILE GENERIC MIDNIGHT DATA ----")

    if frame[0] != 0x7E or frame[-1] != 0x7E:
        print("Invalid HDLC Frame")
        return

    # Find LLC Header
    apdu_start = frame.find(b'\xE6\xE7\x00')
    if apdu_start == -1:
        print("No LLC header found")
        return

    # Remove HDLC + LLC + FCS
    apdu = frame[apdu_start + 3:-3]

    index = 0

    # Skip GET response header (C4 01 C1 00)
    index += 4

    # Skip structure header (01 01 02 XX)
    index += 4

    # -------------------
    # Timestamp
    # -------------------
    if apdu[index] == 0x09:
        index += 2  # Skip 09 0C

        year = int.from_bytes(apdu[index:index+2], 'big')
        month = apdu[index+2]
        day = apdu[index+3]
        hour = apdu[index+4]
        minute = apdu[index+5]
        second = apdu[index+6]

        print(f"Timestamp: {year}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}")

        index += 12

    # -------------------
    # Float32 Values
    # -------------------
    values = []

    while index < len(apdu):
        if apdu[index] == 0x17:  # Float32
            value = struct.unpack('>f', apdu[index+1:index+5])[0]
            values.append(value)
            index += 5
        else:
            index += 1

    print("\nCaptured Billing Values:")
    for i, v in enumerate(values):
        print(f"Value {i+1}: {v}")


parse_profile_generic(frame)