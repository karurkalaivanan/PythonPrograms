import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import serial
import serial.tools.list_ports
import threading
import csv
from datetime import datetime

class SerialMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Serial Monitor")
        self.geometry("1000x750")
        self.minsize(800, 600)
        
        # Configure style
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except:
            pass  # Fall back to default theme if 'clam' is not available
        
        self.configure(bg='#2e2e2e')
        
        # Variables
        self.ser = None
        self.stop_thread = False
        self.connected = False
        self.received_bytes = 0
        self.sent_bytes = 0
        self.line_endings = {"None": "", "LF (\\n)": "\n", "CR (\\r)": "\r", "CR+LF (\\r\\n)": "\r\n"}
        self.current_line_ending = "\n"
        
        # Setup the UI
        self.setup_ui()
        
        # Start periodic port check
        self.after(1000, self.check_ports)
        
    def setup_ui(self):
        # Create main paned window for resizable panels
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for controls and history
        left_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=1)
        
        # Right panel for terminal
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=3)
        
        # Setup left panel content
        self.setup_left_panel(left_frame)
        
        # Setup right panel content
        self.setup_right_panel(right_frame)
        
        # Setup status bar
        self.setup_status_bar()
        
    def setup_left_panel(self, parent):
        # Connection frame
        conn_frame = ttk.LabelFrame(parent, text="Connection Settings", padding=10)
        conn_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Port selection
        port_frame = ttk.Frame(conn_frame)
        port_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(port_frame, text="Port:").pack(side=tk.LEFT, padx=(0, 5))
        self.port_combo = ttk.Combobox(port_frame, values=self.get_ports(), width=20)
        self.port_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.refresh_btn = ttk.Button(port_frame, text="Refresh", command=self.refresh_ports, width=8)
        self.refresh_btn.pack(side=tk.RIGHT)
        
        # Baud rate and connection settings
        settings_frame = ttk.Frame(conn_frame)
        settings_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(settings_frame, text="Baudrate:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.baud_combo = ttk.Combobox(settings_frame, values=["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"], width=12)
        self.baud_combo.set("115200")
        self.baud_combo.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(settings_frame, text="Line Ending:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.line_ending_combo = ttk.Combobox(settings_frame, values=list(self.line_endings.keys()), width=12)
        self.line_ending_combo.set("LF (\\n)")
        self.line_ending_combo.grid(row=0, column=3)
        self.line_ending_combo.bind("<<ComboboxSelected>>", self.on_line_ending_change)
        
        # Connection buttons
        btn_frame = ttk.Frame(conn_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.connect_btn = ttk.Button(btn_frame, text="Connect", command=self.connect_serial)
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.disconnect_btn = ttk.Button(btn_frame, text="Disconnect", command=self.disconnect_serial, state="disabled")
        self.disconnect_btn.pack(side=tk.LEFT)
        
        # Display options
        options_frame = ttk.Frame(conn_frame)
        options_frame.pack(fill=tk.X, pady=5)
        
        self.timestamp_var = tk.BooleanVar()
        self.timestamp_chk = ttk.Checkbutton(options_frame, text="Timestamps", variable=self.timestamp_var)
        self.timestamp_chk.pack(side=tk.LEFT, padx=(0, 10))
        
        self.autoscroll_var = tk.BooleanVar(value=True)
        self.autoscroll_chk = ttk.Checkbutton(options_frame, text="Auto-scroll", variable=self.autoscroll_var)
        self.autoscroll_chk.pack(side=tk.LEFT)
        
        # Command frame
        cmd_frame = ttk.LabelFrame(parent, text="Send Command", padding=10)
        cmd_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.entry_box = ttk.Entry(cmd_frame, font=("Consolas", 10))
        self.entry_box.pack(fill=tk.X, pady=(0, 5))
        self.entry_box.bind("<Return>", self.send_command)
        
        send_btn_frame = ttk.Frame(cmd_frame)
        send_btn_frame.pack(fill=tk.X)
        
        self.send_btn = ttk.Button(send_btn_frame, text="Send", command=self.send_command)
        self.send_btn.pack(side=tk.RIGHT)
        
        # History frame
        history_frame = ttk.LabelFrame(parent, text="Command History", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # Button frame for history controls
        history_btn_frame = ttk.Frame(history_frame)
        history_btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.load_btn = ttk.Button(history_btn_frame, text="Load", command=self.load_commands)
        self.load_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_btn = ttk.Button(history_btn_frame, text="Save", command=self.save_history)
        self.save_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_btn = ttk.Button(history_btn_frame, text="Clear", command=self.clear_history)
        self.clear_btn.pack(side=tk.LEFT)
        
        # History list with scrollbar
        list_frame = ttk.Frame(history_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.cmd_list = tk.Listbox(list_frame, bg="white", font=("Consolas", 9), 
                                  selectbackground="#4a7abc", selectforeground="white")
        self.cmd_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.cmd_list.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cmd_list.configure(yscrollcommand=list_scrollbar.set)
        
        self.cmd_list.bind("<Double-1>", self.send_from_history)
        self.cmd_list.bind("<Delete>", self.delete_history_item)
        
    def setup_right_panel(self, parent):
        # Terminal frame
        terminal_frame = ttk.LabelFrame(parent, text="Serial Monitor", padding=10)
        terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        # Terminal controls
        term_ctrl_frame = ttk.Frame(terminal_frame)
        term_ctrl_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(term_ctrl_frame, text="Font Size:").pack(side=tk.LEFT, padx=(0, 5))
        self.font_size = tk.IntVar(value=10)
        
        # Use tk.Spinbox instead of ttk.Spinbox
        font_spinbox = tk.Spinbox(term_ctrl_frame, from_=8, to=24, width=5, textvariable=self.font_size,
                                 command=self.change_font_size)
        font_spinbox.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_btn = ttk.Button(term_ctrl_frame, text="Clear Output", command=self.clear_output)
        self.clear_btn.pack(side=tk.RIGHT)
        
        # Terminal output
        self.output_box = scrolledtext.ScrolledText(terminal_frame, wrap=tk.WORD, state="disabled", 
                                                  bg="#252525", fg="#e0e0e0", font=("Consolas", 10),
                                                  insertbackground="white", padx=10, pady=10)
        self.output_box.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for colored text
        self.output_box.tag_config("timestamp", foreground="#888888")
        self.output_box.tag_config("send", foreground="#4a9cf9")
        self.output_box.tag_config("receive", foreground="#e0e0e0")
        self.output_box.tag_config("error", foreground="#ff5555")
        self.output_box.tag_config("info", foreground="#55ff55")
        
    def setup_status_bar(self):
        status_frame = ttk.Frame(self, relief=tk.SUNKEN)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_connection = ttk.Label(status_frame, text="Disconnected", anchor=tk.W)
        self.status_connection.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.status_stats = ttk.Label(status_frame, text="Received: 0 bytes | Sent: 0 bytes", anchor=tk.W)
        self.status_stats.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.status_port = ttk.Label(status_frame, text="Port: None", anchor=tk.W)
        self.status_port.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.status_baud = ttk.Label(status_frame, text="Baud: None", anchor=tk.W)
        self.status_baud.pack(side=tk.RIGHT, padx=5, pady=2)
        
    def change_font_size(self):
        new_size = self.font_size.get()
        self.output_box.config(font=("Consolas", new_size))
        
    def on_line_ending_change(self, event):
        selected = self.line_ending_combo.get()
        self.current_line_ending = self.line_endings[selected]
        
    def check_ports(self):
        if not self.connected:
            current_port = self.port_combo.get()
            available_ports = self.get_ports()
            self.port_combo['values'] = available_ports
            
            # If the current port is no longer available, clear the selection
            if current_port and current_port not in available_ports:
                self.port_combo.set('')
                
        self.after(1000, self.check_ports)
        
    def get_ports(self):
        return [p.device for p in serial.tools.list_ports.comports()]

    def refresh_ports(self):
        ports = self.get_ports()
        self.port_combo['values'] = ports
        if ports and not self.port_combo.get():
            self.port_combo.set(ports[0])
        self.update_status("Ports refreshed")

    def update_status(self, message):
        self.status_connection.config(text=message)
        
    def update_stats(self):
        self.status_stats.config(text=f"Received: {self.received_bytes} bytes | Sent: {self.sent_bytes} bytes")

    def clear_output(self):
        self.output_box.config(state="normal")
        self.output_box.delete(1.0, tk.END)
        self.output_box.config(state="disabled")
        self.update_status("Output cleared")

    def connect_serial(self):
        port = self.port_combo.get()
        baud = self.baud_combo.get()
        
        if not port:
            messagebox.showerror("Error", "Please select a serial port")
            return
            
        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=int(baud),
                timeout=1
            )
            self.stop_thread = False
            self.connected = True
            threading.Thread(target=self.read_serial, daemon=True).start()
            
            # Update UI states
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")
            self.port_combo.config(state="disabled")
            self.baud_combo.config(state="disabled")
            self.refresh_btn.config(state="disabled")
            
            # Set focus to command entry
            self.entry_box.focus()
            
            # Update status
            self.update_status(f"Connected to {port}")
            self.status_port.config(text=f"Port: {port}")
            self.status_baud.config(text=f"Baud: {baud}")
            
            # Log connection
            self.log_output(f"Connected to {port} at {baud} baud\n", "info")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open port: {e}")
            self.update_status(f"Connection failed: {e}")

    def disconnect_serial(self):
        if self.ser and self.ser.is_open:
            self.stop_thread = True
            self.connected = False
            self.ser.close()
            
            # Update UI states
            self.connect_btn.config(state="normal")
            self.disconnect_btn.config(state="disabled")
            self.port_combo.config(state="readonly")
            self.baud_combo.config(state="readonly")
            self.refresh_btn.config(state="normal")
            
            # Update status
            self.update_status("Disconnected")
            self.status_port.config(text="Port: None")
            self.status_baud.config(text="Baud: None")
            
            # Log disconnection
            self.log_output("Disconnected\n", "info")

    def read_serial(self):
        while not self.stop_thread and self.ser and self.ser.is_open:
            try:
                # Read all available data
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting).decode(errors="ignore")
                    if data:
                        self.received_bytes += len(data)
                        self.log_output(data, "receive")
                        self.update_stats()
            except Exception as e:
                if not self.stop_thread:
                    self.log_output(f"Read error: {e}\n", "error")
                break

    def log_output(self, text, msg_type="receive"):
        self.output_box.config(state="normal")
        
        # Add timestamp if enabled
        if self.timestamp_var.get():
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            self.output_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add the actual text with appropriate formatting
        self.output_box.insert(tk.END, text, msg_type)
        
        # Auto-scroll if enabled
        if self.autoscroll_var.get():
            self.output_box.see(tk.END)
            
        self.output_box.config(state="disabled")

    def send_command(self, event=None):
        cmd = self.entry_box.get().strip()
        if cmd:
            if self.ser and self.ser.is_open:
                full_cmd = cmd + self.current_line_ending
                try:
                    self.ser.write(full_cmd.encode())
                    self.sent_bytes += len(full_cmd)
                    self.update_stats()
                    
                    # Add to history if not duplicate of last command
                    if not self.cmd_list.size() or self.cmd_list.get(self.cmd_list.size()-1) != cmd:
                        self.cmd_list.insert(tk.END, cmd)
                    
                    # Log the sent command
                    # self.log_output(f"{cmd}{self.current_line_ending}", "send")
                    
                    self.update_status(f"Sent: {cmd}")
                except Exception as e:
                    self.log_output(f"Send error: {e}\n", "error")
                    self.update_status(f"Send failed: {e}")
        elif self.ser and self.ser.is_open:
            # Send just the line ending if input is empty
            try:
                self.ser.write(self.current_line_ending.encode())
                self.sent_bytes += len(self.current_line_ending)
                self.update_stats()
                self.log_output(self.current_line_ending, "send")
            except Exception as e:
                self.log_output(f"Send error: {e}\n", "error")
                
        self.entry_box.delete(0, tk.END)

    def send_from_history(self, event):
        selection = self.cmd_list.curselection()
        if selection:
            cmd = self.cmd_list.get(selection[0]).strip()
            if cmd and self.ser and self.ser.is_open:
                full_cmd = cmd + self.current_line_ending
                try:
                    self.ser.write(full_cmd.encode())
                    self.sent_bytes += len(full_cmd)
                    self.update_stats()
                    # self.log_output(f"{cmd}{self.current_line_ending}", "send")
                    self.update_status(f"Sent from history: {cmd}")
                except Exception as e:
                    self.log_output(f"Send error: {e}\n", "error")

    def delete_history_item(self, event):
        selection = self.cmd_list.curselection()
        if selection:
            self.cmd_list.delete(selection[0])

    def clear_history(self):
        self.cmd_list.delete(0, tk.END)
        self.update_status("History cleared")

    def load_commands(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not file_path:
            return
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.endswith(".csv"):
                    reader = csv.reader(f)
                    for row in reader:
                        if row:
                            self.cmd_list.insert(tk.END, row[0].strip())
                else:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):  # Skip comment lines
                            self.cmd_list.insert(tk.END, line)
                            
            self.log_output(f"Loaded commands from {file_path}\n", "info")
            self.update_status(f"Commands loaded from {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")
            self.update_status(f"Load error: {e}")

    def save_history(self):
        if not self.cmd_list.size():
            messagebox.showinfo("Info", "No commands in history to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not file_path:
            return
            
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                if file_path.endswith(".csv"):
                    writer = csv.writer(f)
                    for i in range(self.cmd_list.size()):
                        writer.writerow([self.cmd_list.get(i)])
                else:
                    for i in range(self.cmd_list.size()):
                        f.write(self.cmd_list.get(i) + "\n")
                        
            self.log_output(f"Saved command history to {file_path}\n", "info")
            self.update_status(f"History saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")
            self.update_status(f"Save error: {e}")


if __name__ == "__main__":
    app = SerialMonitor()
    app.mainloop()
