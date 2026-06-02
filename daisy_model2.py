import serial
import serial.tools.list_ports
import time
import binascii
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime

# ==========================
# DLMS Helper Functions (from your file)
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
# DLMS Communication (uses callbacks)
# Each function accepts:
#  - port: COM port string
#  - device_addr: integer meter address
#  - log_cb: function(str) to append to common log
#  - serial_cb: function(str) to update the meter-specific result box
# ==========================
def send_dlms_sequence(port, device_addr, log_cb, serial_cb):
    serial_cb("READING...")
    try:
        with serial.Serial(port, baudrate=9600, timeout=1) as ser:
            addr_encoded = encode_hdlc_address_2bytes(device_addr)
            log_cb(f"{'='*60}")
            log_cb(f"COMMUNICATING WITH METER ID: {device_addr}")
            log_cb(f"{'='*60}")
            serial_cb(f"CONNECTING to {port}...")

            def send_and_log(name, frame_bytes, read_len=200, delay=1):
                log_cb(f"[TX] {name} -> {frame_bytes.hex(' ').upper()}")
                ser.write(frame_bytes)
                time.sleep(delay)
                resp = ser.read(read_len)
                log_cb(f"[RX] {name} ({len(resp)} bytes) -> {resp.hex(' ').upper()}")
                return resp

            # SNRM
            snrm = [0xA0, 0x0A, 0x00, 0x02] + addr_encoded + [0x21, 0x93]
            send_and_log("SNRM", build_dlms_frame(snrm), 100)

            # AARQ
            serial_cb("AUTHENTICATING...")
            aarq_start = [0xA0, 0x3A, 0x00, 0x02] + addr_encoded + [0x21, 0x10]
            inner_crc = crc16_ibm_sdlc(aarq_start[0:8])
            aarq_header = aarq_start + [inner_crc & 0xFF, (inner_crc >> 8) & 0xFF]
            aarq_rest = [
                0xE6,0xE6,0x00,0x60,0x29,0xA1,0x09,0x06,0x07,0x60,0x85,0x74,0x05,0x08,0x01,0x01,
                0xA6,0x0A,0x04,0x08,0x52,0x45,0x4E,0x30,0x30,0x30,0x30,0x30,0xBE,0x10,0x04,0x0E,
                0x01,0x00,0x00,0x00,0x06,0x5F,0x1F,0x04,0x00,0x40,0xB8,0x1F,0xFF,0xFF
            ]
            send_and_log("AARQ", build_dlms_frame(aarq_header + aarq_rest), 200)

            # GET Serial Number
            serial_cb("READING SERIAL...")
            get_start = [0xA0, 0x1C, 0x00, 0x02] + addr_encoded + [0x21, 0x32]
            inner_crc_get = crc16_ibm_sdlc(get_start[0:8])
            get_header = get_start + [inner_crc_get & 0xFF, (inner_crc_get >> 8) & 0xFF]
            get_rest = [0xE6,0xE6,0x00,0xC0,0x01,0xC1,0x00,0x01,0x00,0x00,0x60,0x01,0x00,0xFF,0x02,0x00]
            resp = send_and_log("GET Serial Number", build_dlms_frame(get_header + get_rest), 300)

            serial_no = extract_serial_number(resp)
            if serial_no:
                log_cb(f"SUCCESS: METER {device_addr} SERIAL: {serial_no}")
                serial_cb(serial_no)
            else:
                log_cb("WARNING: Serial number not found in response.")
                serial_cb("ERROR: No Serial Found")

            # DISCONNECT
            log_cb("DISCONNECTING...")
            disc_header = [0xA0, 0x0A, 0x00, 0x02] + addr_encoded + [0x21]
            disc_frame = build_dlms_frame(disc_header + [0x53])
            send_and_log("DISCONNECT", disc_frame, 100)

            log_cb("COMMUNICATION COMPLETED")
            log_cb(f"{'='*60}")

    except serial.SerialException as e:
        log_cb(f"ERROR: Serial Port Failed on {port} → {str(e)}")
        serial_cb("PORT ERROR")
    except Exception as e:
        log_cb(f"ERROR: Communication Failed on {port} → {str(e)}")
        serial_cb("COMM ERROR")

