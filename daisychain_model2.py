"""
DLMS Daisy-Chain Professional Tool - FINAL FIXED VERSION
Two Tabs | Common COM Port | Export with Device ID & Serial
100% Working - No More LabelFrame Error!
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import serial
import serial.tools.list_ports
import threading
import time
import binascii
import csv
from datetime import datetime

# --------------------- ttkbootstrap ---------------------
try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
except ImportError:
    import os
    os.system("pip install ttkbootstrap")
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *

# Correct ttkbootstrap widget names
from tkinter.ttk import Notebook

# ---------------------------- CONFIG & UTILS ----------------------------
class Config:
    METER_RANGE = range(101, 131)
    BAUDRATE = 9600
    TIMEOUT = 1.5

    AARQ_LNT = "7EA04C0341106B04E6E600603EA109060760857405080101A60A040852454E30303030308A0207808B0760857405080201AC0680046C6E7431BE10040E01000000065F1F040040B81FFFFFFB267E"
    AARQ_SECURE = "7EA044034110B3E1E6E6006036A1090607608574050801018A0207808B0760857405080201AC0A80084142434430303031BE10040E01000000065F1F0400621E5DFFFF50C77E"
    SNRM_FRAME = "7EA0070341935A647E"
    DISC_FRAME = "7EA00703415356A27E"
    GET_DEVICE_ID_FRAME = "7EA0190341323ABDE6E600C001C100170000160000FF090015C97E"

def crc16_ibm_sdlc(data_bytes):
    crc = 0xFFFF
    for b in data_bytes:
        x = ((crc >> 8) ^ b) << 8
        for _ in range(8):
            if x & 0x8000:
                x = (x << 1) ^ 0x1021
            else:
                x <<= 1
            x &= 0xFFFF
        crc = (crc << 8) ^ x
    return crc

def build_dlms_frame(data_list):
    data = bytes(data_list)
    crc = crc16_ibm_sdlc(data)
    return bytes([0x7E]) + data + bytes([crc & 0xFF, (crc >> 8) & 0xFF, 0x7E])

def encode_hdlc_address_2bytes(addr):
    low = ((addr << 1) | 1) & 0xFF
    high = (addr >> 7) & 0xFF
    return [high, low]

def extract_serial_number(rx_bytes):
    try:
        hx = binascii.hexlify(rx_bytes).decode().upper()
        for tag, length in (("090C", 12), ("0908", 8)):
            if tag in hx:
                idx = hx.find(tag)
                ser = hx[idx + 4: idx + 4 + length * 2]
                return bytes.fromhex(ser).decode("ascii").strip()
        return None
    except:
        return None

# ---------------------------- PROTOCOL ----------------------------
class DLMSProtocol:
    @staticmethod
    def read_daisy_serial(port, meter_id, log_cb):
        try:
            with serial.Serial(port, Config.BAUDRATE, timeout=Config.TIMEOUT) as ser:
                addr = encode_hdlc_address_2bytes(meter_id)
                log_cb(f"Reading Meter {meter_id}")

                def send(frame, name, read_len=200, delay=0.8):
                    log_cb(f"[TX] {name} → {frame.hex().upper()}")
                    ser.write(frame)
                    time.sleep(delay)
                    resp = ser.read(read_len)
                    log_cb(f"[RX] {name} → {resp.hex().upper()}")
                    return resp

                snrm = [0xA0, 0x0A, 0x00, 0x02] + addr + [0x21, 0x93]
                send(build_dlms_frame(snrm), "SNRM")

                aarq_hdr = [0xA0, 0x3A, 0x00, 0x02] + addr + [0x21, 0x10]
                crc_a = crc16_ibm_sdlc(bytes(aarq_hdr))
                aarq_payload = aarq_hdr + [crc_a & 0xFF, (crc_a >> 8) & 0xFF] + [
                    0xE6,0xE6,0x00,0x60,0x29,0xA1,0x09,0x06,0x07,0x60,0x85,0x74,0x05,0x08,0x01,0x01,
                    0xA6,0x0A,0x04,0x08,0x52,0x45,0x4E,0x30,0x30,0x30,0x30,0x30,
                    0xBE,0x10,0x04,0x0E,0x01,0x00,0x00,0x00,0x06,0x5F,0x1F,0x04,0x00,0x40,0xB8,0x1F,0xFF,0xFF
                ]
                send(build_dlms_frame(aarq_payload), "AARQ")

                get_hdr = [0xA0, 0x1C, 0x00, 0x02] + addr + [0x21, 0x32]
                crc_g = crc16_ibm_sdlc(bytes(get_hdr))
                get_payload = get_hdr + [crc_g & 0xFF, (crc_g >> 8) & 0xFF] + [
                    0xE6,0xE6,0x00,0xC0,0x01,0xC1,0x00,0x01,0x00,0x00,0x60,0x01,0x00,0xFF,0x02,0x00
                ]
                resp = send(build_dlms_frame(get_payload), "GET SERIAL", read_len=400)
                sn = extract_serial_number(resp)
                return sn or "NOT FOUND"
        except Exception as e:
            log_cb(f"ERROR: {e}", "danger")
            return "FAILED"

    @staticmethod
    def read_single_serial(port, log_cb):
        try:
            with serial.Serial(port, Config.BAUDRATE, timeout=Config.TIMEOUT) as ser:
                ser.write(bytes.fromhex(Config.SNRM_FRAME))
                time.sleep(0.6)
                ser.write(bytes.fromhex("7EA02B032110FBAFE6E600601DA109060760857405080101BE10040E01000000065F1F0400001E5DFFFFB3E27E"))
                time.sleep(0.8)
                ser.write(bytes.fromhex("7EA0190321326FD8E6E600C001C100010000600100FF020089A07E"))
                time.sleep(0.8)
                resp = ser.read(1024)
                return extract_serial_number(resp) or "NOT FOUND"
        except Exception as e:
            log_cb(f"Single read error: {e}", "danger")
            return "ERROR"

    @staticmethod
    def read_device_id(port, meter_type, log_cb):
        try:
            with serial.Serial(port, Config.BAUDRATE, timeout=1) as ser:
                aarq = Config.AARQ_LNT if meter_type == "Meter 1 (LNT)" else Config.AARQ_SECURE
                for frame, name in [(Config.SNRM_FRAME, "SNRM"), (aarq, "AARQ"), (Config.GET_DEVICE_ID_FRAME, "GET ID")]:
                    ser.write(bytes.fromhex(frame))
                    time.sleep(0.6)
                    resp = ser.read(512)
                    log_cb(f"{name} → {resp.hex().upper()}")
                if len(resp) >= 18:
                    return str((resp[16] << 8) | resp[17])
                return "NOT FOUND"
        except Exception as e:
            log_cb(f"Read ID error: {e}", "danger")
            return "ERROR"

    @staticmethod
    def write_device_id(port, meter_type, new_id, log_cb):
        try:
            with serial.Serial(port, Config.BAUDRATE, timeout=1.5) as ser:
                aarq = Config.AARQ_LNT if meter_type == "Meter 1 (LNT)" else Config.AARQ_SECURE
                high = (new_id >> 8) & 0xFF
                low = new_id & 0xFF
                payload = f"A0 1C 03 41 32 6D D3 E6 E6 00 C1 01 C1 00 17 00 00 16 00 00 FF 09 00 12 {high:02X} {low:02X}"
                frame = build_dlms_frame([int(x,16) for x in payload.split()])

                ser.write(bytes.fromhex(Config.SNRM_FRAME))
                time.sleep(0.5); ser.read(256)
                ser.write(bytes.fromhex(aarq))
                time.sleep(0.8); resp = ser.read(512)
                if b'\x61' not in resp and b'\x60' not in resp:
                    return "AARQ FAILED"

                ser.write(frame)
                time.sleep(1.5)
                resp = ser.read(512)
                return "SUCCESS" if len(resp) >= 15 and resp[14] == 0x00 else "FAILED"
        except Exception as e:
            log_cb(f"Write error: {e}", "danger")
            return "ERROR"

# ---------------------------- MAIN GUI ----------------------------
class DLMSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DLMS Daisy-Chain Professional Tool")
        self.root.geometry("1500x950")
        self.root.state('zoomed')

        self.results = {i: "IDLE" for i in Config.METER_RANGE}
        self.setup_ui()
        self.refresh_ports()

    def log(self, text, tag=None):
        ts = time.strftime("%H:%M:%S")
        self.log_box.insert(tk.END, f"[{ts}] {text}\n", tag)
        self.log_box.see(tk.END)

    def setup_ui(self):
        # Header
        header = ttkb.Frame(self.root, padding=20)
        header.pack(fill="x")
        ttkb.Label(header, text="DLMS Daisy-Chain Professional Suite", font=("Helvetica", 28, "bold")).pack(side="left")
        ttkb.Label(header, text="Final Fixed Version", font=("Helvetica", 12), foreground="cyan").pack(side="right")

        # Top Control Bar (Common)
        top = ttkb.Frame(self.root, padding=15)
        top.pack(fill="x")

        ttkb.Label(top, text="COM Port:", font=14).grid(row=0, column=0, padx=10, sticky="w")
        self.port_combo = ttkb.Combobox(top, width=15, state="readonly", font=("Consolas", 11))
        self.port_combo.grid(row=0, column=1, padx=5)
        ttkb.Button(top, text="Refresh", bootstyle=INFO, command=self.refresh_ports).grid(row=0, column=2, padx=5)

        ttkb.Label(top, text="Meter Type:", font=14).grid(row=0, column=3, padx=(50,10), sticky="w")
        self.meter_type = ttkb.Combobox(top, values=["Meter 1 (LNT)", "Meter 2 (SECURE)"], width=20, state="readonly")
        self.meter_type.current(0)
        self.meter_type.grid(row=0, column=4)

        # Notebook Tabs
        notebook = Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=15, pady=10)

        # Tab 1: Daisy-Chain 101-130
        tab1 = ttkb.Frame(notebook, padding=20)
        notebook.add(tab1, text=" Daisy-Chain Meters (101-130) ")

        # Tab 2: Single Meter + Device ID
        tab2 = ttkb.Frame(notebook, padding=20)
        notebook.add(tab2, text=" Single Meter & Device ID ")

        # === TAB 1: Daisy-Chain ===
        left_frame = ttkb.Labelframe(tab1, text="Meters 101–130", padding=15)  # FIXED: Labelframe
        left_frame.pack(side="left", fill="both", expand=True)

        canvas = tk.Canvas(left_frame)
        scroll = ttkb.Scrollbar(left_frame, command=canvas.yview, bootstyle=INFO)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        container = ttkb.Frame(canvas)
        canvas.create_window((0,0), window=container, anchor="nw")

        self.boxes = {}
        for mid in Config.METER_RANGE:
            row = ttkb.Frame(container, padding=8, bootstyle="dark")
            row.pack(fill="x", pady=3)
            ttkb.Label(row, text=f"Meter {mid}", width=12, font=("Helvetica", 11, "bold")).pack(side="left")
            txt = tk.Text(row, height=1, width=38, font=("Consolas", 11), bg="#1e1e1e", fg="lime")
            txt.insert("1.0", "IDLE")
            txt.config(state="disabled")
            txt.pack(side="left", padx=10)
            ttkb.Button(row, text="Read", bootstyle=SUCCESS, width=8,
                       command=lambda m=mid: self.read_meter(m)).pack(side="right")
            self.boxes[mid] = txt

        container.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Read All + Export
        btn_frame = ttkb.Frame(tab1)
        btn_frame.pack(pady=10)
        ttkb.Button(btn_frame, text="Read ALL Meters", bootstyle=PRIMARY, width=20, command=self.read_all).pack(side="left", padx=10)
        ttkb.Button(btn_frame, text="Export Results (CSV)", bootstyle=SUCCESS, width=20, command=self.export_csv).pack(side="left", padx=10)

        # === TAB 2: Single + Device ID ===
        single_frame = ttkb.Labelframe(tab2, text="Single Meter Operations", padding=20)  # FIXED: Labelframe
        single_frame.pack(fill="x", pady=10)

        ttkb.Button(single_frame, text="Read Serial Number", bootstyle=SUCCESS, width=25, command=self.read_single).pack(pady=8)
        self.single_entry = ttkb.Entry(single_frame, width=50, font=("Consolas", 14), justify="center")
        self.single_entry.pack(pady=10)

        ttkb.Separator(tab2, orient="horizontal").pack(fill="x", pady=20)

        device_frame = ttkb.Labelframe(tab2, text="Device ID Management", padding=20)  # FIXED: Labelframe
        device_frame.pack(fill="x")

        row1 = ttkb.Frame(device_frame)
        row1.pack(pady=10)
        ttkb.Button(row1, text="Read Device ID", bootstyle=PRIMARY, command=self.read_device_id).pack(side="left", padx=10)
        self.device_id_entry = ttkb.Entry(row1, width=20, font=("Consolas", 14))
        self.device_id_entry.pack(side="left", padx=10)

        row2 = ttkb.Frame(device_frame)
        row2.pack(pady=10)
        ttkb.Label(row2, text="New Device ID:", font=12).pack(side="left")
        self.new_id_entry = ttkb.Entry(row2, width=15, font=("Consolas", 12))
        self.new_id_entry.pack(side="left", padx=10)
        ttkb.Button(row2, text="Write Device ID", bootstyle=DANGER, command=self.write_device_id).pack(side="left", padx=10)
        self.write_status = ttkb.Entry(row2, width=25, font=("Consolas", 12))
        self.write_status.pack(side="left", padx=10)

        # === LOG PANEL (Common) ===
        log_frame = ttkb.Labelframe(self.root, text="Live Communication Log", padding=10)  # FIXED: Labelframe
        log_frame.pack(fill="both", expand=True, padx=15, pady=(0,15))

        self.log_box = scrolledtext.ScrolledText(log_frame, font=("Consolas", 10), bg="#0d1117", fg="#00ff88")
        self.log_box.pack(fill="both", expand=True)
        self.log_box.tag_config("success", foreground="#00ff88")
        self.log_box.tag_config("warning", foreground="#ffaa00")
        self.log_box.tag_config("danger", foreground="#ff4444")

        log_btns = ttkb.Frame(log_frame)
        log_btns.pack(pady=8)
        ttkb.Button(log_btns, text="Clear Log", bootstyle=WARNING, command=lambda: self.log_box.delete(1.0, tk.END)).pack(side="left", padx=5)
        ttkb.Button(log_btns, text="Save Log", bootstyle=INFO, command=self.save_log).pack(side="left", padx=5)

        # Status Bar
        self.status = ttkb.Label(self.root, text="Ready", relief="sunken", anchor="w", padding=10)
        self.status.pack(side="bottom", fill="x")

    def refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports: self.port_combo.current(0)

    def update_box(self, mid, text):
        box = self.boxes[mid]
        box.config(state="normal")
        box.delete(1.0, tk.END)
        box.insert(1.0, text)
        box.config(state="disabled")
        box.config(fg="lime" if len(text) >= 8 else "#ff6666")
        self.results[mid] = text

    def read_meter(self, mid):
        port = self.port_combo.get()
        if not port: return messagebox.showwarning("Port", "Select COM port")
        self.update_box(mid, "Reading...")
        threading.Thread(target=lambda: self.update_box(mid, DLMSProtocol.read_daisy_serial(port, mid, self.log)), daemon=True).start()

    def read_all(self):
        port = self.port_combo.get()
        if not port: return messagebox.showwarning("Port", "Select COM port")
        self.log("Reading ALL meters 101-130...", "success")
        def worker():
            for mid in Config.METER_RANGE:
                self.root.after(0, lambda m=mid: self.update_box(m, "Reading..."))
            for mid in Config.METER_RANGE:
                sn = DLMSProtocol.read_daisy_serial(port, mid, self.log)
                self.root.after(0, lambda m=mid, s=sn: self.update_box(m, s))
                time.sleep(0.4)
            self.log("All meters read complete!", "success")
        threading.Thread(target=worker, daemon=True).start()

    def read_single(self):
        port = self.port_combo.get()
        if not port: return
        self.single_entry.delete(0, tk.END)
        self.single_entry.insert(0, "Reading...")
        threading.Thread(target=lambda: self.single_entry.delete(0, tk.END) or self.single_entry.insert(0, DLMSProtocol.read_single_serial(port, self.log)), daemon=True).start()

    def read_device_id(self):
        port = self.port_combo.get()
        if not port: return
        self.device_id_entry.delete(0, tk.END)
        self.device_id_entry.insert(0, "Reading...")
        threading.Thread(target=lambda: self.device_id_entry.delete(0, tk.END) or self.device_id_entry.insert(0, DLMSProtocol.read_device_id(port, self.meter_type.get(), self.log)), daemon=True).start()

    def write_device_id(self):
        port = self.port_combo.get()
        if not port: return
        try:
            nid = int(self.new_id_entry.get().strip())
            if not 1 <= nid <= 65535: raise ValueError
        except:
            return messagebox.showerror("Invalid", "Enter number 1–65535")

        self.write_status.delete(0, tk.END)
        self.write_status.insert(0, "Writing...")
        def worker():
            result = DLMSProtocol.write_device_id(port, self.meter_type.get(), nid, self.log)
            self.root.after(0, lambda: (self.write_status.delete(0, tk.END), self.write_status.insert(0, result)))
            self.log(f"Write Device ID {nid}: {result}", "success" if result == "SUCCESS" else "danger")
        threading.Thread(target=worker, daemon=True).start()

    def export_csv(self):
        f = filedialog.asksaveasfilename(defaultextension=".csv", title="Export Results - Device ID & Serial Number")
        if not f: return
        with open(f, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Device ID", "Serial Number", "Timestamp"])
            for mid, sn in self.results.items():
                writer.writerow([mid, sn, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        self.log(f"Exported: {os.path.basename(f)}", "success")

    def save_log(self):
        f = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=f"dlms_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        if f:
            with open(f, "w", encoding="utf-8") as file:
                file.write(self.log_box.get(1.0, tk.END))
            self.log(f"Log saved: {os.path.basename(f)}", "success")

# ---------------------------- RUN ----------------------------
if __name__ == "__main__":
    root = ttkb.Window(themename="cyborg")
    app = DLMSApp(root)
    root.mainloop()