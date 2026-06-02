import os
import re
import struct
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv


# ==========================================================
# OBIS NAME + UNIT MAP
# ==========================================================

OBIS_INFO = {
    "0.0.0.1.2.255": ("Billing Date", ""),
    "1.0.13.0.0.255": ("Avg PF for Billing Period", ""),
    "0.0.94.91.13.255": ("Billing Power On Duration", ""),
    "1.0.5.8.0.255": ("Cum Energy VArh Q1", "VArh"),
    "1.0.8.8.0.255": ("Cum Energy VArh Q4", "VArh"),
    "1.0.6.8.0.255": ("Cum Energy VArh Q2", "VArh"),
    "1.0.7.8.0.255": ("Cum Energy VArh Q3", "VArh"),
    "1.0.9.8.0.255": ("Cum Energy VAh Import", "VAh"),
    "1.0.10.8.0.255": ("Cum Energy VAh Export", "VAh"),
    "1.0.0.0.0.255": ("Meter Serial Number", ""),
    "1.0.1.8.0.255": ("Active Energy Import", "kWh"),
    "1.0.2.8.0.255": ("Active Energy Export", "kWh"),
    "1.0.3.8.0.255": ("Reactive Energy Import", "kVArh"),
    "1.0.4.8.0.255": ("Reactive Energy Export", "kVArh"),
    "1.0.1.6.0.255": ("Max Demand", "kW"),
    "1.0.32.7.0.255": ("Voltage L1", "V"),
    "1.0.52.7.0.255": ("Voltage L2", "V"),
    "1.0.72.7.0.255": ("Voltage L3", "V"),
    "1.0.31.7.0.255": ("Current L1", "A"),
    "1.0.51.7.0.255": ("Current L2", "A"),
    "1.0.71.7.0.255": ("Current L3", "A"),
    "1.0.1.8.1.255": ("Cum Energy Wh Import - TZ1", "Wh"),
    "1.0.1.8.2.255": ("Cum Energy Wh Import - TZ2", "Wh"),
    "1.0.1.8.3.255": ("Cum Energy Wh Import - TZ3", "Wh"),
    "1.0.1.8.4.255": ("Cum Energy Wh Import - TZ4", "Wh"),
    "1.0.1.8.5.255": ("Cum Energy Wh Import - TZ5", "Wh"),
    "1.0.1.8.6.255": ("Cum Energy Wh Import - TZ6", "Wh"),
    "1.0.1.8.7.255": ("Cum Energy Wh Import - TZ7", "Wh"),
    "1.0.1.8.8.255": ("Cum Energy Wh Import - TZ8", "Wh"),
    "1.0.2.8.1.255": ("Cum Energy Wh Export - TZ1", "Wh"),
    "1.0.2.8.2.255": ("Cum Energy Wh Export - TZ2", "Wh"),
    "1.0.2.8.3.255": ("Cum Energy Wh Export - TZ3", "Wh"),
    "1.0.2.8.4.255": ("Cum Energy Wh Export - TZ4", "Wh"),
    "1.0.2.8.5.255": ("Cum Energy Wh Export - TZ5", "Wh"),
    "1.0.2.8.6.255": ("Cum Energy Wh Export - TZ6", "Wh"),
    "1.0.2.8.7.255": ("Cum Energy Wh Export - TZ7", "Wh"),
    "1.0.2.8.8.255": ("Cum Energy Wh Export - TZ8", "Wh"),
    "1.0.9.8.1.255": ("Cum Energy VAh Import - TZ1", "VAh"),
    "1.0.9.8.2.255": ("Cum Energy VAh Import - TZ2", "VAh"),
    "1.0.9.8.3.255": ("Cum Energy VAh Import - TZ3", "VAh"),
    "1.0.9.8.4.255": ("Cum Energy VAh Import - TZ4", "VAh"),
    "1.0.9.8.5.255": ("Cum Energy VAh Import - TZ5", "VAh"),
    "1.0.9.8.6.255": ("Cum Energy VAh Import - TZ6", "VAh"),
    "1.0.9.8.7.255": ("Cum Energy VAh Import - TZ7", "VAh"),
    "1.0.9.8.8.255": ("Cum Energy VAh Import - TZ8", "VAh"),
    "1.0.10.8.1.255": ("Cum Energy VAh Export - TZ1", "VAh"),
    "1.0.10.8.2.255": ("Cum Energy VAh Export - TZ2", "VAh"),
    "1.0.10.8.3.255": ("Cum Energy VAh Export - TZ3", "VAh"),
    "1.0.10.8.4.255": ("Cum Energy VAh Export - TZ4", "VAh"),
    "1.0.10.8.5.255": ("Cum Energy VAh Export - TZ5", "VAh"),
    "1.0.10.8.6.255": ("Cum Energy VAh Export - TZ6", "VAh"),
    "1.0.10.8.7.255": ("Cum Energy VAh Export - TZ7", "VAh"),
    "1.0.10.8.8.255": ("Cum Energy VAh Export - TZ8", "VAh"),
    "1.0.1.6.0.255": ("MD W Import", "W"),
    "1.0.1.6.1.255": ("MD W Import - TZ1", "W"),
    "1.0.1.6.2.255": ("MD W Import - TZ2", "W"),
    "1.0.1.6.3.255": ("MD W Import - TZ3", "W"),
    "1.0.1.6.4.255": ("MD W Import - TZ4", "W"),
    "1.0.1.6.5.255": ("MD W Import - TZ5", "W"),
    "1.0.1.6.6.255": ("MD W Import - TZ6", "W"),
    "1.0.1.6.7.255": ("MD W Import - TZ7", "W"),
    "1.0.1.6.8.255": ("MD W Import - TZ8", "W"),
    "1.0.2.6.0.255": ("MD W Export", "W"),
    "1.0.2.6.1.255": ("MD W Import - TZ1", "W"),
    "1.0.2.6.2.255": ("MD W Import - TZ2", "W"),
    "1.0.2.6.3.255": ("MD W Import - TZ3", "W"),
    "1.0.2.6.4.255": ("MD W Import - TZ4", "W"),
    "1.0.2.6.5.255": ("MD W Import - TZ5", "W"),
    "1.0.2.6.6.255": ("MD W Import - TZ6", "W"),
    "1.0.2.6.7.255": ("MD W Import - TZ7", "W"),
    "1.0.2.6.8.255": ("MD W Import - TZ8", "W"),
    "1.0.9.6.0.255": ("MD VA Import", "W"),
    "1.0.9.6.1.255": ("MD VA Import - TZ1", "W"),
    "1.0.9.6.2.255": ("MD VA Import - TZ2", "W"),
    "1.0.9.6.3.255": ("MD VA Import - TZ3", "W"),
    "1.0.9.6.4.255": ("MD VA Import - TZ4", "W"),
    "1.0.9.6.5.255": ("MD VA Import - TZ5", "W"),
    "1.0.9.6.6.255": ("MD VA Import - TZ6", "W"),
    "1.0.9.6.7.255": ("MD VA Import - TZ7", "W"),
    "1.0.9.6.8.255": ("MD VA Import - TZ8", "W"),
    "1.0.10.6.0.255": ("MD VA Export", "W"),
    "1.0.10.6.1.255": ("MD VA Export - TZ1", "W"),
    "1.0.10.6.2.255": ("MD VA Export - TZ2", "W"),
    "1.0.10.6.3.255": ("MD VA Export - TZ3", "W"),
    "1.0.10.6.4.255": ("MD VA Export - TZ4", "W"),
    "1.0.10.6.5.255": ("MD VA Export - TZ5", "W"),
    "1.0.10.6.6.255": ("MD VA Export - TZ6", "W"),
    "1.0.10.6.7.255": ("MD VA Export - TZ7", "W"),
    "1.0.10.6.8.255": ("MD VA Export - TZ8", "W"),
}

