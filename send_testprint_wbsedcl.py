#!/usr/bin/env python3
"""
Send an ESC/POS command sequence over UART.

Install pyserial first:
    pip install pyserial
"""

import serial
import time

# ---------- Configure these ----------
PORT      = "COM11"      # e.g. "COM5" on Windows or "/dev/ttyUSB0" on Linux
BAUDRATE  = 9600        # typical for small printers
# -------------------------------------

# The command block you listed, written as one hex string
HEX_STRING = """
1B 40
1B 21 01 1B 45 01 1B 61 01
57 45 4C 43 4F 4D 45 20 54 4F 20 53 50 4F 54 20 42 49 4C 4C 49 4E 47 20 4D
4F 42 49 4C 45 20 41 50 50 53
0D 0A
54 48 49 53 20 49 53 20 54 45 53 54 20 50 52 49 4E 54
0D 0A
54 48 41 4E 4B 20 59 4F 55
0A 0A 0A 0A
"""

def hex_to_bytes(hex_str: str) -> bytes:
    """Convert any whitespace‑separated hex string to a bytes object."""
    hex_str = hex_str.strip().replace("\n", " ")
    byte_list = [int(b, 16) for b in hex_str.split() if b]
    return bytes(byte_list)

def main() -> None:
    data = hex_to_bytes(HEX_STRING)

    print(f"Opening {PORT} @ {BAUDRATE} baud …")
    with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
        ser.write(data)
        ser.flush()          # make sure all bytes go out
        print(f"Sent {len(data)} bytes")

    # Some printers need a small delay after reset before next command
    time.sleep(0.2)

if __name__ == "__main__":
    main()
