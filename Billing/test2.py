import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import binascii
import re
import struct

def parse_obis_and_values(hex_text: str):
    hex_clean = re.sub(r'[^0-9a-fA-F]', '', hex_text.lower())
    try:
        raw_bytes = binascii.unhexlify(hex_clean)
    except binascii.Error:
        return None, "Invalid hex string"

    frames = []
    i = 0
    while i < len(raw_bytes):
        if raw_bytes[i] == 0x7e:
            start = i
            i += 1
            while i < len(raw_bytes) and raw_bytes[i] != 0x7e:
                i += 1
            if i < len(raw_bytes) and raw_bytes[i] == 0x7e:
                frame = raw_bytes[start:i+1]
                if len(frame) >= 9:
                    frames.append(frame)
        else:
            i += 1

    if not frames:
        return None, "No valid HDLC frames found"

    results = []
    for frame_idx, frame in enumerate(frames, 1):
        if len(frame) < 12:
            continue

        addr_len = 1
        if frame[1] & 0x01 == 0:
            addr_len = 2

        dlms_start = 1 + addr_len + 1
        dlms_data = frame[dlms_start:-3]

        pos = 0
        while pos < len(dlms_data) - 10:
            if dlms_data[pos:pos+2] == b'\x09\x06':
                obis_bytes = dlms_data[pos+2:pos+8]
                obis_str = ".".join(f"{b:02d}" for b in obis_bytes)

                value_str = "—"
                consumed = 8

                if pos + 8 < len(dlms_data):
                    tag = dlms_data[pos + 8]
                    consumed += 1

                    if tag == 0x06 and pos + 8 + 8 <= len(dlms_data):  # Double
                        raw = dlms_data[pos+9:pos+17]
                        try:
                            val = struct.unpack(">d", raw)[0]
                            # Most common scaler for energy: ×1000
                            scaled = val / 1000.0
                            value_str = f"{scaled:,.3f} kWh"
                        except:
                            value_str = "double err"

                        consumed += 8

                    elif tag == 0x09 or tag == 0x0c:  # Octet string
                        if pos + 9 < len(dlms_data):
                            length = dlms_data[pos + 9]
                            consumed += 1
                            if pos + 9 + length <= len(dlms_data):
                                str_bytes = dlms_data[pos+10:pos+10+length]
                                if length == 12:  # date-time
                                    try:
                                        year = int.from_bytes(str_bytes[0:2], 'big')
                                        mon  = str_bytes[2]
                                        day  = str_bytes[3]
                                        hour = str_bytes[5]
                                        min_ = str_bytes[6]
                                        sec  = str_bytes[7]
                                        value_str = f"{day:02d}-{mon:02d}-{year} {hour:02d}:{min_:02d}:{sec:02d}"
                                    except:
                                        value_str = str_bytes.hex().upper()
                                else:
                                    try:
                                        value_str = str_bytes.decode('ascii').strip()
                                    except:
                                        value_str = str_bytes.hex().upper()
                                consumed += length

                    elif tag in (0x10, 0x11, 0x12, 0x06):  # integers
                        sizes = {0x10:1, 0x11:1, 0x12:2, 0x06:4}
                        sz = sizes.get(tag, 4)
                        if pos + 8 + sz <= len(dlms_data):
                            val = int.from_bytes(dlms_data[pos+9:pos+9+sz], 'big')
                            value_str = str(val)
                            consumed += sz

                hint = f"attr={tag:02x}" if 'tag' in locals() else ""

                results.append((frame_idx, obis_str, pos, hint, value_str))

                pos += consumed
            else:
                pos += 1

    msg = f"Found {len(frames)} frames • {len(results)} OBIS + values"
    return results, msg


class DLMSViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DLMS / OBIS Hex Viewer with Values")
        self.geometry("1300x750")

        top = ttk.Frame(self, padding=10)
        top.pack(fill='x')

        ttk.Button(top, text="Parse Hex", command=self.parse).pack(side='left', padx=6)
        ttk.Button(top, text="Clear", command=self.clear).pack(side='left', padx=6)

        paned = ttk.PanedWindow(self, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=10, pady=5)

        # Left: input
        left = ttk.LabelFrame(paned, text="Hex Input", padding=8)
        paned.add(left, weight=1)

        self.text = scrolledtext.ScrolledText(left, wrap='word', font=("Consolas", 10), height=35)
        self.text.pack(fill='both', expand=True)

        # Right: table
        right = ttk.LabelFrame(paned, text="OBIS & Values", padding=8)
        paned.add(right, weight=3)

        cols = ("Frame", "OBIS", "Pos", "Attr", "Value")
        self.tree = ttk.Treeview(right, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=140, anchor='center')

        vsb = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        self.status = ttk.Label(self, text="Ready", relief='sunken', anchor='w')
        self.status.pack(fill='x', ipady=5)

    def parse(self):
        self.tree.delete(*self.tree.get_children())
        content = self.text.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("Input needed", "Paste hex first")
            return

        data, msg = parse_obis_and_values(content)
        self.status.config(text=msg)

        if data:
            for frame, obis, pos, attr, val in data:
                self.tree.insert("", "end", values=(frame, obis, pos, attr, val))
        else:
            messagebox.showerror("Error", msg)

    def clear(self):
        self.text.delete("1.0", "end")
        self.tree.delete(*self.tree.get_children())
        self.status.config(text="Cleared")


if __name__ == "__main__":
    app = DLMSViewer()

    # Pre-fill with your latest fragment
    app.text.insert("1.0", """7e a9 09 41 03 52 e1 8a e6 e7 00 c4 02 c1 00 00 00 00 01 00 82 01 ea 01 82 01 d9 02 04 12 00 03 09 06 00 00 00 01 02 ff 0f 02 12 00 00 02 04 12 00 03 09 06 01 00 0d 00 00 ff 0f 02 12 00 00 02 04 12 00 03 09 06 01 00 0d 00 82 ff 0f 02 12 00 00 02 04 12 00 01 09 06 00 00 00 01 0c ff 0f 02 12 00 00 02 04 12 00 01 09 06 01 00 60 8d 01 ff 0f 02 12 00 00 02 04 12 00 03 09 06 00 00 5e 5b 0d ff 0f 02 12 00 00 02 04 12 00 03 09 06 01 00 01 08 00 ff 0f 02 12 00 00 02 04 12 00 03 09 06 01 00 02 08 00 ff 0f 02 12 00 00 02 04 12 00 03 09 06 01 00 81 08 00 ff 0f 02 12 00 00 02 04 12 00 03 09 06 01 00 82 08 00 ff 0f 02 12 00 00 02 04 12 00 03 09 06 01 00 05 08 00 ff 0f 02 12 00 00 02 04 12 00 03 09 06 01 00 08 08 00 ff 0f 02 12 00 00 02 04 12 00 03 09 06 01 00 06 08 00 ff 0f 02 12 00 00 02 04 12 fd 29 7e""")

    app.mainloop()