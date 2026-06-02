import tkinter as tk
from tkinter import ttk
import serial, threading, csv, time
import serial.tools.list_ports
from datetime import datetime

ACK, NAK = 0x06, 0x15
CSV_FILE = "meter_log.csv"

# ---------------- CHECKSUM ----------------
def checksum(pkt):
    s = sum(pkt[1:-1]) & 0xFF
    return (~s + 1) & 0xFF

def nibble_swap(v):
    return ((v & 0x0F) << 4) | ((v & 0xF0) >> 4)

def challenge_response(a):
    if len(a) != 4:
        raise ValueError("Invalid challenge length")

    a0, a1, a2, a3 = a

    X = (a1 + a2 + a3) & 0xFF
    X ^= a2
    X = (X + a0) & 0xFF
    X = nibble_swap(X)

    Y = (a0 + a2 + a3) & 0xFF
    Y ^= a3
    Y = (Y + a1) & 0xFF
    Y = nibble_swap(Y)

    return X, Y

# ---------------- GUI ----------------
class MeterGUI:
    def __init__(self, root):
        self.root = root
        root.title("Advanced Meter Communication Tool")
        self.ser = None
        self.build_ui()
        self.init_csv()

    # ---------- UI ----------
    def build_ui(self):
        top = ttk.Frame(self.root)
        top.pack(fill="x")

        self.port = ttk.Combobox(top, width=12)
        self.port.pack(side="left", padx=5)
        ttk.Button(top, text="Refresh", command=self.refresh_ports).pack(side="left")
        ttk.Button(top, text="Connect", command=self.connect).pack(side="left")
        ttk.Button(top, text="SIGN ON", command=self.sign_on).pack(side="left")
        ttk.Button(top, text="BREAK", command=self.send_break).pack(side="left")

        btns = ttk.Frame(self.root)
        btns.pack(fill="x", pady=5)

        commands = [
            ("Meter ID",0x01),("RTC",0xC8),
            ("Previous MD",0xCE),("CURRENT MD",0xCD),
            ("Energy Total",0xCB),
            
        ]

        for name, cmd in commands:
            ttk.Button(btns, text=name,
                       command=lambda c=cmd: self.send_72(c)).pack(side="left", padx=2)

        self.log = tk.Text(self.root, height=30, width=120)
        self.log.pack()

        self.refresh_ports()

    # ---------- UTIL ----------
    def refresh_ports(self):
        self.port["values"] = [p.device for p in serial.tools.list_ports.comports()]

    def connect(self):
        self.ser = serial.Serial(self.port.get(), 9600, timeout=2)
        self.write_log("SYS", "Connected")

    def write_log(self, tag, msg, color="black"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.insert("end", f"[{ts}] {tag} : {msg}\n", tag)
        self.log.tag_config(tag, foreground=color)
        self.log.see("end")

    def csv_log(self, direction, cmd, raw, decoded=""):
        with open(CSV_FILE, "a", newline="") as f:
            csv.writer(f).writerow([
                datetime.now(), direction, cmd, raw, decoded
            ])

    def init_csv(self):
        with open(CSV_FILE, "w", newline="") as f:
            csv.writer(f).writerow(
                ["Time","Dir","Cmd","Raw HEX","Decoded"]
            )

    # ---------- SEND / RX ----------
    def send(self, pkt, cmd=""):
        self.ser.write(bytes(pkt))
        raw = " ".join(f"{b:02X}" for b in pkt)
        self.write_log("TX", raw, "blue")
        self.csv_log("TX", cmd, raw)

    def recv(self):
        data = self.ser.read(64)
        if data:
            raw = " ".join(f"{b:02X}" for b in data)
            self.write_log("RX", raw, "green")
            self.csv_log("RX", "", raw)
        return data

    # ---------- SIGN ON ----------
    def sign_on(self):
        threading.Thread(target=self._signon, daemon=True).start()

    def _signon(self):
        # --- SEND SIGN ON ---
        pkt = [0x01,0x3F,0x42,0x45,0x53,0x43,0xFF,0xFF,0xFF,0]
        pkt[-1] = checksum(pkt)
        self.send(pkt,"SIGNON")

        # --- WAIT FOR ACK ---
        ack = self.ser.read(1)
        if ack != bytes([ACK]):
            self.write_log("ERR","No ACK for Sign-On","red")
            return

        # --- READ FULL CHALLENGE PACKET ---
        rx = self.ser.read(64)   # read full frame
        if len(rx) < 14:
            self.write_log("ERR",f"Invalid challenge length ({len(rx)})","red")
            return

        self.write_log("RX", " ".join(f"{b:02X}" for b in rx), "green")

        # --- EXTRACT CHALLENGE (BYTES 9–12) ---
        challenge = rx[9:13]

        if len(challenge) != 4:
            self.write_log("ERR","Challenge not received","red")
            return

        # --- CALCULATE RESPONSE ---
        X, Y = challenge_response(challenge)

        self.write_log("DATA",f"Challenge={challenge.hex().upper()}  X={X:02X} Y={Y:02X}","purple")

        # --- SEND RESPONSE ---
        resp = [0x01,0x42,0x45,X,Y,0xFF,0xFF,0xFF,0xFF,0]
        resp[-1] = checksum(resp)
        self.send(resp,"CHALLENGE")

        result = self.ser.read(1)
        if result == bytes([ACK]):
            self.write_log("SYS","SIGN ON SUCCESS","green")
        else:
            self.write_log("SYS","SIGN ON FAILED","red")

    # def _signon(self):
    #     pkt = [0x01,0x3F,0x42,0x45,0x53,0x43,0xFF,0xFF,0xFF,0]
    #     pkt[-1] = checksum(pkt)
    #     self.send(pkt,"SIGNON")
        # if self.recv()[:1] != bytes([ACK]): return

        # rx = self.recv()
        # ch = rx[9:13]
        # X,Y = challenge_response(ch)
        # resp = [0x01,0x42,0x45,X,Y,0xFF,0xFF,0xFF,0xFF,0]
        # resp[-1] = checksum(resp)
        # self.send(resp,"CHALLENGE")
        # self.recv()

    # ---------- BREAK ----------
    def send_break(self):
        pkt = [0x01,0x1B,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0]
        pkt[-1] = checksum(pkt)
        self.send(pkt,"BREAK")

    # ---------- 0x72 COMMAND ----------
    def send_72(self, sub):
        pkt = [0x01,0x72,0x01,sub,0xFF,0xFF,0xFF,0xFF,0xFF,0]
        pkt[-1] = checksum(pkt)
        self.send(pkt,f"72-{sub:02X}")
        self.recv()
        rx = self.recv()
        self.decode(sub, rx)

    # ---------- DECODER ----------
    def decode(self, sub, rx):
        try:
            if sub == 0x04:
                vb = int.from_bytes(rx[3:5],"big")/10
                ib = int.from_bytes(rx[9:11],"big")/100
                freq = int.from_bytes(rx[-3:-1],"big")/100
                self.write_log("DATA",
                               f"Voltage={vb}V Current={ib}A Freq={freq}Hz",
                               "purple")
        except:
            pass

# ---------------- RUN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    MeterGUI(root)
    root.mainloop()
