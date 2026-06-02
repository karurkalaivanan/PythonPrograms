from pymodbus.client.serial import ModbusSerialClient

# Configuration
SERIAL_PORT = "COM8"  # Change for Windows (e.g., "COM3")
BAUDRATE = 9600
SLAVE_ID = 1

# Starting address for reading/writing the 10-digit serial number
REGISTER_START = 72  # Change based on meter's documentation
REGISTER_COUNT = 5  # Number of registers (each holds 2 ASCII characters)

# Define the new serial number to be written
new_serial_number = "NSGW999999"  # Change as needed

# Convert serial number to ASCII (each 16-bit register holds 2 characters)
new_data_pairs = [ord(new_serial_number[i]) << 8 | ord(new_serial_number[i + 1]) for i in range(0, len(new_serial_number), 2)]

# Initialize Modbus RTU client
client = ModbusSerialClient(
    port=SERIAL_PORT,
    baudrate=BAUDRATE,
    timeout=1,  # Wait for response
    parity='N',
    stopbits=1,
    bytesize=8
)

# Connect to the meter
if client.connect():
    print("Connected to energy meter.")

    try:
        # Step 1: Read the existing serial number
        print("\nReading current serial number from meter...")
        result = client.read_holding_registers(address=REGISTER_START, count=REGISTER_COUNT, slave=SLAVE_ID)  # UPDATED

        if result.isError():
            print("Error reading registers")
        elif result.registers:
            # Convert register values to a string
            current_serial_number = "".join(chr(value >> 8) + chr(value & 0xFF) for value in result.registers)
            print(f"Current Serial Number: {current_serial_number}")

            # Step 2: Compare with the new serial number
            if current_serial_number == new_serial_number:
                print("\nSerial number is already correct. No update needed.")
            else:
                print("\nSerial number mismatch. Updating meter...")
                # Step 3: Write the new serial number
                for i, value in enumerate(new_data_pairs):
                    reg_address = REGISTER_START + i
                    client.write_register(address=reg_address, value=value, slave=SLAVE_ID)  # UPDATED
                    print(f"Written {hex(value)} at register {reg_address}.")

                # Step 4: Verify the update
                print("\nVerifying the updated serial number...")
                result = client.read_holding_registers(address=REGISTER_START, count=REGISTER_COUNT, slave=SLAVE_ID)  # UPDATED
                if not result.isError() and result.registers:
                    updated_serial_number = "".join(chr(value >> 8) + chr(value & 0xFF) for value in result.registers)
                    print(f"Updated Serial Number: {updated_serial_number}")
                else:
                    print("Failed to read back the updated serial number.")

        else:
            print("Failed to read the current serial number.")

    except Exception as e:
        print("Error:", e)

    client.close()
else:
    print("Failed to connect to energy meter.")