obis_headers = []


# ==========================================================
# SAFE HEX CLEANER
# ==========================================================

def clean_hex_string(text):
    cleaned = re.sub(r'[^0-9A-Fa-f]', '', text)
    if len(cleaned) % 2 != 0:
        return None
    return cleaned


# ==========================================================
# STEP 1 : EXTRACT OBIS FROM OBIS FILE (SAFE)
# ==========================================================

# def extract_obis_from_file(filepath):

#     with open(filepath, "r") as f:
#         raw_data = f.read()

#     frames = re.findall(r'7e.*?7e', raw_data, re.IGNORECASE)
#     obis_list = []

#     for frame in frames:

#         hex_frame = clean_hex_string(frame)
#         if not hex_frame:
#             continue

#         try:
#             data = bytes.fromhex(hex_frame)
#         except:
#             continue

#         matches = re.finditer(b'\x09\x06(.{6})', data)

#         for match in matches:
#             obis_bytes = match.group(1)
#             obis = ".".join(str(b) for b in obis_bytes)

#             if obis not in obis_list:
#                 obis_list.append(obis)

#     return obis_list

def extract_obis_from_file(filepath):

    with open(filepath, "r") as f:
        raw_data = f.read()

    frames = re.findall(r'7e.*?7e', raw_data, re.IGNORECASE)
    obis_list = []

    for frame in frames:

        hex_frame = clean_hex_string(frame)
        if not hex_frame:
            continue

        try:
            data = bytes.fromhex(hex_frame)
        except:
            continue

        matches = re.finditer(b'\x09\x06(.{6})', data)

        for match in matches:
            obis_bytes = match.group(1)
            obis = ".".join(str(b) for b in obis_bytes)

            if obis not in obis_list:

                name = OBIS_INFO.get(obis, "Unknown OBIS")
                obis_list.append(f"{obis} - {name}")

    return obis_list
