import serial
import time

# Mapping baud rate options from the protocol (4th letter in the response)
BAUD_RATES = {
    "0": 300,
    "1": 600,
    "2": 1200,
    "3": 2400,
    "4": 4800,
    "5": 9600,
    "6": 19200,
}

def read_response(ser):
    """Read a response from the serial connection."""
    try:
        response = ser.readline()
        if response:
            decoded_response = response.decode('ascii').strip()
            print(f"Received: {decoded_response}")
            return decoded_response
        else:
            print("No response received.")
            return None
    except Exception as e:
        print(f"Error reading response: {e}")
        return None
    
def initiate_serial_connection(port, baudrate=300):
    """Initialize the serial connection with the specified baud rate."""
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.SEVENBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=2
        )
        print(f"Serial port {port} opened with baud rate {baudrate}.")
        return ser
    except Exception as e:
        print(f"Error initializing serial connection: {e}")
        return None

def send_command(ser, command):
    """Send a command over the serial connection."""
    try:
        ser.write(command.encode())
        print(f"Sent: {command.strip()}")
    except Exception as e:
        print(f"Error sending command: {e}")

def wait_for_bytes(ser, byte_list, timeout=5):
    """
    Wait for specific bytes to appear in the serial data.

    Parameters:
        ser (serial.Serial): The open serial port object.
        byte_list (list): List of target byte values to wait for (e.g., [0x03, 0x05]).
        timeout (int): Maximum time to wait in seconds.

    Returns:
        bool: True if all target bytes are found, False if timeout occurs.
    """
    start_time = time.time()
    received_bytes = []

    while True:
        if ser.in_waiting > 0:
            # Read available bytes from the serial buffer
            byte = ser.read(1)
            byte_value = ord(byte)  # Convert to integer
            
            # Add the byte to received list if it's a target byte
            if byte_value in byte_list and byte_value not in received_bytes:
                received_bytes.append(byte_value)
                print(f"Received byte: 0x{byte_value:02X}")

            # Check if all target bytes are received
            if all(target in received_bytes for target in byte_list):
                print("All target bytes received.")
                return True

        # Break if timeout is reached
        if time.time() - start_time > timeout:
            print("Timeout reached while waiting for target bytes.")
            return False
        
def read_complete_response(ser):
    """Read a complete response until termination or timeout."""
    response = ""
    start_time = time.time()
    timeout = 10  # Adjust timeout as needed

    while True:
        chunk = ser.read(ser.in_waiting or 1).decode('ascii', errors='ignore')
        response += chunk
        if (time.time() - start_time > timeout): #'\r\n' in response or
            break

    print(f"Received complete response: {response.strip()}")
    return response.strip()

def switch_baud_rate(ser, baud_option):
    """Switch the baud rate based on the given baud option."""
    if baud_option in BAUD_RATES:
        new_baud_rate = BAUD_RATES[baud_option]
        ser.baudrate = new_baud_rate
        print(f"Switched to baud rate: {new_baud_rate}")
        return new_baud_rate
    else:
        print(f"Invalid baud rate option: {baud_option}")
        return None

def iec_62056_21_communication(port):
    """Perform communication using IEC 62056-21 protocol."""
    ser = initiate_serial_connection(port, baudrate=300)
    if not ser:
        return

    try:
        # Step 1: Send the sign-on command
        command_sign_on = "/?!\r\n"
        send_command(ser, command_sign_on)

        # Step 2: Receive the first response
        response = read_response(ser)
        if not response or len(response) < 4:
            print("Failed to establish initial communication or invalid response.")
            return

        # Extract the 4th letter from the response for baud rate switching
        fourth_letter = response[4]  # Index 3 for the 4th letter (0-based indexing)
        print(f"4th letter (baud rate option): {fourth_letter}")

        time.sleep(1)
        
        # Step 3: Send ACK and 040 command
        ack = "\x06"  # ASCII ACK character
        command_040 = f"{ack}040\r\n"
        send_command(ser, command_040)

        time.sleep(0.5)

        # Step 5: Switch the baud rate based on the 4th letter
        new_baud_rate = switch_baud_rate(ser, fourth_letter)
        if not new_baud_rate:
            print("Failed to switch baud rate. Exiting.")
            return

        # Step 6: Continue communication at the new baud rate
        print(f"Continuing communication at {new_baud_rate} baud.")
        final_response = read_complete_response(ser)
        if final_response:
            print(f"Final response: {final_response}")

    except Exception as e:
        print(f"Communication error: {e}")
    finally:
        ser.close()
        print("Serial communication complete. Port closed.")

# Example usage
if __name__ == "__main__":
    serial_port = "COM4"  # Replace with your serial port
    iec_62056_21_communication(serial_port)
