import serial
import time
import tkinter as tk
from tkinter import ttk
import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque

# Define the COM port
COM_PORT = "COM12"

# Modbus RTU command for the water meter
modbus_commands = {
    "07": bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x0A, 0xC5, 0xCD])
}

# Serial port settings
baud_rate = 9600
timeout = 0.5

# Try to open COM port
try:
    ser = serial.Serial(COM_PORT, baud_rate, timeout=timeout)
    print(f"Opened {COM_PORT}")
except Exception as e:
    print(f"Failed to open {COM_PORT}: {e}")
    ser = None

# CSV file setup
CSV_FILE = f"E:\watermeter_zeven_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# Check if the file exists, if not, create it with headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Device ID", "Liters (L)", "Flowrate (m³/h)"])  # CSV Header

# Function to log session start
def add_session_header():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([f"Session Started: {timestamp}", "", "", ""])

# Function to parse water meter readings
def watermeter_parsing(meter_reading):
    START_PATTERNS = ["0103", "0203", "0303", "0403", "0503", "0603", "0703", "0803", "0903"]

    start_pos = -1
    for pattern in START_PATTERNS:
        start_pos = meter_reading.find(pattern)
        if start_pos != -1:
            break

    if start_pos == -1:
        return None

    parsed_reading = meter_reading[start_pos:]

    if len(parsed_reading) < 22:  # Ensure enough data is available
        return None

    try:
        reading_hex = parsed_reading[14:22]  # First 8 hex characters
        liters = int(reading_hex, 16) / 10  

        flowrate_hex = parsed_reading[10:14]  
        flowrate = int(flowrate_hex, 16) / 1000  

        return {"liters": liters, "flowrate": flowrate}
    except:
        return None

# GUI Application using Tkinter
class MeterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MST Test Bench Monitoring Zeven")
        self.root.geometry("800x600")

        # Create table with device IDs
        self.tree = ttk.Treeview(root, columns=("Device ID", "Liters", "Flowrate"), show="headings")
        self.tree.heading("Device ID", text="Device ID")
        self.tree.heading("Liters", text="Reading (L)")
        self.tree.heading("Flowrate", text="Flowrate (m³/h)")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Add placeholders for device IDs
        for device_id in modbus_commands.keys():
            self.tree.insert("", "end", iid=device_id, values=(device_id, "Waiting...", "Waiting..."))

        # Add session header before starting updates
        add_session_header()

        # Live graph setup
        self.flowrate_data = deque(maxlen=100)  # Stores last 100 readings
        self.time_data = deque(maxlen=100)

        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Flowrate Over Time")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Flowrate (m³/h)")
        self.ax.grid(True)

        self.line, = self.ax.plot([], [], "b-", label="Flowrate (m³/h)")
        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Start updating data
        self.update_data()

    def update_data(self):
        if ser is None or not ser.is_open:
            print(f"Serial port {COM_PORT} is not available.")
            self.root.after(2000, self.update_data)  # Retry after 2 seconds
            return

        for device_id, command in modbus_commands.items():
            try:
                ser.write(command)
                time.sleep(0.1)  # Short delay for response

                response = ser.read(60)  
                
                if response:
                    hex_response = response.hex().upper()
                    print(f"[Device {device_id}] Response: {hex_response}")

                    parsed_data = watermeter_parsing(hex_response)
                    if parsed_data:
                        liters = parsed_data["liters"]
                        flowrate = parsed_data["flowrate"]
                        timestamp = datetime.now().strftime("%H:%M:%S")

                        print(f"[Device {device_id}] Reading: {liters} L, Flowrate: {flowrate} m³/h")
                        self.tree.item(device_id, values=(device_id, liters, flowrate))

                        # Append data to CSV
                        with open(CSV_FILE, mode="a", newline="") as file:
                            writer = csv.writer(file)
                            writer.writerow([timestamp, device_id, liters, flowrate])

                        # Update graph
                        self.flowrate_data.append(flowrate)
                        self.time_data.append(timestamp)
                        self.update_graph()

                    else:
                        self.tree.item(device_id, values=(device_id, "Error", "Error"))
                else:
                    self.tree.item(device_id, values=(device_id, "No response", "No response"))

            except Exception as e:
                self.tree.item(device_id, values=(device_id, "Error", "Error"))

        # Refresh data every 500ms
        self.root.after(500, self.update_data)

    def update_graph(self):
        self.ax.clear()
        self.ax.set_title("Flowrate Over Time")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Flowrate (m³/h)")
        self.ax.grid(True)

        self.ax.plot(self.time_data, self.flowrate_data, "b-", label="Flowrate (m³/h)")
        self.ax.legend()

        self.canvas.draw()

# Run the GUI
root = tk.Tk()
app = MeterGUI(root)
root.mainloop()