# ==========================================================
# STEP 2 : REBUILD APDU (SAFE)
# ==========================================================

def rebuild_apdu_from_file(filepath):

    with open(filepath, "r") as f:
        raw_data = f.read()

    frames = re.findall(r'7e.*?7e', raw_data, re.IGNORECASE)
    full_apdu = b''

    for frame in frames:

        hex_frame = clean_hex_string(frame)
        if not hex_frame:
            continue

        try:
            data = bytes.fromhex(hex_frame)
        except:
            continue

        if data[0] != 0x7E or data[-1] != 0x7E:
            continue

        llc_index = data.find(b'\xE6\xE7\x00')

        if llc_index != -1:
            apdu = data[llc_index+3:-3]
        else:
            apdu = data[9:-3]

        full_apdu += apdu

    return full_apdu


# ==========================================================
# STEP 3 : BILLING PARSER
# ==========================================================

def parse_billing(apdu):

    index = 0

    if apdu[0] == 0xC4:
        index += 4

    index += 8

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

        elif tag == 0x09:  # Octet String
            length = data[idx + 1]
            start = idx + 2
            end = start + length
            raw_bytes = data[start:end]

            if length == 12:  # DateTime
                year = int.from_bytes(raw_bytes[0:2], 'big')
                month = raw_bytes[2]
                day = raw_bytes[3]
                hour = raw_bytes[5]
                minute = raw_bytes[6]
                second = raw_bytes[7]

                dt = f"{day:02}-{month:02}-{year} {hour:02}:{minute:02}:{second:02}"
                return dt, end

            elif length < 9:
                return raw_bytes.hex().upper(), end

            else:
                try:
                    return raw_bytes.decode("ascii").strip(), end
                except:
                    return raw_bytes.hex().upper(), end

        elif tag == 0x06:  # Unsigned32
            value = int.from_bytes(data[idx+1:idx+5], 'big')
            return value, idx + 5

        elif tag == 0x11:  # Unsigned8
            return data[idx+1], idx + 2

        elif tag == 0x12:  # Unsigned16
            value = int.from_bytes(data[idx+1:idx+3], 'big')
            return value, idx + 3

        elif tag == 0x10:  # Signed16
            value = struct.unpack('>h', data[idx+1:idx+3])[0]
            return value, idx + 3

        else:
            return None, idx + 1

    for _ in range(array_count):

        row_data = []

        for _ in range(structure_count):
            value, index = parse_element(apdu, index)
            if value is not None:
                row_data.append(value)

        billing_rows.append(row_data)

    return billing_rows


