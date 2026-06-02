import os
import re
import struct

# ==========================================================
# STEP 1 : READ FILE
# ==========================================================

path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(path, "billing2.txt")

with open(file_path, "r") as f:
    raw_data = f.read()

# ==========================================================
# STEP 2 : REBUILD MULTI BLOCK APDU
# ==========================================================

frames_text = raw_data.split("_")
full_apdu = b''

for part in frames_text:

    match = re.search(r'7e.*?7e', part, re.IGNORECASE)
    if not match:
        continue

    hex_frame = match.group().replace(" ", "")
    frame = bytes.fromhex(hex_frame)

    if frame[0] != 0x7E or frame[-1] != 0x7E:
        continue

    # Locate LLC (E6 E7 00)
    llc_index = frame.find(b'\xE6\xE7\x00')

    if llc_index != -1:
        apdu = frame[llc_index+3:-3]   # Remove LLC and FCS
    else:
        apdu = frame[9:-3]            # Continuation block

    full_apdu += apdu

print("Total APDU Length:", len(full_apdu))


# ==========================================================
# STEP 3 : REMOVE GET RESPONSE HEADER (C4 02 C1 xx)
# ==========================================================

index = 0

# Skip GET RESPONSE header
if full_apdu[0] == 0xC4:
    index += 4

# Skip block control info (8 bytes usually)
index += 8


# ==========================================================
# STEP 4 : PARSE ARRAY + STRUCTURE
# ==========================================================

if full_apdu[index] != 0x01:
    print("Not Array format")
    exit()

index += 1
array_count = full_apdu[index]
index += 1

if full_apdu[index] != 0x02:
    print("Not Structure format")
    exit()

index += 1
structure_count = full_apdu[index]
index += 1

print("Array Count:", array_count)
print("Structure Elements per Row:", structure_count)


# ==========================================================
# STEP 5 : PARSE BILLING DATA
# ==========================================================

def parse_element(data, idx):

    tag = data[idx]

    # Float32
    if tag == 0x17:
        value = struct.unpack('>f', data[idx+1:idx+5])[0]
        return value, idx + 5

    # DateTime
    elif tag == 0x09 and data[idx+1] == 0x0C:
        year = int.from_bytes(data[idx+2:idx+4], 'big')
        month = data[idx+4]
        day = data[idx+5]
        hour = data[idx+6]
        minute = data[idx+7]
        second = data[idx+8]

        dt = f"{year}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}"
        return dt, idx + 14

    # Unsigned 32
    elif tag == 0x06:
        value = int.from_bytes(data[idx+1:idx+5], 'big')
        return value, idx + 5

    # Unsigned 16
    elif tag == 0x12:
        value = int.from_bytes(data[idx+1:idx+3], 'big')
        return value, idx + 3

    # Signed 16
    elif tag == 0x10:
        value = struct.unpack('>h', data[idx+1:idx+3])[0]
        return value, idx + 3

    # Default skip
    else:
        return None, idx + 1


print("\n========== BILLING DATA ==========\n")

for row in range(array_count):

    print(f"\n------ Billing Row {row+1} ------")

    for element in range(structure_count):

        value, index = parse_element(full_apdu, index)

        if value is not None:
            print(f"{element+1:03}: {value}")