import os
import re
import struct
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv

# ==========================================================
# DLMS BILLING PARSER ENGINE
# ==========================================================

def rebuild_apdu_from_file(filepath):
    with open(filepath, "r") as f:
        raw_data = f.read()

    # Split by underscore if frames are separated that way in your logs
    frames_text = raw_data.split("_")
    full_apdu = b''

    for part in frames_text:
        match = re.search(r'7e.*?7e', part, re.IGNORECASE | re.DOTALL)
        if not match:
            continue

        hex_frame = match.group().replace(" ", "").replace("\n", "").replace("\r", "")
        frame = bytes.fromhex(hex_frame)

        if len(frame) < 10 or frame[0] != 0x7E or frame[-1] != 0x7E:
            continue

        # Look for LLC layer (E6 E7 00)
        llc_index = frame.find(b'\xE6\xE7\x00')

        if llc_index != -1:
            # Strip HDLC header/footer and LLC
            apdu = frame[llc_index+3:-3]
        else:
            # Fallback for standard HDLC addressing offsets
            apdu = frame[9:-3]

        full_apdu += apdu

    return full_apdu

def parse_billing(apdu):
    index = 0
    if not apdu: return []

    # Skip GET RESPONSE / Action Response headers if present
    if apdu[0] in [0xC4, 0xC7]:
        index += 4

    # Skip potential block-transfer info (common in large billing reads)
    # This offset can vary based on the specific DLMS conformance block
    index += 8  

    if index >= len(apdu): return []

    # Check for Array (0x01)
    if apdu[index] != 0x01:
        raise Exception(f"Expected Array (0x01), found {hex(apdu[index])} at index {index}")

    index += 1
    array_count = apdu[index]
    index += 1

    billing_rows = []

    def parse_element(data, idx):
        if idx >= len(data): return None, idx
        tag = data[idx]

        if tag == 0x17:  # Float32
            value = struct.unpack('>f', data[idx+1:idx+5])[0]
            return round(value, 3), idx + 5

        elif tag == 0x09:  # Octet-String (usually DateTime)
            length = data[idx+1]
            if length == 0x0C: # Standard 12-byte DateTime
                year = int.from_bytes(data[idx+2:idx+4], 'big')
                dt = f"{year}-{data[idx+4]:02}-{data[idx+5]:02} {data[idx+6]:02}:{data[idx+7]:02}:{data[idx+8]:02}"
                return dt, idx + 2 + length
            else:
                return data[idx+2:idx+2+length].hex(), idx + 2 + length

        elif tag == 0x06:  # Unsigned32
            value = int.from_bytes(data[idx+1:idx+5], 'big')
            return value, idx + 5

        elif tag == 0x12:  # Unsigned16
            value = int.from_bytes(data[idx+1:idx+3], 'big')
            return value, idx + 3

        elif tag == 0x10:  # Signed16
            value = struct.unpack('>h', data[idx+1:idx+3])[0]
            return value, idx + 3
        
        elif tag == 0x0F:  # Integer8
            value = struct.unpack('>b', data[idx+1:idx+2])[0]
            return value, idx + 2

        return "Unknown", idx + 1

    for _ in range(array_count):
        if index >= len(apdu): break
        
        # Check for Structure (0x02)
        if apdu[index] == 0x02:
            index += 1
            struct_len = apdu[index]
            index += 1
            
            row_data = []
            for _ in range(struct_len):
                val, index = parse_element(apdu, index)
                row_data.append(val)
            billing_rows.append(row_data)
        else:
            index += 1

    return billing_rows

# ==========================================================
# GUI APPLICATION
# ==========================================================

class BillingViewer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("DLMS Professional Billing Viewer")
        self.geometry("1100x700")

        self.billing_data = []

        # UI Construction
        self.create_widgets()

    def create_widgets(self):
        btn_frame = tk.Frame(self, bg="#F0F0F0")
        btn_frame.pack(fill="x", pady=5)

        # Main Buttons
        load_btn = tk.Button(btn_frame, text="📂 Load Billing File", command=self.load_file,
                             bg="#2E86C1", fg="white", font=('Arial', 10, 'bold'), width=18)
        load_btn.pack(side="left", padx=10, pady=5)

        export_btn = tk.Button(btn_frame, text="📊 Export CSV", command=self.export_csv,
                               bg="#28B463", fg="white", font=('Arial', 10, 'bold'), width=18)
        export_btn.pack(side="left", padx=10, pady=5)

        clear_btn = tk.Button(btn_frame, text="🗑️ Clear Data", command=self.clear_data,
                              bg="#CB4335", fg="white", font=('Arial', 10, 'bold'), width=15)
        clear_btn.pack(side="right", padx=10, pady=5)

        # Table with Scrollbars
        table_container = tk.Frame(self)
        table_container.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(table_container)
        
        sy = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        sx = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")

        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not filepath: return

        try:
            apdu = rebuild_apdu_from_file(filepath)
            new_rows = parse_billing(apdu)

            if not new_rows:
                messagebox.showwarning("Empty", "No valid billing data found in file.")
                return

            self.billing_data.extend(new_rows)
            self.display_data(append=True)
            messagebox.showinfo("Success", f"Added {len(new_rows)} rows.")

        except Exception as e:
            messagebox.showerror("Parsing Error", f"Failed to parse DLMS data:\n{str(e)}")

    def display_data(self, append=False):
        if not self.billing_data: return

        # Set up columns if first load or if number of columns changed
        max_cols = max(len(row) for row in self.billing_data)
        current_cols = list(self.tree["columns"])

        if len(current_cols) < max_cols:
            cols = [f"C{i}" for i in range(max_cols)]
            self.tree["columns"] = cols
            self.tree["show"] = "headings"
            for i, col in enumerate(cols):
                self.tree.heading(col, text=f"Param {i+1}")
                self.tree.column(col, width=120, anchor="center")

        # Add only new rows
        existing_count = len(self.tree.get_children())
        for row in self.billing_data[existing_count:]:
            self.tree.insert("", "end", values=row)

    def clear_data(self):
        if messagebox.askyesno("Clear", "Clear all loaded data?"):
            self.billing_data = []
            self.tree.delete(*self.tree.get_children())

    def export_csv(self):
        if not self.billing_data:
            messagebox.showwarning("Warning", "No data to export.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not path: return

        try:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(self.billing_data)
            messagebox.showinfo("Success", "File exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

if __name__ == "__main__":
    app = BillingViewer()
    app.mainloop()