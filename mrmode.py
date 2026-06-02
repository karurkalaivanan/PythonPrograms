import serial
from gurux_dlms import GXDLMSClient
from gurux_dlms.enums import Authentication

def main():
    # Open serial port
    ser = serial.Serial(port="COM5", baudrate=9600, bytesize=8, parity="N", stopbits=1, timeout=1)

    # Create DLMS client
    client = GXDLMSClient(
        useLogicalNameReferencing=True,
        clientAddress=16,
        serverAddress=1
    )
    client.authentication = Authentication.NONE
    client.password = None

    # SNRM request
    ser.write(client.snrmRequest())
    data = ser.read(1024)
    client.parseUAResponse(data)   # ✅ only one argument

    # Association request
    ser.write(client.aarqRequest())
    data = ser.read(1024)
    client.parseAAREResponse(data) # ✅ only one argument

    # OBIS code for billing profile (example: 0.0.98.1.0.255)
    billing_profile_obis = "0.0.98.1.0.255"

    # Read billing profile buffer (attribute 2)
    request = client.read(billing_profile_obis, 2)
    ser.write(request)
    data = ser.read(4096)
    result = client.parseResponse(data)  # ✅ returns parsed value directly

    print("Billing Profile Data:", result)

    # Disconnect
    ser.write(client.disconnectRequest())
    ser.close()

if __name__ == "__main__":
    main()
