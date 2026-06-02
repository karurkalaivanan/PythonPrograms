import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial
import serial.tools.list_ports
import threading
import time
import binascii
from datetime import datetime

# ---------------- Utility Functions ----------------

def calc_crc16(data_bytes):
    """Calculate CRC16 (sum of bytes) for FCS used between 2nd-9th bytes."""
    crc = sum(data_bytes) & 0xFFFF
    return [(crc >> 8) & 0xFF, crc & 0xFF]

# def extract_serial_number(rx_bytes):
#     """Extract serial number (ASCII) from GetResponseNormal frame."""
#     try:
#         data_hex = binascii.hexlify(rx_bytes).decode().upper()
#         idx = data_hex.find("090C")
#         if idx != -1:
#             serial_hex = data_hex[idx + 4: idx + 4 + (12 * 2)]  # 12 bytes
#             serial_ascii = bytes.fromhex(serial_hex).decode("ascii").strip()
#             return serial_ascii
#     except Exception as e:
#         print("Error decoding serial number:", e)
#     return None

def extract_serial_number(rx_bytes):
    """Extract serial number (ASCII) from DLMS GetResponseNormal frame."""
    try:
        data_hex = binascii.hexlify(rx_bytes).decode().upper()
        if "090C" in data_hex:
            idx = data_hex.find("090C")
            serial_hex = data_hex[idx + 4 : idx + 4 + (12 * 2)]
        elif "0908" in data_hex:
            idx = data_hex.find("0908")
            serial_hex = data_hex[idx + 4 : idx + 4 + (8 * 2)]
        else:
            return None
        return bytes.fromhex(serial_hex).decode("ascii").strip()
    except Exception:
        return None
def build_snrm_frame(dev_id):
    """Build SNRM frame for given device ID."""
    # 7E A0 0A 00 02 00 CB 21 93 7B BE 7E
    base = [0x7E, 0xA0, 0x0A, 0x00, 0x02, 0x00, 0xCB, dev_id]
    crc = calc_crc16(base[1:9])
    frame = base + crc + [ 0x7E ]
    return bytes(frame)

def build_aarq_frame(dev_id):
    """Build AARQ frame for given device ID."""
    base = [0x7E, 0xA0, 0x3A, 0x00, 0x02, 0x00, 0xCB, dev_id]
    crc = calc_crc16(base[1:9])
    frame = base + crc + [
        0xE6, 0xE6, 0x00, 0x60, 0x29, 0xA1, 0x09, 0x06, 0x07,
        0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01, 0xA6, 0x0A,
        0x04, 0x08, 0x52, 0x45, 0x4E, 0x30, 0x30, 0x30, 0x30,
        0xBE, 0x10, 0x04, 0x0E, 0x01, 0x00, 0x00, 0x00, 0x65,
        0xF1, 0xF0, 0x40, 0x40, 0xB8, 0x1F, 0xFF, 0xFF, 0xAC,
        0x58, 0x7E
    ]
    return bytes(frame)

def build_serial_read_frame(dev_id):
    """Build serial number read command for given device ID."""
    base = [0x7E, 0xA0, 0x1C, 0x00, 0x02, 0x00, 0xCB, dev_id]
    crc = calc_crc16(base[1:9])
    frame = base + crc + [
        0xE7, 0xE6, 0xE6, 0x00, 0xC0, 0x01, 0xC1, 0x00,
        0x01, 0x00, 0x00, 0x60, 0x01, 0x00, 0xFF, 0x02,
        0x00, 0x89, 0xA0, 0x7E
    ]
    return bytes(frame)

def build_disconnect_frame(dev_id):
    """Build disconnect frame for given device ID."""
    base = [0x7E, 0xA0, 0x0A, 0x00, 0x02, 0x00, 0xCB, dev_id]
    crc = calc_crc16(base[1:9])
    frame = base + crc + [0x77, 0x78, 0x7E]
    return bytes(frame)

# ---------------- Serial Communication ----------------

def send_and_receive(port, baud, frame, log_callback):
    try:
        with serial.Serial(port, baud, timeout=2) as ser:
            ser.write(frame)
            log_callback(f"➡️ Sent: {binascii.hexlify(frame).decode().upper()}")
            time.sleep(0.3)
            rx = ser.read(200)
            if rx:
                log_callback(f"⬅️ Received: {binascii.hexlify(rx).decode().upper()}")
                serial_number = extract_serial_number(rx)
                if serial_number:
                    log_callback(f"📟 Meter Serial Number: {serial_number}", "green")
            else:
                log_callback("⚠️ No response received.")
    except Exception as e:
        log_callback(f"❌ Error: {e}")

# ---------------- GUI Section ----------------

def refresh_ports():
    ports = [p.device for p in serial.tools.list_ports.comports()]
    port_combo["values"] = ports
    if ports:
        port_combo.current(0)

def read_meter(dev_id):
    port = port_combo.get()
    baud = int(baud_combo.get())
    if not port:
        messagebox.showwarning("Warning", "Please select a COM port.")
        return

    def task():
        log_callback(f"\n=== Reading Meter {dev_id} ===")
        send_and_receive(port, baud, build_snrm_frame(dev_id), log_callback)
        send_and_receive(port, baud, build_aarq_frame(dev_id), log_callback)
        send_and_receive(port, baud, build_serial_read_frame(dev_id), log_callback)
        send_and_receive(port, baud, build_disconnect_frame(dev_id), log_callback)
        log_callback(f"=== Completed Meter {dev_id} ===\n")

    threading.Thread(target=task, daemon=True).start()

def save_log():
    content = log_box.get("1.0", tk.END)
    if not content.strip():
        messagebox.showinfo("Info", "No log data to save.")
        return
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"DLMS_Log_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo("Success", f"Log saved successfully as {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save log: {e}")

def log_callback(msg, color=None):
    if color:
        log_box.insert(tk.END, msg + "\n", color)
    else:
        log_box.insert(tk.END, msg + "\n")
    log_box.yview_moveto(1.0)  # Auto-scroll

# ---------------- UI Layout ----------------

root = tk.Tk()
root.title("DLMS Meter Serial Reader")
root.geometry("860x550")

# Port Controls
frame_top = ttk.Frame(root, padding=10)
frame_top.pack(fill=tk.X)

ttk.Label(frame_top, text="COM Port:").pack(side=tk.LEFT, padx=5)
port_combo = ttk.Combobox(frame_top, width=15)
port_combo.pack(side=tk.LEFT, padx=5)
refresh_button = ttk.Button(frame_top, text="🔄 Refresh", command=refresh_ports)
refresh_button.pack(side=tk.LEFT, padx=5)

ttk.Label(frame_top, text="Baud Rate:").pack(side=tk.LEFT, padx=5)
baud_combo = ttk.Combobox(frame_top, values=["9600", "19200", "38400", "57600", "115200"], width=10)
baud_combo.set("9600")
baud_combo.pack(side=tk.LEFT, padx=5)

save_button = ttk.Button(frame_top, text="💾 Save Log", command=save_log)
save_button.pack(side=tk.RIGHT, padx=10)

# Meter Buttons
frame_buttons = ttk.Frame(root, padding=10)
frame_buttons.pack(fill=tk.X)

for i in range(101, 111):
    btn = ttk.Button(frame_buttons, text=f"Read Meter {i}", command=lambda d=i: read_meter(d))
    btn.pack(side=tk.LEFT, padx=5, pady=5)

# Log Box
log_box = tk.Text(root, wrap=tk.WORD, height=22, bg="black", fg="white", insertbackground="white")
log_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

log_box.tag_config("green", foreground="lime")

refresh_ports()
root.mainloop()
