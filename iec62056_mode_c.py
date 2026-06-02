import serial
import serial.tools.list_ports
import time
import os

# -------------------------------
# Auto-detect COM port
# -------------------------------
def auto_select_port():
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No COM ports found.")
        return None

    selected = ports[0].device
    print(f"Selected COM: {selected}")
    return selected

# -------------------------------
# Send HEX string to serial
# -------------------------------
def send_hex(ser, hex_string):
    ser.write(bytes.fromhex(hex_string.replace(" ", "")))
    print(f">> Sent HEX: {hex_string}")

# -------------------------------
# Main IEC62056 Mode C Function
# -------------------------------
def iec62056_mode_c_save():
    port = auto_select_port()
    if not port:
        return

    ser = serial.Serial(port, baudrate=300, bytesize=7,
                        parity=serial.PARITY_EVEN, stopbits=1,
                        timeout=1)

    try:
        # Step 1: Wake-up with 3A 3A twice
        send_hex(ser, "3A 3A")
        time.sleep(0.2)
        send_hex(ser, "3A 3A")

        # Wait for 0x15
        ack = ser.read()
        if ack != b'\x15':
            print("Meter NOT responding with 0x15. Received:", ack)
            return
        print("<< Received ACK 0x15")

        # Step 2: Send /?!\r\n
        ser.write(b"/?!\r\n")
        time.sleep(0.5)
        id_msg = ser.read(64)

        if not id_msg:
            print("No identification message received.")
            return

        decoded = id_msg.decode(errors="ignore")
        print("<< Identification:", decoded)

        # Extract meter serial number from 6th byte onward
        if len(decoded) < 6:
            print("Invalid identification message.")
            return
        meter_sno = decoded[5:]
        print(f"Meter Serial Number: {meter_sno}")

        # Extract baud rate (5th byte = index 4)
        baud_char = decoded[4]
        baud_map = {'0': 300, '1': 600, '2': 1200, '3': 2400, '4': 4800, '5': 9600}
        if baud_char not in baud_map:
            print("Unknown baud char:", baud_char)
            return
        new_baud = baud_map[baud_char]
        print(f"Meter baud rate: {new_baud}")

        # Step 3: Send ACK with baud
        baud_hex = baud_char.encode().hex()
        cmd = f"06 30 {baud_hex} 30 0D 0A"
        send_hex(ser, cmd)

        # Step 4: Switch to new baud
        ser.baudrate = new_baud
        print(f"Switched serial port to {new_baud} baud")
        
        # Step 5: Wait 5 seconds to receive full data
        print("Waiting 5 seconds for meter data...")
        time.sleep(5)

        data = b""
        while ser.in_waiting:
            data += ser.read(ser.in_waiting)

        if not data:
            print("No data received from meter after baud switch.")
            return

        # Save data to text file named by meter serial number
        filename = f"{meter_sno.strip()}.txt"
        with open(filename, "wb") as f:
            f.write(data)

        print(f"Data saved to file: {filename}")
        print("Raw Meter Data:")
        try:
            print(data.decode(errors="ignore"))
        except:
            print(data.hex())

    finally:
        ser.close()


if __name__ == "__main__":
    iec62056_mode_c_save()
