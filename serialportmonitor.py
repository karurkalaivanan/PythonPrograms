import threading
import queue
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import serial
import serial.tools.list_ports
import re
import json
from pathlib import Path
from datetime import datetime

HIST_FILE = Path.home() / ".serial_gui_history.json"
MAX_HISTORY = 100  # keep last N entries


class SerialGUI(tk.Tk):
    """Serial Monitor with colored TX/RX, persistent history, dual RX panes, and rich TX controls."""

    HEX_RE = re.compile(r"(?:0x)?([0-9A-Fa-f]{2})")

    def __init__(self):
        super().__init__()
        self.title("Serial Monitor")
        self.geometry("1080x600")

        # --- runtime state ---
        self.ser: serial.Serial | None = None
        self.reader_thread: threading.Thread | None = None
        self.alive = threading.Event()
        self.rx_queue: queue.Queue[bytes] = queue.Queue()
        self.tx_history: list[str] = self._load_history()

        # --- build UI ---
        self._build_toolbar()
        self._build_main_panes()
        self._populate_history_listbox()
        self.after(100, self._pump_rx)

    # ========== History ==========
    def _load_history(self):
        if HIST_FILE.exists():
            try:
                return json.loads(HIST_FILE.read_text())[:MAX_HISTORY]
            except Exception:
                pass
        return []

    def _save_history(self):
        try:
            HIST_FILE.write_text(json.dumps(self.tx_history[-MAX_HISTORY:]))
        except Exception:
            pass

    def _add_history(self, label):
        if label in self.tx_history:
            self.tx_history.remove(label)
        self.tx_history.append(label)
        self._save_history()
        self._populate_history_listbox()

    def _populate_history_listbox(self):
        self.hist_list.delete(0, tk.END)
        for item in reversed(self.tx_history):
            self.hist_list.insert(tk.END, item)

    # ========== UI BUILD ==========
    def _build_toolbar(self):
        bar = ttk.Frame(self)
        bar.pack(fill=tk.X, padx=10, pady=6)

        ttk.Label(bar, text="Port:").pack(side=tk.LEFT)
        self.port_cmb = ttk.Combobox(bar, width=14, values=self._list_ports())
        self.port_cmb.pack(side=tk.LEFT, padx=4)

        ttk.Label(bar, text="Baud:").pack(side=tk.LEFT)
        self.baud_cmb = ttk.Combobox(bar, width=10, values=[9600, 19200, 38400, 57600, 115200, 230400])
        self.baud_cmb.set(115200)
        self.baud_cmb.pack(side=tk.LEFT, padx=4)

        self.connect_btn = ttk.Button(bar, text="Connect", command=self.toggle_connection)
        self.connect_btn.pack(side=tk.LEFT, padx=6)

        ttk.Button(bar, text="⟳", width=3, command=lambda: self.port_cmb.configure(values=self._list_ports())).pack(side=tk.LEFT)

        ttk.Separator(bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)

        self.tx_entry = ttk.Entry(bar, width=50)
        self.tx_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.send_text_btn = ttk.Button(bar, text="Send Text", command=self.send_text, state=tk.DISABLED)
        self.send_text_btn.pack(side=tk.LEFT, padx=4)

        self.send_hex_btn = ttk.Button(bar, text="Send Hex", command=self.send_hex, state=tk.DISABLED)
        self.send_hex_btn.pack(side=tk.LEFT, padx=4)

        self.file_btn = ttk.Button(bar, text="HEX file…", command=self.send_file, state=tk.DISABLED)
        self.file_btn.pack(side=tk.LEFT, padx=4)

        ttk.Button(bar, text="Clear Output", command=self.clear_output).pack(side=tk.RIGHT)

    def _build_main_panes(self):
        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        # RX panes
        rx_paned = ttk.Panedwindow(paned, orient=tk.VERTICAL)
        ascii_frm = ttk.Labelframe(rx_paned, text="ASCII")
        self.ascii_area = scrolledtext.ScrolledText(ascii_frm, wrap=tk.NONE, state=tk.DISABLED, font=("Consolas", 10))
        self.ascii_area.tag_configure("tx", foreground="green")
        self.ascii_area.tag_configure("rx", foreground="black")
        ascii_frm.pack_propagate(False)
        self.ascii_area.pack(fill=tk.BOTH, expand=True)
        rx_paned.add(ascii_frm, weight=1)

        hex_frm = ttk.Labelframe(rx_paned, text="HEX")
        self.hex_area = scrolledtext.ScrolledText(hex_frm, wrap=tk.NONE, state=tk.DISABLED, font=("Consolas", 10))
        self.hex_area.tag_configure("tx", foreground="blue")
        self.hex_area.tag_configure("rx", foreground="black")
        self.hex_area.pack(fill=tk.BOTH, expand=True)
        rx_paned.add(hex_frm, weight=1)

        paned.add(rx_paned, weight=3)

        # History list
        hist_frm = ttk.Labelframe(paned, text="Sent History (dbl‑click)")
        self.hist_list = tk.Listbox(hist_frm)
        self.hist_list.pack(fill=tk.BOTH, expand=True)
        self.hist_list.bind("<Double-Button-1>", self._resend_history)
        paned.add(hist_frm, weight=1)

    # ========== Serial helpers ==========
    @staticmethod
    def _list_ports():
        return [p.device for p in serial.tools.list_ports.comports()]

    def toggle_connection(self):
        (self._disconnect if (self.ser and self.ser.is_open) else self._connect)()

    def _connect(self):
        port = self.port_cmb.get()
        if not port:
            messagebox.showwarning("Port", "Select a COM port")
            return
        try:
            self.ser = serial.Serial(port, int(self.baud_cmb.get()), timeout=0.1)
            self.alive.set()
            self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.reader_thread.start()
            self.connect_btn.configure(text="Disconnect")
            for b in (self.send_text_btn, self.send_hex_btn, self.file_btn):
                b.configure(state=tk.NORMAL)
        except serial.SerialException as e:
            messagebox.showerror("Serial", str(e))

    def _disconnect(self):
        self.alive.clear()
        if self.reader_thread:
            self.reader_thread.join(timeout=1)
        if self.ser:
            self.ser.close()
        self.connect_btn.configure(text="Connect")
        for b in (self.send_text_btn, self.send_hex_btn, self.file_btn):
            b.configure(state=tk.DISABLED)

    # ========== RX processing ==========
    def _read_loop(self):
        while self.alive.is_set() and self.ser and self.ser.is_open:
            try:
                data = self.ser.read(self.ser.in_waiting or 1)
                if data:
                    self.rx_queue.put(data)
            except serial.SerialException:
                break
        self.after(0, self._disconnect)

    def _pump_rx(self):
        while not self.rx_queue.empty():
            chunk = self.rx_queue.get_nowait()
            self._append_ascii(chunk, sent=False)
            self._append_hex(chunk, sent=False)
        self.after(100, self._pump_rx)

    # ========== Output helpers ==========
    def _append_ascii(self, data: bytes | str, sent: bool):
        tag = "tx" if sent else "rx"
        text = data if isinstance(data, str) else data.decode(errors="replace")
        self.ascii_area.configure(state=tk.NORMAL)
        self.ascii_area.insert(tk.END, text, (tag,))
        self.ascii_area.see(tk.END)
        self.ascii_area.configure(state=tk.DISABLED)

    def _append_hex(self, data: bytes, sent: bool):
        tag = "tx" if sent else "rx"
        line = " ".join(f"{b:02X}" for b in data) + " \n"
        self.hex_area.configure(state=tk.NORMAL)
        self.hex_area.insert(tk.END, line, (tag,))
        self.hex_area.see(tk.END)
        self.hex_area.configure(state=tk.DISABLED)

    def clear_output(self):
        for area in (self.ascii_area, self.hex_area):
            area.configure(state=tk.NORMAL)
            area.delete(1.0, tk.END)
            area.configure(state=tk.DISABLED)

    # ========== TX methods ==========
    def _send_bytes(self, data: bytes, label: str):
        if not (self.ser and self.ser.is_open):
            messagebox.showwarning("Serial", "Not connected")
            return
        try:
            self.ser.write(data)
            self._append_ascii(f"[Sent] {label}\n", sent=True)
            self._append_hex(data, sent=True)
            self._add_history(label)
        except serial.SerialException as e:
            messagebox.showerror("Serial", str(e))
    
    def send_text(self):
        text = self.tx_entry.get()
        if text:
            self._send_bytes((text + "\r\n").encode(), text)
            self.tx_entry.delete(0, tk.END)

    def send_hex(self):
        raw = self.tx_entry.get()
        data = bytearray(int(m.group(1), 16) for m in self.HEX_RE.finditer(raw))
        if not data:
            messagebox.showinfo("HEX", "Enter hex values like AA 0xBB CC ..")
            return
        self._send_bytes(bytes(data), "HEX: " + " ".join(f"{b:02X}" for b in data))
        self.tx_entry.delete(0, tk.END)

    def send_file(self):
        if not (self.ser and self.ser.is_open):
            messagebox.showwarning("Serial", "Not connected")
            return
        path = filedialog.askopenfilename(filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if not path:
            return
        try:
            content = open(path, "r", encoding="utf-8").read()
        except Exception as e:
            messagebox.showerror("File", str(e))
            return
        data = bytearray(int(m.group(1), 16) for m in self.HEX_RE.finditer(content))
        if not data:
            messagebox.showinfo("HEX", "No valid hex bytes found in file")
            return
        self._send_bytes(bytes(data), f"File {path} ({len(data)} bytes)")

    def _resend_history(self, _):
        sel = self.hist_list.curselection()
        if not sel:
            return
        item = self.hist_list.get(sel[0])
        if item.startswith("HEX:"):
            self.tx_entry.delete(0, tk.END)
            self.tx_entry.insert(0, item[4:].strip())
            self.send_hex()
        else:
            self.tx_entry.delete(0, tk.END)
            self.tx_entry.insert(0, item)
            self.send_text()


if __name__ == "__main__":
    SerialGUI().mainloop()
