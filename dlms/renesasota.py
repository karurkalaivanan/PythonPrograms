import serial
import time
from pathlib import Path

# XMODEM constants
XMODEM_SOH = 0x01
XMODEM_EOT = 0x04
XMODEM_ACK = 0x06
XMODEM_NAK = 0x15
XMODEM_CAN = 0x18


# Configure the serial port
ser = serial.Serial(
    port='COM5',  # Replace with your serial port
    baudrate=9600,
    timeout=1  # Set a timeout for read operations
)

# Check if the serial port is open
if ser.is_open:
    print("Serial port is open")
else:
    ser.open()
    print("Opened serial port")

# Function to calculate checksum
def calculate_checksum(data):
    checksum = sum(data) % 256  # Ensure checksum is a single byte (0-255)
    return checksum

def send_packet(packet, max_retries=10):
    for _ in range(max_retries):
        ser.write(packet)
        print(f"Sent {len(packet)} bytes: {packet.hex()}")
        response = ser.read(1)
        if response == bytes([XMODEM_ACK]):
            print("Received ACK")
            return True
        elif response == bytes([XMODEM_NAK]):
            print("Received NAK, retrying...")
        elif response == bytes([XMODEM_CAN]):
            print("Transmission canceled")
            return False
    print("Max retries reached, aborting...")
    return False
  
# Function to read hex file and send in 128-byte chunks
def send_hex_file(file_path):
    try:
        with open(file_path, 'rb') as hex_file:
            packet_number = 1  # Start with packet number 1
            while True:
                chunk = hex_file.read(128)
                if not chunk:
                    break
                checksum = calculate_checksum(chunk)
                
                packet = (
                    bytes([XMODEM_SOH]) +
                    bytes([packet_number]) +
                    bytes([255 - packet_number]) +
                    chunk +
                    bytes([checksum])
                )
                # ser.write(packet)
                if not send_packet(packet):
                    break  # Exit if transmission fails
                              
                packet_number = (packet_number + 1) % 256  # Increment packet number and wrap around at 256
                              
                time.sleep(0.1)  # Add a short delay to avoid overwhelming the receiver

    except Exception as e:
        print(f"Error: {e}")
    finally:
        ser.close()
        print("Serial port closed")

# Path to the hex file
hex_file_path = Path('led_blink.hex')

# Send the hex file
send_hex_file(hex_file_path)
