import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import serial
import serial.tools.list_ports
import threading
import json
import os

HISTORY_FILE = "command_history.json"

def list_serial_ports():
    return [port.device for port in serial.tools.list_ports.comports()]

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return []  # Handle corrupted JSON file
    return []

def save_history(history):
    history = list(set(history))  # Remove duplicates
    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file)

def clear_history(self):
    self.sent_commands = []  # Reset in memory
    save_history(self.sent_commands)  # Clear from JSON file
    self.history_combobox["values"] = []  # Clear dropdown
    messagebox.showinfo("History Cleared", "Command history has been cleared.")

class SerialMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Port Monitor")
        self.root.state('zoomed')

        self.serial_connection = None
        self.is_monitoring = False
        self.sent_commands = load_history()

        self.create_menu()

        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

        # Port selection
        frame = ttk.Frame(root)
        frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Port:").grid(row=0, column=0, padx=5, pady=5)
        self.port_var = tk.StringVar()
        self.port_combobox = ttk.Combobox(frame, textvariable=self.port_var, values=list_serial_ports(), width=15)
        self.port_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.port_combobox.bind("<Button-1>", self.refresh_ports)  # Auto-refresh ports on click

        ttk.Label(frame, text="Baud Rate:").grid(row=0, column=2, padx=5, pady=5)
        self.baud_var = tk.StringVar(value="9600")
        self.baud_combobox = ttk.Combobox(frame, textvariable=self.baud_var, values=["9600", "115200", "57600", "38400", "19200", "4800", "2400"], width=10)
        self.baud_combobox.grid(row=0, column=3, padx=5, pady=5)

        # Buttons
        self.connect_button = ttk.Button(frame, text="Connect", command=self.connect_serial)
        self.connect_button.grid(row=0, column=4, padx=5, pady=5)

        self.disconnect_button = ttk.Button(frame, text="Disconnect", command=self.disconnect_serial, state=tk.DISABLED)
        self.disconnect_button.grid(row=0, column=5, padx=5, pady=5)

        # Scrolled Text for Serial Output
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.text_area.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Send Command Section
        send_frame = ttk.Frame(root)
        send_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        send_frame.columnconfigure(1, weight=1)

        ttk.Label(send_frame, text="Send:").grid(row=0, column=0, padx=5, pady=5)
        self.send_entry = ttk.Entry(send_frame, width=50)
        self.send_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.send_entry.bind("<Return>", self.send_serial_event)

        self.format_var = tk.StringVar(value="ASCII")
        self.format_combobox = ttk.Combobox(send_frame, textvariable=self.format_var, values=["ASCII", "HEX"], width=10)
        self.format_combobox.grid(row=0, column=2, padx=5, pady=5)

        self.send_button = ttk.Button(send_frame, text="Send", command=self.send_serial)
        self.send_button.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(send_frame, text="History:").grid(row=1, column=0, padx=5, pady=5)
        self.history_combobox = ttk.Combobox(send_frame, values=self.sent_commands, width=50)
        self.history_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.history_combobox.bind("<<ComboboxSelected>>", self.fill_send_entry)

    def refresh_ports(self, event=None):
        """ Refresh available serial ports dynamically """
        self.port_combobox["values"] = list_serial_ports()

    def fill_send_entry(self, event):
        """Fill the send entry with selected history command and send automatically."""
        selected_command = self.history_combobox.get()
        if selected_command:
            self.send_entry.delete(0, tk.END)
            self.send_entry.insert(0, selected_command)
            self.send_serial()  # Automatically send the command

    def send_serial_event(self, event):
        self.send_serial()

    def send_serial(self):
        if self.serial_connection and self.serial_connection.is_open:
            data = self.send_entry.get()
            if self.format_var.get() == "HEX":
                try:
                    data = bytes.fromhex(data)
                except ValueError:
                    messagebox.showerror("Error", "Invalid HEX input")
                    return
            else:
                data = data.encode()

            self.serial_connection.write(data)
            if data.decode() not in self.sent_commands:
                self.sent_commands.append(self.send_entry.get())
                save_history(self.sent_commands)

        else:
            messagebox.showerror("Error", "Serial port not connected")

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Clear Output", command=self.clear_output)
        menubar.add_cascade(label="Edit", menu=edit_menu)

    def clear_output(self):
        self.text_area.delete('1.0', tk.END)

    def connect_serial(self):
        port = self.port_var.get()
        baud = self.baud_var.get()

        if not port:
            messagebox.showerror("Error", "Please select a serial port.")
            return

        try:
            self.serial_connection = serial.Serial(port, baudrate=int(baud), timeout=1)
            self.is_monitoring = True
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            self.monitor_thread = threading.Thread(target=self.read_serial, daemon=True)
            self.monitor_thread.start()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def disconnect_serial(self):
        if self.serial_connection:
            self.is_monitoring = False
            self.serial_connection.close()
            self.serial_connection = None
            self.connect_button.config(state=tk.NORMAL)
            self.disconnect_button.config(state=tk.DISABLED)

    def read_serial(self):
        while self.is_monitoring:
            try:
                if self.serial_connection and self.serial_connection.in_waiting:
                    data = self.serial_connection.read_until(b'\n').strip()
                    if data:
                        ascii_data = data.decode(errors='ignore')
                        hex_data = ' '.join(f'{b:02X}' for b in data)
                        self.text_area.insert(tk.END, f"ASCII: {ascii_data}\nHEX: {hex_data}\n")
                        self.text_area.see(tk.END)
            except Exception as e:
                self.text_area.insert(tk.END, f"Error: {str(e)}\n")
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialMonitor(root)
    root.mainloop()
