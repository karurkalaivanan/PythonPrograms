import serial
import serial.tools.list_ports
import time
import binascii
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime


# ==========================
# DLMS Helper Functions
# (These remain the same as they are the core protocol logic)
# ==========================
def reflect_bits(data, bits=8):
    reflection = 0
    for i in range(bits):
        if data & (1 << i):
            reflection |= 1 << (bits - 1 - i)
    return reflection


def crc16_ibm_sdlc(data):
    crc = 0xFFFF
    for byte in data:
        byte = reflect_bits(byte, 8)
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    crc = reflect_bits(crc, 16) ^ 0xFFFF
    return crc


def encode_hdlc_address_2bytes(address):
    lower_7 = (address & 0x7F) << 1 | 0x01
    upper_7 = ((address >> 7) & 0x7F) << 1
    return [upper_7, lower_7]


def build_dlms_frame(data_bytes):
    crc = crc16_ibm_sdlc(data_bytes)
    low = crc & 0xFF
    high = (crc >> 8) & 0xFF
    return bytes([0x7E] + data_bytes + [low, high, 0x7E])


def extract_serial_number(rx_bytes):
    try:
        data_hex = binascii.hexlify(rx_bytes).decode().upper()
        if "090C" in data_hex:
            idx = data_hex.find("090C")
            serial_hex = data_hex[idx + 4: idx + 4 + (12 * 2)]
        elif "0908" in data_hex:
            idx = data_hex.find("0908")
            serial_hex = data_hex[idx + 4: idx + 4 + (8 * 2)]
        else:
            return None
        return bytes.fromhex(serial_hex).decode("ascii").strip()
    except Exception:
        return None


# ==========================
# DLMS Communication Sequence
# ==========================
def send_dlms_sequence(port, device_addr, log_callback, serial_callback, hex_callback):
    """
    DLMS communication sequence: SNRM -> AARQ -> GET Serial Number -> DISCONNECT.
    """
    serial_callback("READING...")
    
    # We use a try block with a global serial object to manage the connection state.
    # The connection setup now resides in the connect_port function.
    if not hasattr(root, 'ser') or not root.ser or not root.ser.is_open:
        log_callback("\nERROR: Port not connected. Press CONNECT first.", log=True)
        serial_callback("PORT NOT OPEN")
        return

    ser = root.ser

    try:
        addr_encoded = encode_hdlc_address_2bytes(device_addr)
        log_callback(f"\n{'='*70}", log=True)
        log_callback(f"  READING SERIAL NUMBER (ID: {device_addr})  ", log=True)
        log_callback(f"{'='*70}", log=True)
        serial_callback(f"Communicating with ID {device_addr}...")

        def send_and_log(name, frame_bytes, read_len=200, delay=1):
            log_callback(f"\nSending {name}:\n   {frame_bytes.hex(' ').upper()}", log=True)
            ser.write(frame_bytes)
            time.sleep(delay)
            resp = ser.read(read_len)
            resp_hex = resp.hex(' ').upper()
            log_callback(f"Response ({len(resp)} bytes):\n   {resp_hex}\n", log=True)
            hex_callback(resp_hex) # Update raw hex area
            return resp

        # SNRM
        snrm = [0xA0, 0x0A, 0x00, 0x02] + addr_encoded + [0x21, 0x93]
        send_and_log("SNRM", build_dlms_frame(snrm), 100)

        # AARQ
        serial_callback("AUTHENTICATING...")
        aarq_start = [0xA0, 0x3A, 0x00, 0x02] + addr_encoded + [0x21, 0x10]
        inner_crc = crc16_ibm_sdlc(aarq_start[0:8])
        aarq_header = aarq_start + [inner_crc & 0xFF, (inner_crc >> 8) & 0xFF]
        aarq_rest = [
            0xE6,0xE6,0x00,0x60,0x29,0xA1,0x09,0x06,0x07,0x60,0x85,0x74,0x05,0x08,0x01,0x01,
            0xA6,0x0A,0x04,0x08,0x52,0x45,0x4E,0x30,0x30,0x30,0x30,0x30,0xBE,0x10,0x04,0x0E,
            0x01,0x00,0x00,0x00,0x06,0x5F,0x1F,0x04,0x00,0x40,0xB8,0x1F,0xFF,0xFF
        ]
        send_and_log("AARQ", build_dlms_frame(aarq_header + aarq_rest), 200, 2)

        # GET Serial Number
        serial_callback("READING SERIAL NUMBER...")
        get_start = [0xA0, 0x1C, 0x00, 0x02] + addr_encoded + [0x21, 0x32]
        inner_crc_get = crc16_ibm_sdlc(get_start[0:8])
        get_header = get_start + [inner_crc_get & 0xFF, (inner_crc_get >> 8) & 0xFF]
        get_rest = [0xE6,0xE6,0x00,0xC0,0x01,0xC1,0x00,0x01,0x00,0x00,0x60,0x01,0x00,0xFF,0x02,0x00]
        resp = send_and_log("GET Serial Number", build_dlms_frame(get_header + get_rest), 300, 2)

        serial_no = extract_serial_number(resp)
        if serial_no:
            log_callback(f"\nSUCCESS: METER SERIAL NUMBER: {serial_no}", log=True)
            serial_callback(serial_no)
        else:
            log_callback("WARNING: Serial number not found in response.", log=True)
            serial_callback("ERROR: No Serial Found")

        # DISCONNECT
        log_callback("DISCONNECTING...", log=True)
        disc_header = [0xA0, 0x0A, 0x00, 0x02] + addr_encoded + [0x21]
        disc_frame = build_dlms_frame(disc_header + [0x53])
        send_and_log("DISCONNECT", disc_frame, 100)

        log_callback(f"\n{'='*70}", log=True)
        log_callback("  COMMUNICATION COMPLETED  ", log=True)
        log_callback(f"{'='*70}\n", log=True)

    except serial.SerialException as e:
        log_callback(f"\nERROR: Serial Port Failed on {ser.port} → {str(e)}\n", log=True)
        serial_callback("PORT ERROR")
    except Exception as e:
        log_callback(f"\nERROR: Communication failed → {str(e)}\n", log=True)
        serial_callback("COMM ERROR")


