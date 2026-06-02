import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import serial
import serial.tools.list_ports
import threading
import queue
import time
import os
import platform
import re

class SerialMonitorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Serial Port Monitor")
        self.geometry("900x700")

        # Cross-platform maximize (no crash on Linux)
        try:
            if platform.system() == "Windows":
                self.state('zoomed')
            else:
                self.attributes('-zoomed', True)
        except tk.TclError:
            # Fallback if WM doesn't support zoomed
            self.geometry("900x700")  # Use default size if zoomed not supported

        # --- Member Variables ---
        self.serial_port = None
        self.read_thread = None
        self.thread_running = False
        self.data_queue = queue.Queue()
        self.command_history = []
        self.history_file = "command_history.txt"

        # --- UI Setup ---
        self.create_widgets()
        self.populate_ports()
        self.load_history()

        # --- Start periodic queue check ---
        self.after(100, self.process_queue)

        # --- Handle window closing ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """Creates and arranges all the GUI widgets."""
        # Configure grid weights for proper resizing
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # --- Connection Frame ---
        conn_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding="10")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        conn_frame.columnconfigure(1, weight=1)
        conn_frame.columnconfigure(3, weight=1)
        conn_frame.columnconfigure(5, weight=1)
        conn_frame.columnconfigure(7, weight=1)
        conn_frame.columnconfigure(9, weight=1)

        # Port
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(conn_frame, textvariable=self.port_var, state="readonly")
        self.port_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)

        self.scan_btn = ttk.Button(conn_frame, text="Scan Ports", command=self.populate_ports)
        self.scan_btn.grid(row=0, column=2, padx=5, pady=2)

        # Baud Rate
        ttk.Label(conn_frame, text="Baud Rate:").grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        self.baud_var = tk.StringVar(value='9600')
        baud_rates = ['300', '1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200', '230400', '460800', '921600']
        self.baud_combo = ttk.Combobox(conn_frame, textvariable=self.baud_var, values=baud_rates, state="readonly")
        self.baud_combo.grid(row=0, column=4, sticky=(tk.W, tk.E), padx=5, pady=2)

        # Data Bits
        ttk.Label(conn_frame, text="Data Bits:").grid(row=0, column=5, sticky=tk.W, padx=5, pady=2)
        self.databits_var = tk.StringVar(value='8')
        databits_values = ['5', '6', '7', '8']
        self.databits_combo = ttk.Combobox(conn_frame, textvariable=self.databits_var, values=databits_values, state="readonly", width=5)
        self.databits_combo.grid(row=0, column=6, sticky=(tk.W, tk.E), padx=5, pady=2)

        # Parity
        ttk.Label(conn_frame, text="Parity:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.parity_var = tk.StringVar(value='N')
        parity_values = ['N', 'E', 'O', 'M', 'S']
        self.parity_combo = ttk.Combobox(conn_frame, textvariable=self.parity_var, values=parity_values, state="readonly", width=5)
        self.parity_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)

        # Stop Bits
        ttk.Label(conn_frame, text="Stop Bits:").grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        self.stopbits_var = tk.StringVar(value='1')
        stopbits_values = ['1', '1.5', '2']
        self.stopbits_combo = ttk.Combobox(conn_frame, textvariable=self.stopbits_var, values=stopbits_values, state="readonly", width=5)
        self.stopbits_combo.grid(row=1, column=4, sticky=(tk.W, tk.E), padx=5, pady=2)

        # Connect/Disconnect buttons
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.connect_serial)
        self.connect_btn.grid(row=1, column=5, padx=5, pady=2)

        self.disconnect_btn = ttk.Button(conn_frame, text="Disconnect", command=self.disconnect_serial, state=tk.DISABLED)
        self.disconnect_btn.grid(row=1, column=6, padx=5, pady=2)

        # --- Data Display ---
        notebook_frame = ttk.Frame(main_frame)
        notebook_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        notebook_frame.columnconfigure(0, weight=1)
        notebook_frame.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.hex_view = scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, font=("Courier New", 10))
        self.ascii_view = scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, font=("Courier New", 10))
        # Terminal-like colors
        self.hex_view.configure(state='disabled', background="#111", foreground="#33FF99", insertbackground="#33FF99")
        self.ascii_view.configure(state='disabled', background="#111", foreground="#D0D0D0", insertbackground="#D0D0D0")

        self.notebook.add(self.hex_view, text='Hex View')
        self.notebook.add(self.ascii_view, text='ASCII View')

        # --- Send Command Frame ---
        send_frame = ttk.LabelFrame(main_frame, text="Send Command", padding="10")
        send_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        send_frame.columnconfigure(0, weight=1)

        self.cmd_var = tk.StringVar()
        self.cmd_combo = ttk.Combobox(send_frame, textvariable=self.cmd_var, font=("Courier New", 10))
        self.cmd_combo.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=2)
        # Enter to send
        self.cmd_combo.bind('<Return>', lambda event: self.send_command())
        # Pick from history -> fill only
        self.cmd_combo.bind("<<ComboboxSelected>>", self.on_history_selected)

        # Frame for send options
        options_frame = ttk.Frame(send_frame)
        options_frame.grid(row=1, column=0, sticky=tk.W, pady=2)

        self.send_format_var = tk.StringVar(value="ASCII")
        ascii_radio = ttk.Radiobutton(options_frame, text="ASCII", variable=self.send_format_var, value="ASCII")
        ascii_radio.pack(side=tk.LEFT, padx=5)
        hex_radio = ttk.Radiobutton(options_frame, text="Hex", variable=self.send_format_var, value="Hex")
        hex_radio.pack(side=tk.LEFT, padx=5)

        self.send_btn = ttk.Button(send_frame, text="Send", command=self.send_command, state=tk.DISABLED)
        self.send_btn.grid(row=1, column=2, padx=5, pady=2, sticky=tk.E)

        # --- Control Frame ---
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=1, sticky=(tk.E, tk.S), padx=5, pady=5)

        self.clear_btn = ttk.Button(control_frame, text="Clear Output", command=self.clear_output)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        self.clear_hist_btn = ttk.Button(control_frame, text="Clear History", command=self.clear_history)
        self.clear_hist_btn.pack(side=tk.LEFT, padx=5)

        # --- Status Bar ---
        self.status_var = tk.StringVar(value="Status: Disconnected")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=5)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))

    # ---------- History ----------
    def load_history(self):
        """Loads command history from a file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    # Keep most-recent-first order as stored
                    self.command_history = [line.rstrip("\n") for line in f if line.strip()]
                self.cmd_combo['values'] = self.command_history
            except IOError as e:
                messagebox.showwarning("History Error", f"Could not load command history:\n{e}")

    def save_history(self):
        """Saves command history to a file."""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                for command in self.command_history:
                    f.write(command + "\n")
        except IOError as e:
            messagebox.showerror("History Error", f"Could not save command history:\n{e}")

    def clear_history(self):
        self.command_history.clear()
        self.cmd_combo['values'] = []
        self.save_history()
        messagebox.showinfo("History", "Command history cleared.")

    def on_history_selected(self, event=None):
        sel = self.cmd_combo.get()
        self.cmd_var.set(sel)

    # ---------- Ports & Connection ----------
    def populate_ports(self):
        """Find and list available serial ports."""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            if self.port_var.get() not in ports:
                self.port_var.set(ports[0])
        else:
            self.port_var.set("")

    def connect_serial(self):
        """Establish the serial connection."""
        port = self.port_var.get()
        try:
            baudrate = int(self.baud_var.get())
            bytesize = int(self.databits_var.get())
            stopbits = float(self.stopbits_var.get())
            parity_map = {'N': serial.PARITY_NONE, 'E': serial.PARITY_EVEN, 
                         'O': serial.PARITY_ODD, 'M': serial.PARITY_MARK, 
                         'S': serial.PARITY_SPACE}
            parity = parity_map[self.parity_var.get()]
        except ValueError:
            messagebox.showerror("Error", "Invalid serial parameters.")
            return

        if not port:
            messagebox.showerror("Error", "No serial port selected.")
            return

        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                timeout=0.1
            )
            time.sleep(0.15)  # small settle time

            if self.serial_port.is_open:
                self.thread_running = True
                self.read_thread = threading.Thread(target=self.read_from_port, daemon=True)
                self.read_thread.start()

                self.connect_btn.config(state=tk.DISABLED)
                self.disconnect_btn.config(state=tk.NORMAL)
                self.send_btn.config(state=tk.NORMAL)
                self.port_combo.config(state=tk.DISABLED)
                self.baud_combo.config(state=tk.DISABLED)
                self.databits_combo.config(state=tk.DISABLED)
                self.parity_combo.config(state=tk.DISABLED)
                self.stopbits_combo.config(state=tk.DISABLED)
                self.scan_btn.config(state=tk.DISABLED)
                self.status_var.set(f"Status: Connected to {port} at {baudrate} baud")
        except serial.SerialException as e:
            messagebox.showerror("Connection Error", f"Failed to connect to {port}:\n{e}")
            self.serial_port = None

    def disconnect_serial(self):
        """Close the serial connection."""
        self.thread_running = False
        if self.read_thread and self.read_thread.is_alive():
            # Let the thread notice thread_running flag
            self.read_thread.join(timeout=0.5)

        if self.serial_port:
            try:
                if self.serial_port.is_open:
                    self.serial_port.close()
            except Exception:
                pass
            self.serial_port = None

        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)
        self.port_combo.config(state="readonly")
        self.baud_combo.config(state="readonly")
        self.databits_combo.config(state="readonly")
        self.parity_combo.config(state="readonly")
        self.stopbits_combo.config(state="readonly")
        self.scan_btn.config(state=tk.NORMAL)
        self.status_var.set("Status: Disconnected")

    # ---------- Serial I/O ----------
    def read_from_port(self):
        """Read data from serial port in a separate thread."""
        while self.thread_running:
            try:
                if self.serial_port and self.serial_port.is_open:
                    n = self.serial_port.in_waiting
                    if n:
                        data = self.serial_port.read(n)
                        if data:
                            self.data_queue.put(('recv', data))
                time.sleep(0.01)  # small delay to prevent high CPU usage
            except serial.SerialException:
                # Device disconnected or error
                self.data_queue.put(('error', None))
                break
            except Exception:
                # Any unexpected error ends the loop safely
                self.data_queue.put(('error', None))
                break

    def send_command(self):
        """Send a command to the serial port based on selected format."""
        if not (self.serial_port and self.serial_port.is_open):
            messagebox.showerror("Send Error", "Not connected.")
            return

        command_str = (self.cmd_var.get() or "").strip()
        if not command_str:
            return

        send_format = self.send_format_var.get()
        try:
            if send_format == "Hex":
                # Accept hex with spaces/commas/0x, e.g., "AA 55, 01" or "0xAA 0x55 0x01"
                clean = re.sub(r'[^0-9A-Fa-f]', '', command_str)
                if not clean or len(clean) % 2 != 0:
                    raise ValueError("Invalid hex length")
                command_bytes = bytes.fromhex(clean)
            else:
                command_bytes = command_str.encode('utf-8')
        except ValueError:
            messagebox.showerror("Invalid Hex", "The input string is not a valid hexadecimal value.")
            return

        try:
            self.serial_port.write(command_bytes)
            self.data_queue.put(('sent', command_bytes))

            # Add to history if new; keep most-recent-first
            if command_str not in self.command_history:
                self.command_history.insert(0, command_str)
                self.cmd_combo['values'] = self.command_history
                self.save_history()  # save immediately
        except serial.SerialException as e:
            messagebox.showerror("Send Error", f"Failed to send data:\n{e}")
            self.disconnect_serial()

    # ---------- UI Update Loop ----------
    def process_queue(self):
        """Periodically check the queue for data from the read thread."""
        try:
            while not self.data_queue.empty():
                msg_type, data = self.data_queue.get_nowait()
                if msg_type == 'error':
                    messagebox.showwarning("Serial Error", "Device disconnected or connection lost.")
                    self.disconnect_serial()
                    break

                direction = ">> " if msg_type == 'sent' else "<< "
                self.update_display(direction, data)
        except queue.Empty:
            pass  # Queue is empty, which is fine
        finally:
            self.after(100, self.process_queue)

    def update_display(self, direction, data: bytes):
        """Update the Hex and ASCII text widgets."""
        if not data:
            return

        # Hex View
        hex_data = ' '.join(f'{b:02X}' for b in data)
        self.hex_view.configure(state='normal')
        self.hex_view.insert(tk.END, f"{direction}{hex_data}\n")
        self.hex_view.configure(state='disabled')
        self.hex_view.yview(tk.END)  # Auto-scroll

        # ASCII View (non-printables shown as '.')
        ascii_data = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data)
        self.ascii_view.configure(state='normal')
        self.ascii_view.insert(tk.END, f"{direction}{ascii_data}\n")
        self.ascii_view.configure(state='disabled')
        self.ascii_view.yview(tk.END)  # Auto-scroll

    # ---------- Utilities ----------
    def clear_output(self):
        """Clear the content of both display tabs."""
        for widget in (self.hex_view, self.ascii_view):
            widget.configure(state='normal')
            widget.delete('1.0', tk.END)
            widget.configure(state='disabled')

    def on_closing(self):
        """Handle window close event."""
        try:
            self.save_history()
        finally:
            try:
                self.disconnect_serial()
            except Exception:
                pass
            self.destroy()

if __name__ == "__main__":
    app = SerialMonitorApp()
    app.mainloop()
