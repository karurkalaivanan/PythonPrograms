# Global sequence counters
g_RRR = 0  # Receive Sequence Number (3 bits)
g_SSS = 0  # Send Sequence Number (3 bits)

def get_sequence_number(nAct):
    global g_RRR, g_SSS
    cFrameType = 0

    if nAct == 0:
        # Increment Receive Sequence Number
        g_RRR = (g_RRR + 1) & 0x07  # Keep within 3 bits
    elif nAct == 1:
        # Increment Send Sequence Number
        g_SSS = (g_SSS + 1) & 0x07  # Keep within 3 bits
    elif nAct == 2:
        # Generate frame using current RRR and SSS
        cFrameType = ((g_RRR & 0x07) << 5) | 0x10
        cFrameType |= (g_SSS & 0x07) << 1
    elif nAct == 3:
        # Generate frame with poll/final bit = 1
        cFrameType = ((g_RRR & 0x07) << 5) | 0x10
        cFrameType |= 0x01

    return cFrameType

# Example: simulate a full frame (2 bytes)
def build_frame():
    high_byte = get_sequence_number(2)  # Case 2 returns frame type
    low_byte = get_sequence_number(3)   # Case 3 returns poll/final frame
    return high_byte, low_byte

# Example usage:
g_RRR = 4
g_SSS = 7

frame_hi, frame_lo = build_frame()
print(f"High byte: 0x{frame_hi:02X}  Binary: {frame_hi:08b}")
print(f"Low  byte: 0x{frame_lo:02X}  Binary: {frame_lo:08b}")
print(f"Full frame: 0x{frame_hi:02X}{frame_lo:02X}")