# ==========================
# GUI Functions
# ==========================
def refresh_ports():
    ports = [p.device for p in serial.tools.list_ports.comports()]
    port_combo["values"] = ports
    if ports:
        port_combo.current(0)
        status_update(f"Ready | {len(ports)} COM port(s) detected", "#2e7d32")
    else:
        port_combo.set("")
        status_update("No COM ports found", "#c62828")

def connect_port():
    port = port_combo.get().strip()
    if not port:
        messagebox.showerror("Error", "Please select a COM port first.")
        return

    # If already connected, disconnect first
    if hasattr(root, 'ser') and root.ser and root.ser.is_open:
        disconnect_port()
        return

    try:
        root.ser = serial.Serial(port, baudrate=9600, timeout=2)
        connect_btn.config(text="DISCONNECT", bg="#c62828")
        status_update(f"SUCCESS: Connected to {port}", "#2e7d32")
        log_callback(f"\n*** Connected to {port} ***\n", log=True)
        serial_callback("CONNECTED")
    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to connect to {port}: {e}")
        status_update(f"ERROR: Connection failed to {port}", "#c62828")
        if hasattr(root, 'ser') and root.ser:
            root.ser = None

def disconnect_port():
    if hasattr(root, 'ser') and root.ser:
        try:
            if root.ser.is_open:
                root.ser.close()
            root.ser = None
            connect_btn.config(text="CONNECT", bg="#4CAF50")
            status_update("Disconnected", "#1565c0")
            log_callback("\n*** Port Disconnected ***\n", log=True)
            serial_callback("IDLE")
        except Exception as e:
            status_update(f"Error during disconnect: {e}", "#c62828")
            connect_btn.config(text="CONNECT", bg="#4CAF50") # Reset button even on error

def run_read_serial_number():
    # Meter address (Hardcoded to 1 for single meter read, or use a default)
    device_addr = 1 
    
    if not hasattr(root, 'ser') or not root.ser or not root.ser.is_open:
        messagebox.showerror("Error", "Port is not connected. Press CONNECT first.")
        return

    # Clear and start log
    log_box.delete("1.0", tk.END)
    log_box.insert(tk.END, f"Starting Serial Read (ID {device_addr}) on {root.ser.port}...\n\n")
    serial_callback("Connecting...")
    hex_callback("")
    
    # Start communication in a separate thread
    threading.Thread(target=send_dlms_sequence, 
                     args=(root.ser.port, device_addr, log_callback, serial_callback, hex_callback), 
                     daemon=True).start()

