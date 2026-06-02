import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import serial
import serial.tools.list_ports
import threading
import csv

class SerialMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python Serial Monitor (Like Putty/TeraTerm)")
        self.geometry("800x600")

        self.ser = None
        self.stop_thread = False

        # ---- Serial Port Controls ----
        control_frame = tk.Frame(self)
        control_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(control_frame, text="Port:").pack(side="left")
        self.port_combo = ttk.Combobox(control_frame, values=self.get_ports(), width=15)
        self.port_combo.pack(side="left", padx=5)

        tk.Label(control_frame, text="Baudrate:").pack(side="left")
        self.baud_combo = ttk.Combobox(control_frame, values=["9600","19200","38400","57600","115200"], width=10)
        self.baud_combo.set("115200")
        self.baud_combo.pack(side="left", padx=5)

        self.connect_btn = tk.Button(control_frame, text="Connect", command=self.connect_serial)
        self.connect_btn.pack(side="left", padx=5)

        self.disconnect_btn = tk.Button(control_frame, text="Disconnect", command=self.disconnect_serial, state="disabled")
        self.disconnect_btn.pack(side="left", padx=5)

        # ---- Terminal Display ----
        self.output_box = scrolledtext.ScrolledText(self, height=20, state="disabled", bg="black", fg="lime")
        self.output_box.pack(fill="both", expand=True, padx=5, pady=5)

        # ---- Command Entry ----
        entry_frame = tk.Frame(self)
        entry_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(entry_frame, text="Command:").pack(side="left")
        self.entry_box = tk.Text(entry_frame, height=1, width=60)
        self.entry_box.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_box.bind("<Return>", self.send_command)  # Enter key default send

        # ---- Command History ----
        history_frame = tk.Frame(self)
        history_frame.pack(fill="both", expand=True, padx=5, pady=5)

        tk.Label(history_frame, text="Command History:").pack(anchor="w")

        btn_frame = tk.Frame(history_frame)
        btn_frame.pack(fill="x", pady=2)

        self.load_btn = tk.Button(btn_frame, text="Load Commands", command=self.load_commands)
        self.load_btn.pack(side="left", padx=5)

        self.cmd_list = tk.Listbox(history_frame, height=10)
        self.cmd_list.pack(fill="both", expand=True)
        self.cmd_list.bind("<Double-1>", self.send_from_history)

    def get_ports(self):
        return [p.device for p in serial.tools.list_ports.comports()]

    def connect_serial(self):
        try:
            self.ser = serial.Serial(
                self.port_combo.get(),
                int(self.baud_combo.get()),
                timeout=1
            )
            self.stop_thread = False
            threading.Thread(target=self.read_serial, daemon=True).start()
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")
            self.log_output(f"Connected to {self.port_combo.get()} at {self.baud_combo.get()} baud\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open port: {e}")

    def disconnect_serial(self):
        if self.ser and self.ser.is_open:
            self.stop_thread = True
            self.ser.close()
            self.connect_btn.config(state="normal")
            self.disconnect_btn.config(state="disabled")
            self.log_output("Disconnected.\n")

    def read_serial(self):
        while not self.stop_thread and self.ser and self.ser.is_open:
            try:
                data = self.ser.readline().decode(errors="ignore")
                if data:
                    self.log_output(data)
            except:
                break

    def log_output(self, text):
        self.output_box.config(state="normal")
        self.output_box.insert(tk.END, text)
        self.output_box.see(tk.END)
        self.output_box.config(state="disabled")

    def send_command(self, event=None):
        cmd = self.entry_box.get("1.0", "end-1c")
        if cmd.strip():  # user typed something
            if self.ser and self.ser.is_open:
                self.ser.write((cmd + "\n").encode())
                self.cmd_list.insert(tk.END, cmd)  # add to history
        else:  # only Enter pressed → send linefeed
            if self.ser and self.ser.is_open:
                self.ser.write(b"\n")
        self.entry_box.delete("1.0", tk.END)
        return "break"   # stop Tkinter from inserting newline


    def send_from_history(self, event):
        selection = self.cmd_list.curselection()
        if selection:
            cmd = self.cmd_list.get(selection[0]).strip()
            if cmd and self.ser and self.ser.is_open:  # ✅ check not empty
                self.ser.write((cmd + "\n").encode())


    def load_commands(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text/CSV Files", "*.txt *.csv")])
        if not file_path:
            return
        try:
            with open(file_path, "r", newline="", encoding="utf-8") as f:
                if file_path.endswith(".csv"):
                    reader = csv.reader(f)
                    for row in reader:
                        if row:
                            self.cmd_list.insert(tk.END, row[0].strip())
                else:  # txt file
                    for line in f:
                        line = line.strip()
                        if line:
                            self.cmd_list.insert(tk.END, line)
            self.log_output(f"Loaded commands from {file_path}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")


if __name__ == "__main__":
    app = SerialMonitor()
    app.mainloop()
