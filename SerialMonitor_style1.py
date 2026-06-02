#!/usr/bin/env python3
# serial_monitor.py
# Created by NewWayLabs
# Simple serial port monitor GUI
# Requires: pip install pyserial

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import queue
import time
import binascii
import serial
import serial.tools.list_ports
import sys


class SerialMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Serial Monitor")
        self.geometry("900x600")

        # Serial state
        self.ser = None
        self.alive = threading.Event()
        self.reader_thread = None
        self.rx_queue = queue.Queue()

        # Logging
        self.log_file = None

        self._build_ui()
        self.after(200, self._process_rx_queue)

    def _build_ui(self):
        # Top frame for controls
        frame = ttk.Frame(self)
        frame.pack(side=tk.TOP, fill=tk.X, padx=6, pady=6)

        # Port list
        ttk.Label(frame, text="Port:").grid(row=0, column=0, sticky=tk.W)
        self.port_cb = ttk.Combobox(frame, width=12, values=self._list_ports())
        self.port_cb.grid(row=0, column=1, padx=4)
        refresh_btn = ttk.Button(frame, text="Refresh", command=self._refresh_ports)
        refresh_btn.grid(row=0, column=2, padx=4)

        # Baudrate
        ttk.Label(frame, text="Baud:").grid(row=0, column=3, sticky=tk.W)
        self.baud_cb = ttk.Combobox(frame, width=8, values=[
            "115200","57600","38400","19200","9600","4800","2400","1200"],)
        self.baud_cb.set("115200")
        self.baud_cb.grid(row=0, column=4, padx=4)

        # Open/Close
        self.open_btn = ttk.Button(frame, text="Open", command=self.toggle_open)
        self.open_btn.grid(row=0, column=5, padx=8)

        # Hex view, timestamp
        self.hex_view_var = tk.BooleanVar(value=False)
        self.hex_view_cb = ttk.Checkbutton(frame, text="Hex view", variable=self.hex_view_var)
        self.hex_view_cb.grid(row=0, column=6, padx=4)

        self.timestamp_var = tk.BooleanVar(value=False)
        self.timestamp_cb = ttk.Checkbutton(frame, text="Timestamps", variable=self.timestamp_var)
        self.timestamp_cb.grid(row=0, column=7, padx=4)

        # Text area for incoming data
        self.text = ScrolledText(self, wrap=tk.NONE, state=tk.NORMAL)
        self.text.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.text.tag_config("rx", foreground="black")
        self.text.tag_config("tx", foreground="blue")
        self.text.tag_config("err", foreground="red")

        # Bottom frame for send controls
        bottom = ttk.Frame(self)
        bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=6)

        ttk.Label(bottom, text="Send:").grid(row=0, column=0, sticky=tk.W)
        self.send_entry = ttk.Entry(bottom, width=60)
        self.send_entry.grid(row=0, column=1, padx=4, sticky=tk.W+tk.E)

        self.send_hex_var = tk.BooleanVar(value=False)
        self.send_hex_cb = ttk.Checkbutton(bottom, text="Send as hex", variable=self.send_hex_var)
        self.send_hex_cb.grid(row=0, column=2, padx=4)

        self.nl_option = tk.StringVar(value="None")
        ttk.Combobox(bottom, width=8, textvariable=self.nl_option,
                     values=["None", "CR", "LF", "CRLF"]).grid(row=0, column=3, padx=4)

        send_btn = ttk.Button(bottom, text="Send", command=self.send)
        send_btn.grid(row=0, column=4, padx=4)

        clear_btn = ttk.Button(bottom, text="Clear", command=self.clear)
        clear_btn.grid(row=0, column=5, padx=4)

        log_btn = ttk.Button(bottom, text="Log to file", command=self.toggle_log)
        log_btn.grid(row=0, column=6, padx=4)

        # Status bar
        self.status = ttk.Label(self, text="Closed", relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def _list_ports(self):
        ports = []
        for p in serial.tools.list_ports.comports():
            ports.append(p.device)
        return ports

    def _refresh_ports(self):
        values = self._list_ports()
        self.port_cb['values'] = values
        if values:
            # leave current selection if present, otherwise select first
            cur = self.port_cb.get()
            if cur not in values:
                self.port_cb.set(values[0])

    def toggle_open(self):
        if self.ser and self.ser.is_open:
            self._close_serial()
        else:
            self._open_serial()

    def _open_serial(self):
        port = self.port_cb.get()
        if not port:
            messagebox.showwarning("No port", "Please select a serial port.")
            return
        try:
            baud = int(self.baud_cb.get())
        except Exception:
            messagebox.showwarning("Bad baud", "Please enter a valid baud rate.")
            return
        try:
            self.ser = serial.Serial(port, baudrate=baud, timeout=0.1)
        except Exception as e:
            messagebox.showerror("Open failed", f"Failed to open {port}:\n{e}")
            self.ser = None
            return

        self.alive.set()
        self.reader_thread = threading.Thread(target=self._reader, daemon=True)
        self.reader_thread.start()
        self.open_btn.config(text="Close")
        self.status.config(text=f"Open: {port} @ {baud}")
        self._append_text(f"Opened {port} at {baud}\n", "rx")

    def _close_serial(self):
        self.alive.clear()
        if self.reader_thread:
            self.reader_thread.join(timeout=1.0)
        try:
            if self.ser:
                self.ser.close()
        except Exception:
            pass
        self.ser = None
        self.open_btn.config(text="Open")
        self.status.config(text="Closed")
        self._append_text("Closed serial port\n", "rx")

    def _reader(self):
        # background thread: read from serial and put into queue
        try:
            while self.alive.is_set() and self.ser and self.ser.is_open:
                try:
                    data = self.ser.read(1024)
                    if data:
                        # put bytes into queue
                        self.rx_queue.put(data)
                    else:
                        # small sleep to yield CPU
                        time.sleep(0.01)
                except Exception as e:
                    # put exception marker and break
                    self.rx_queue.put(e)
                    break
        finally:
            # signal closure
            self.alive.clear()

    def _process_rx_queue(self):
        try:
            while True:
                item = self.rx_queue.get_nowait()
                if isinstance(item, Exception):
                    self._append_text(f"Read error: {item}\n", "err")
                    self._close_serial()
                    break
                else:
                    self._handle_incoming_bytes(item)
        except queue.Empty:
            pass
        # schedule next check
        self.after(100, self._process_rx_queue)

    def _handle_incoming_bytes(self, data: bytes):
        if self.hex_view_var.get():
            # show as hex pairs
            hexstr = binascii.hexlify(data).decode('ascii')
            # group into bytes
            grouped = ' '.join(hexstr[i:i+2] for i in range(0, len(hexstr), 2))
            line = grouped + '\n'
        else:
            try:
                line = data.decode('utf-8', errors='replace')
            except Exception:
                line = repr(data)
        prefix = ""
        if self.timestamp_var.get():
            prefix = time.strftime("[%H:%M:%S] ")
        self._append_text(prefix + line, "rx")
        # write to log if enabled
        if self.log_file:
            try:
                # always write bytes in hex if hex view, else text as-is
                if self.hex_view_var.get():
                    self.log_file.write((prefix + line).encode('utf-8'))
                else:
                    # ensure string
                    self.log_file.write((prefix + line).encode('utf-8'))
                self.log_file.flush()
            except Exception:
                pass

    def _append_text(self, s, tag=None):
        self.text.configure(state=tk.NORMAL)
        if tag:
            self.text.insert(tk.END, s, tag)
        else:
            self.text.insert(tk.END, s)
        self.text.see(tk.END)
        # limit buffer ~ 100k chars
        max_chars = 200000
        if int(self.text.index('end-1c').split('.')[0]) > max_chars:
            self.text.delete('1.0', '1000.0')
        self.text.configure(state=tk.DISABLED)

    def send(self):
        if not (self.ser and self.ser.is_open):
            messagebox.showwarning("Not open", "Serial port is not open.")
            return
        txt = self.send_entry.get()
        if txt is None:
            return
        tosend = b''
        if self.send_hex_var.get():
            # interpret hex string e.g. "01 02 0A"
            try:
                hexstr = txt.replace(" ", "").replace(",", "")
                if len(hexstr) % 2 != 0:
                    hexstr = "0" + hexstr
                tosend = binascii.unhexlify(hexstr)
            except Exception as e:
                messagebox.showerror("Bad hex", f"Cannot parse hex string:\n{e}")
                return
        else:
            try:
                tosend = txt.encode('utf-8')
            except Exception:
                tosend = txt.encode('latin-1', errors='replace')
        # newline options
        nl = self.nl_option.get()
        if nl == "CR":
            tosend += b'\r'
        elif nl == "LF":
            tosend += b'\n'
        elif nl == "CRLF":
            tosend += b'\r\n'

        try:
            n = self.ser.write(tosend)
            # show sent in UI
            display = ""
            if self.send_hex_var.get():
                display = ' '.join(f"{b:02X}" for b in tosend)
            else:
                try:
                    display = tosend.decode('utf-8', errors='replace')
                except Exception:
                    display = repr(tosend)
            prefix = time.strftime("[%H:%M:%S] ") if self.timestamp_var.get() else ""
            self._append_text(prefix + display + '\n', "tx")
            # optionally also log sent data
            if self.log_file:
                try:
                    self.log_file.write((prefix + display + '\n').encode('utf-8'))
                    self.log_file.flush()
                except Exception:
                    pass
        except Exception as e:
            messagebox.showerror("Send failed", str(e))

    def clear(self):
        self.text.configure(state=tk.NORMAL)
        self.text.delete('1.0', tk.END)
        self.text.configure(state=tk.DISABLED)

    def toggle_log(self):
        if self.log_file:
            try:
                self.log_file.close()
            except Exception:
                pass
            self.log_file = None
            self.status.config(text=self.status.cget("text").split(" | ")[0])
            messagebox.showinfo("Logging", "Stopped logging.")
        else:
            f = filedialog.asksaveasfilename(title="Select log file", defaultextension=".log")
            if f:
                try:
                    self.log_file = open(f, "ab")
                    self.status.config(text=(self.status.cget("text") + " | Logging"))
                    messagebox.showinfo("Logging", f"Logging to {f}")
                except Exception as e:
                    messagebox.showerror("Log failed", f"Cannot open log file:\n{e}")
                    self.log_file = None

    def on_closing(self):
        if self.ser and self.ser.is_open:
            self._close_serial()
        if self.log_file:
            try:
                self.log_file.close()
            except Exception:
                pass
        self.destroy()

if __name__ == "__main__":
    app = SerialMonitor()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()