# ==========================================================
# GUI
# ==========================================================

class BillingViewer(tk.Tk):

    def sort_column(self, col, reverse):

        data_list = []

        for child in self.tree.get_children(''):
            value = self.tree.set(child, col)

            # Try numeric sort first
            try:
                value = float(value)
            except:
                pass

            data_list.append((value, child))

        # Sort
        data_list.sort(reverse=reverse)

        # Rearrange rows
        for index, (val, child) in enumerate(data_list):
            self.tree.move(child, '', index)

        # Reverse next click
        self.tree.heading(col,
            command=lambda: self.sort_column(col, not reverse))
    
    def __init__(self):
        super().__init__()

        self.title("Professional DLMS Billing Viewer")
        self.geometry("1500x700")

        self.billing_data = []

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", pady=10)

        tk.Button(btn_frame, text="Load Billing OBIS File",
                  command=self.load_obis_file,
                  bg="#2E86C1", fg="white", width=25).pack(side="left", padx=10)

        tk.Button(btn_frame, text="Load Billing Data File",
                  command=self.load_billing_file,
                  bg="#28B463", fg="white", width=25).pack(side="left", padx=10)

        tk.Button(btn_frame, text="Export CSV",
                  command=self.export_csv,
                  bg="#AF7AC5", fg="white", width=20).pack(side="left", padx=10)

        self.tree = ttk.Treeview(self)
        self.tree.pack(fill="both", expand=True)

        scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar_y.pack(side="right", fill="y")

        scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        scrollbar_x.pack(side="bottom", fill="x")

        self.tree.configure(yscrollcommand=scrollbar_y.set,
                            xscrollcommand=scrollbar_x.set)

    # ======================================================

    def load_obis_file(self):

        global obis_headers

        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not filepath:
            return

        obis_headers = extract_obis_from_file(filepath)

        if not obis_headers:
            messagebox.showerror("Error", "No OBIS found")
            return

        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = obis_headers
        self.tree["show"] = "headings"

        for col in obis_headers:

            name, unit = OBIS_INFO.get(col, ("OBIS " + col, ""))
            header_text = f"{name} [{unit}]" if unit else name

            self.tree.heading(
                    col,
                    text=header_text,
                    anchor="center",
                    command=lambda _col=col: self.sort_column(_col, False)
                )
            self.tree.column(col, width=170, anchor="center", stretch=False)

        messagebox.showinfo("Success",
                            f"{len(obis_headers)} OBIS columns created")

    # ======================================================

    def load_billing_file(self):

        if not obis_headers:
            messagebox.showwarning("Warning", "Load OBIS file first")
            return

        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not filepath:
            return

        try:
            apdu = rebuild_apdu_from_file(filepath)
            new_rows = parse_billing(apdu)

            self.billing_data.extend(new_rows)

            for row in new_rows:

                formatted_row = []

                for value in row[:len(obis_headers)]:
                    if isinstance(value, float):
                        formatted_row.append(f"{value:.3f}")
                    else:
                        formatted_row.append(value)

                self.tree.insert("", "end", values=formatted_row)

            messagebox.showinfo("Success",
                                f"{len(new_rows)} billing rows appended")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ======================================================

    def export_csv(self):

        if not self.billing_data:
            messagebox.showwarning("Warning", "No billing data")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".csv")
        if not filepath:
            return

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(obis_headers)
            writer.writerows(self.billing_data)

        messagebox.showinfo("Success", "CSV Exported Successfully!")


# ==========================================================

if __name__ == "__main__":
    app = BillingViewer()
    app.mainloop()