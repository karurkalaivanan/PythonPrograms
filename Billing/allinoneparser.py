import os
import re
import struct
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv


# ==========================================================
# DLMS BILLING PARSER
# ==========================================================

def rebuild_apdu_from_file(filepath):
    with open(filepath, "r") as f:
        raw_data = f.read()

    frames_text = raw_data.split("_")
    full_apdu = b''

    for part in frames_text:
        match = re.search(r'7e.*?7e', part, re.IGNORECASE)
        if not match:
            continue

        hex_frame = match.group().replace(" ", "")
        frame = bytes.fromhex(hex_frame)

        if frame[0] != 0x7E or frame[-1] != 0x7E:
            continue

        llc_index = frame.find(b'\xE6\xE7\x00')

        if llc_index != -1:
            apdu = frame[llc_index+3:-3]
        else:
            apdu = frame[9:-3]

        full_apdu += apdu

    return full_apdu


def parse_billing(apdu):
    index = 0

    # Skip GET RESPONSE header
    if apdu[0] == 0xC4:
        index += 4

    index += 8  # block info

    if apdu[index] != 0x01:
        raise Exception("Not Array format")

    index += 1
    array_count = apdu[index]
    index += 1

    if apdu[index] != 0x02:
        raise Exception("Not Structure format")

    index += 1
    structure_count = apdu[index]
    index += 1

    billing_rows = []

    def parse_element(data, idx):
        tag = data[idx]

        if tag == 0x17:  # Float32
            value = struct.unpack('>f', data[idx+1:idx+5])[0]
            return value, idx + 5

        elif tag == 0x09 and data[idx+1] == 0x0C:  # DateTime
            year = int.from_bytes(data[idx+2:idx+4], 'big')
            month = data[idx+4]
            day = data[idx+5]
            hour = data[idx+6]
            minute = data[idx+7]
            second = data[idx+8]
            dt = f"{year}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}"
            return dt, idx + 14

        elif tag == 0x06:  # Unsigned32
            value = int.from_bytes(data[idx+1:idx+5], 'big')
            return value, idx + 5

        elif tag == 0x12:  # Unsigned16
            value = int.from_bytes(data[idx+1:idx+3], 'big')
            return value, idx + 3

        elif tag == 0x10:  # Signed16
            value = struct.unpack('>h', data[idx+1:idx+3])[0]
            return value, idx + 3

        else:
            return None, idx + 1

    for row in range(array_count):
        row_data = []

        for _ in range(structure_count):
            value, index = parse_element(apdu, index)
            if value is not None:
                row_data.append(value)

        billing_rows.append(row_data)

    return billing_rows


# ==========================================================
# GUI APPLICATION
# ==========================================================

class BillingViewer(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("DLMS Professional Billing Viewer")
        self.geometry("1200x600")

        self.billing_data = []

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", pady=10)

        tk.Button(btn_frame, text="Load Billing File", command=self.load_file,
                  bg="#2E86C1", fg="white", width=20).pack(side="left", padx=10)

        tk.Button(btn_frame, text="Export CSV", command=self.export_csv,
                  bg="#28B463", fg="white", width=20).pack(side="left", padx=10)

        # Table
        self.tree = ttk.Treeview(self)
        self.tree.pack(fill="both", expand=True)

        scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar_y.pack(side="right", fill="y")

        scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        scrollbar_x.pack(side="bottom", fill="x")

        self.tree.configure(yscrollcommand=scrollbar_y.set,
                            xscrollcommand=scrollbar_x.set)


    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not filepath:
            return

        try:
            apdu = rebuild_apdu_from_file(filepath)
            self.billing_data = parse_billing(apdu)
            self.display_data()
            messagebox.showinfo("Success", "Billing data loaded successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))


    def display_data(self):

        self.tree.delete(*self.tree.get_children())

        if not self.billing_data:
            return

        max_columns = max(len(row) for row in self.billing_data)

        self.tree["columns"] = [f"C{i}" for i in range(max_columns)]
        self.tree["show"] = "headings"

        for i in range(max_columns):
            self.tree.heading(f"C{i}", text=f"Param {i+1}")
            self.tree.column(f"C{i}", width=120)

        for row in self.billing_data:
            self.tree.insert("", "end", values=row)


    def export_csv(self):
        if not self.billing_data:
            messagebox.showwarning("Warning", "No billing data to export")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".csv")
        if not filepath:
            return

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(self.billing_data)

        messagebox.showinfo("Success", "CSV Exported Successfully!")


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":
    app = BillingViewer()
    app.mainloop()