def read_slave_id_placeholder():
    # Placeholder for reading the current slave ID
    log_callback("\n--- ACTION: Read Current Slave ID (Not implemented in DLMS sequence) ---\n", log=True)
    messagebox.showinfo("Action", "Read Current Slave ID requested. Functionality not yet implemented.")

def set_new_slave_id():
    # Placeholder for setting a new slave ID
    new_id_str = slave_id_entry.get().strip()
    if not new_id_str.isdigit() or not (1 <= int(new_id_str) <= 9999):
        messagebox.showerror("Invalid Input", "Enter a valid Slave ID (1–9999).")
        return
        
    log_callback(f"\n--- ACTION: Set New Slave ID to {new_id_str} (Not implemented in DLMS sequence) ---\n", log=True)
    messagebox.showinfo("Action", f"Set New Slave ID to {new_id_str} requested. Functionality not yet implemented.")

# --- Callbacks for Thread Safety ---

def log_callback(msg, log=True):
    def _append():
        if log:
            log_box.insert(tk.END, msg + "\n")
            log_box.see(tk.END)
    root.after(0, _append)

def serial_callback(serial_no):
    def _update():
        serial_entry.config(state=tk.NORMAL)
        serial_entry.delete("1.0", tk.END)
        serial_entry.insert(tk.END, serial_no)
        serial_entry.config(state=tk.DISABLED)
        
        # Color feedback
        if "ERROR" in serial_no or "PORT" in serial_no:
             serial_entry.config(fg="#c62828")
        elif serial_no in ["READING...", "CONNECTED", "Connecting...", "Communicating with ID 1..."]:
             serial_entry.config(fg="#007bff") # Blue
        else: # Actual serial number / Idle
            serial_entry.config(fg="black")

    root.after(0, _update)

def hex_callback(hex_data):
    def _update():
        raw_hex_box.config(state=tk.NORMAL)
        raw_hex_box.delete("1.0", tk.END)
        raw_hex_box.insert(tk.END, hex_data)
        raw_hex_box.config(state=tk.DISABLED)
    root.after(0, _update)
    
def status_update(msg, color="#1565c0"):
    def _update():
        status_bar.config(text=msg, foreground=color)
    root.after(0, _update)


# ==========================
# GUI SETUP (MATCHING IMAGE)
# ==========================
root = tk.Tk()
root.title("DLMS Meter Probe - Daisy Chain & Single Meter")
root.geometry("1000x700")
root.minsize(800, 600)
root.configure(bg="#e0e0e0")

# --- Main Frame for Two Columns ---
main_frame = tk.Frame(root, bg="#e0e0e0")
main_frame.pack(fill="both", expand=True)

# --- Left Column (Controls) ---
left_frame = tk.Frame(main_frame, bg="white", width=300)
left_frame.pack(fill="y", side="left", padx=(10, 5), pady=10)
left_frame.pack_propagate(False)

tk.Label(left_frame, text="DLMS / HDLC Meter Tool", font=("Segoe UI", 16, "bold"), fg="#333", bg="white").pack(pady=(10, 20), padx=20, anchor="w")

# 1. Connection Panel
conn_panel = tk.Frame(left_frame, bg="white", padx=20)
conn_panel.pack(fill="x", pady=10)

tk.Label(conn_panel, text="COM Port", font=("Segoe UI", 10), bg="white").pack(anchor="w")
port_combo = ttk.Combobox(conn_panel, width=15, font=("Consolas", 10), state="readonly")
port_combo.pack(fill="x", pady=(0, 5))

ttk.Button(conn_panel, text="Refresh Ports", command=refresh_ports).pack(fill="x", pady=5)

connect_btn = tk.Button(conn_panel, text="CONNECT", font=("Segoe UI", 14, "bold"), bg="#4CAF50", fg="white", activebackground="#2e7d32", relief="raised", bd=3, command=connect_port)
connect_btn.pack(fill="x", pady=15, ipady=10)

# 2. Actions Panel
tk.Label(left_frame, text="Actions", font=("Segoe UI", 12, "bold"), bg="white").pack(pady=(15, 5), padx=20, anchor="w")

