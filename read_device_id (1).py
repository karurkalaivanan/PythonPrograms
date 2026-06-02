import serial
import time

AARQ_LNT = "7EA04C0341106B04E6E600603EA109060760857405080101A60A040852454E30303030308A0207808B0760857405080201AC0680046C6E7431BE10040E01000000065F1F040040B81FFFFFFB267E"
AARQ_SECURE = "7EA044034110B3E1E6E6006036A1090607608574050801018A0207808B0760857405080201AC0A80084142434430303031BE10040E01000000065F1F0400621E5DFFFF50C77E"
# Serial port settings
SEND_AARQ = AARQ_SECURE

# Serial port settings
PORT = 'COM3'  # Adjust this if needed
BAUDRATE = 9600
TIMEOUT = 0.1  # Seconds

# DLMS frame commands
commands = {
    "Sending SNRM": "7EA0070341935A647E",
    "COSEM_Open_Request": SEND_AARQ,
    "GETRequestNormal": "7EA0190341323ABDE6E600C001C100170000160000FF090015C97E",
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
                    byte_17 = response[16]
                    byte_18 = response[17]
                    combined_value = (byte_17 << 8) | byte_18
                    print(f"Byte[17]: {byte_17:#02X}, Byte[18]: {byte_18:#02X}")
                    print(f"Device Address(Decimal): {combined_value}")
            else:
                print("No response")

except serial.SerialException as e:
    print(f"Serial error: {e}")