# ==========================
# GUI / App
# ==========================
class DLMSApp:
    def __init__(self, master):
        self.master = master
        master.title("All DLMS Meter Reader (30 fixed meters)")
        master.geometry("1000x760")
        master.minsize(900, 650)

        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Top frame for controls
        top_frame = ttk.Frame(master, padding=(12,10))
        top_frame.pack(fill="x")

        ttk.Label(top_frame, text="COM Port:").pack(side="left")
        self.port_combo = ttk.Combobox(top_frame, width=18, state="readonly")
        self.port_combo.pack(side="left", padx=(6,12))
        ttk.Button(top_frame, text="Refresh", command=self.refresh_ports).pack(side="left")
        # ttk.Button(top_frame, text="Read MSN", command=self.refresh_ports).pack(side="left")
        # msn_entry = ttk.Entry(top_frame, width=20)
        # msn_entry.pack(side="left", padx=5)
        # ttk.Button(top_frame, text="Read ID", command=self.refresh_ports).pack(side="left")
        # msn_entry = ttk.Entry(top_frame, width=20)
        # msn_entry.pack(side="left", padx=5)
        # ttk.Button(top_frame, text="Read ID", command=self.refresh_ports).pack(side="left")
        
        ttk.Label(top_frame, text="  ").pack(side="left")  # spacer

        ttk.Button(top_frame, text="Save Log", command=self.save_log).pack(side="right")
        ttk.Button(top_frame, text="Clear Log", command=lambda: self.log_box.delete("1.0", tk.END)).pack(side="right", padx=(6,0))

        # Middle frame: grid of 20 meter rows + log area
        middle = ttk.Frame(master, padding=(12,6))
        middle.pack(fill="both", expand=True)

        # Left: meters area (scrollable)
        meters_frame = ttk.LabelFrame(middle, text="Meters 101 - 130", padding=8)
        meters_frame.pack(side="left", fill="y", padx=(0,10))

        # Use a Canvas + Scrollbar so the 20 rows fit nicely
        canvas = tk.Canvas(meters_frame, width=420, height=420)
        vscroll = ttk.Scrollbar(meters_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        rows_container = ttk.Frame(canvas)
        canvas.create_window((0,0), window=rows_container, anchor="nw")

        # Create 20 rows (Meter 101..120)
        self.result_boxes = {}   # meter_id -> Text widget
        for idx, meter_id in enumerate(range(101, 131)):
            row = ttk.Frame(rows_container)
            row.grid(row=idx, column=0, pady=6, padx=6, sticky="w")

            lbl = ttk.Label(row, text=f"Meter {meter_id}", width=12)
            lbl.pack(side="left")

            result = tk.Text(row, height=1, width=28, font=("Consolas", 10))
            result.insert("1.0", "IDLE")
            result.config(state=tk.DISABLED)
            result.pack(side="left", padx=(6,6))

            btn = ttk.Button(row, text="Read", width=8, command=lambda m=meter_id: self.read_meter(m))
            btn.pack(side="left")
            # store
            self.result_boxes[meter_id] = result

        # Configure scrolling region
        rows_container.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Right: Log area
        log_frame = ttk.LabelFrame(middle, text="Communication Log", padding=8)
        log_frame.pack(side="left", fill="both", expand=True)

        self.log_box = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.log_box.pack(fill="both", expand=True)

        # Bottom: status bar
        self.status_bar = ttk.Label(master, text="Ready | Select a COM port and press Read", relief=tk.SUNKEN, anchor="w")
        self.status_bar.pack(fill="x", side="bottom")

        # Initialize ports
        self.refresh_ports()

    # GUI helpers
    def refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo["values"] = ports
        if ports:
            self.port_combo.current(0)
            self.status_bar.config(text=f"Ready | {len(ports)} COM port(s) detected")
        else:
            self.port_combo.set("")
            self.status_bar.config(text="No COM ports found")

    def append_log(self, text):
        """Thread-safe append to global log box."""
        def _append():
            ts = datetime.now().strftime("%H:%M:%S")
            self.log_box.insert(tk.END, f"[{ts}] {text}\n")
            self.log_box.see(tk.END)
        self.master.after(0, _append)

    def update_meter_box(self, meter_id, text):
        """Thread-safe update of the per-meter result box."""
        def _update():
            box = self.result_boxes.get(meter_id)
            if box:
                box.config(state=tk.NORMAL)
                box.delete("1.0", tk.END)
                box.insert(tk.END, str(text))
                box.config(state=tk.DISABLED)
        self.master.after(0, _update)

    def read_meter(self, meter_id):
        port = self.port_combo.get().strip()
        if not port:
            messagebox.showerror("Error", "Please select a COM port first.")
            return

        # Clear meter box and write status
        self.update_meter_box(meter_id, "Connecting...")
        self.append_log(f"Starting quick read for Meter {meter_id} on {port}")

        # Start threaded DLMS call
        t = threading.Thread(target=send_dlms_sequence,
                             args=(port, meter_id, self.append_log, lambda s, m=meter_id: self.update_meter_box(m, s)),
                             daemon=True)
        t.start()

    def save_log(self):
        content = self.log_box.get("1.0", tk.END).strip()
        if not content:
            messagebox.showinfo("Info", "No log to save.")
            return
        filename = f"DLMS_Log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"DLMS Multi-Meter Reader Log\nGenerated: {datetime.now()}\n\n")
                f.write(content)
            messagebox.showinfo("Saved", f"Log saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log: {e}")

# ==========================
# Run App
# ==========================
if __name__ == "__main__":
    root = tk.Tk()
    app = DLMSApp(root)
    root.mainloop()