actions_panel = tk.Frame(left_frame, bg="white", padx=20)
actions_panel.pack(fill="x", pady=5)

# Serial Number Read Button (Blue)
read_serial_btn = tk.Button(actions_panel, text="Read Meter Serial Number", font=("Segoe UI", 10, "bold"), bg="#1976D2", fg="white", activebackground="#1565c0", relief="raised", bd=3, command=run_read_serial_number)
read_serial_btn.pack(fill="x", pady=8, ipady=5)

# Current Slave ID Button (Blue)
read_slave_btn = tk.Button(actions_panel, text="Read Current Slave ID", font=("Segoe UI", 10, "bold"), bg="#1976D2", fg="white", activebackground="#1565c0", relief="raised", bd=3, command=read_slave_id_placeholder)
read_slave_btn.pack(fill="x", pady=8, ipady=5)

# 3. New Slave ID Panel
slave_id_entry = tk.Entry(actions_panel, width=15, font=("Consolas", 11), justify="center", bd=1, relief=tk.SUNKEN)
slave_id_entry.insert(0, "1-9999")
slave_id_entry.pack(fill="x", pady=(10, 5), ipady=5)

set_slave_btn = tk.Button(actions_panel, text="SET NEW SLAVE ID", font=("Segoe UI", 11, "bold"), bg="orange", fg="white", activebackground="#ff8f00", relief="raised", bd=3, command=set_new_slave_id)
set_slave_btn.pack(fill="x", pady=5, ipady=8)


# --- Right Column (Logs) ---
right_frame = tk.Frame(main_frame, bg="#f0f0f0")
right_frame.pack(fill="both", side="left", expand=True, padx=(5, 10), pady=10)
right_frame.grid_columnconfigure(0, weight=1)
right_frame.grid_rowconfigure(0, weight=3) # Live Log takes 3/4 height
right_frame.grid_rowconfigure(1, weight=1) # Raw Hex takes 1/4 height

# 1. Live Log
log_label = tk.Label(right_frame, text="Live Log", font=("Segoe UI", 12, "bold"), fg="#333", bg="#f0f0f0")
log_label.grid(row=0, column=0, sticky="new", padx=5, pady=(0, 2))

log_box = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, font=("Consolas", 9), bg="white", fg="black", relief=tk.FLAT, bd=2, insertbackground='black')
log_box.grid(row=0, column=0, sticky="nsew", padx=5, pady=(25, 5))


# Hidden Serial Number/Status for internal tracking, placed below logs
serial_entry = tk.Text(right_frame, wrap=tk.WORD, height=1, width=30, font=("Consolas", 1, "bold"), bg="#f0f0f0", fg="#f0f0f0", relief=tk.FLAT, bd=0)
# serial_entry.grid(row=2, column=0, sticky="s") # Kept visible for easy debugging, but visually hidden

# 2. Raw Hex Area
raw_hex_label = tk.Label(right_frame, text="Raw Hex", font=("Segoe UI", 12, "bold"), fg="#333", bg="#f0f0f0")
raw_hex_label.grid(row=1, column=0, sticky="w", padx=5, pady=(5, 2))

raw_hex_box = tk.Text(right_frame, wrap=tk.WORD, font=("Consolas", 9), bg="#1e1e1e", fg="#00ff88", relief=tk.FLAT, bd=2, insertbackground='#00ff88', height=8)
raw_hex_box.grid(row=1, column=0, sticky="nsew", padx=5, pady=(25, 5))
raw_hex_box.insert(tk.END, "Last received response payload in Hexadecimal format...")
raw_hex_box.config(state=tk.DISABLED)


# Status Bar (Moved to the bottom edge of the root window)
status_bar = tk.Label(root, text="Ready | Select a COM port to begin", relief=tk.SUNKEN, anchor="w", padx=15, font=("Segoe UI", 10), bg="#e0e0e0", fg="#1565c0")
status_bar.pack(fill="x", side="bottom")

# Initial setup
refresh_ports()
serial_callback("IDLE")
root.ser = None # Initialize serial port object
root.protocol("WM_DELETE_WINDOW", lambda: (disconnect_port(), root.destroy())) # Ensure port closes on exit
root.mainloop()