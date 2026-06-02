from gurux.serial import GXSmsClient
from gurux.serial import GXSerialEnumerator

def main():
    
    
    connection = GXSmsClient()
    connection.Address = "2401:4900:402c:F591::2"  # IPv6 address of the energy meter.
    connection.Port = 4001  # Modbus TCP port.

    # Connect to the energy meter.
    if not connection.Open():
        print("Failed to open connection to the energy meter.")
        return

    # Read the serial number (assuming it's stored in holding registers).
    register_address = 100  # Example register address where the serial number is stored.
    serial_number_data, result = connection.ReadHoldingRegisters(register_address, 2)  # Assuming serial number is 2 registers long.
    if not result:
        print("Failed to read serial number from the energy meter.")
        return

    # Parse the serial number data.
    serial_number = ''.join(format(byte, '02X') for byte in serial_number_data)  # Example parsing logic.

    print("Serial Number:", serial_number)

    # Close the connection.
    connection.Close()

if __name__ == "__main__":
    main()
