import serial
from gurux_dlms import GXDLMSClient
from gurux_dlms.enums import InterfaceType, Authentication, TraceLevel

ser = serial.Serial(
    port='COM4',          # or '/dev/ttyUSB0' on Linux
    baudrate=300,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_ONE,
    bytesize=7,
    timeout=5
)

client = GXDLMSClient(
    use_logical_name_referencing=True,
    client_address=16,
    server_address=1,
    authentication=Authentication.NONE,
    # password=b'yourpassword' if needed
    interface_type=InterfaceType.HDLC
)

client.trace = TraceLevel.VERBOSE

try:
    # ser.open()  # already open above
    # If IEC handshake needed (many optical probes):
    # from gurux_dlms.iec import initialize_iec
    # initialize_iec(client, ser)

    client.initialize_connection(ser)
    print("Connected!")

    # Read something simple
    reply = client.read("0.0.96.1.0.255", 2)  # manufacturer
    print("Manufacturer:", reply)

except Exception as e:
    print("Error:", e)
finally:
    client.disconnect(ser)
    ser.close()