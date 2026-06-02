# daily_diary_FINAL_WITH_CSV_AND_TXT.py  ← BEST VERSION EVER
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import Calendar
import json
from datetime import datetime
import os
import csv

# Save data safely in Documents
DATA_FILE = os.path.join(os.path.expanduser("~"), "Documents", "my_diary.json")

def load_entries():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_entries(entries):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=4, ensure_ascii=False)

class DiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My Diary - TXT + CSV Export")
        self.root.geometry("1300x750")
        self.root.configure(bg="#f8f9fa")

        self.entries = load_entries()

        # LEFT PANEL
        left = tk.Frame(root, bg="#2c3e50", width=340)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)

        tk.Label(left, text="MY DIARY", font=("Arial", 24, "bold"), bg="#2c3e50", fg="white").pack(pady=30)

        self.cal = Calendar(left, selectmode="day", date_pattern="y-mm-dd",
                            background="#34495e", foreground="white", selectbackground="#3498db")
        self.cal.pack(pady=20, padx=20)
        self.cal.bind("<<CalendarSelected>>", lambda e: self.filter_by_date())

        tk.Button(left, text="Show All", command=self.show_all,
                  bg="#27ae60", fg="white", font=("bold", 12), height=2).pack(pady=30, padx=50, fill=tk.X)

        # RIGHT PANEL
        right = tk.Frame(root, bg="#f8f9fa")
        right.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(right, text="Write Your Day", font=("Helvetica", 22, "bold"), fg="#2c3e50").pack(pady=15)

        box = tk.LabelFrame(right, text=" Entry ", font=("Arial", 14, "bold"), padx=20, pady=20)
        box.pack(fill=tk.X, pady=10)

        # Date & Time
        dtf = tk.Frame(box)
        dtf.pack(fill=tk.X, pady=10)
        tk.Label(dtf, text="Date & Time:", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        self.dt_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        tk.Entry(dtf, textvariable=self.dt_var, width=28, font=("Arial", 11)).pack(side=tk.LEFT, padx=12)
        tk.Button(dtf, text="Now", command=lambda: self.dt_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                  bg="#3498db", fg="white").pack(side=tk.LEFT)

        self.text_box = tk.Text(box, height=10, font=("Arial", 12), wrap=tk.WORD)
        self.text_box.pack(fill=tk.X, pady=15)

        # Buttons
        btns = tk.Frame(box)
        btns.pack(pady=12)
        tk.Button(btns, text="Save Entry", command=self.save_entry, bg="#27ae60", fg="white", width=14, font=("bold",11)).pack(side=tk.LEFT, padx=10)
        tk.Button(btns, text="Edit Selected", command=self.edit_entry, bg="#f39c12", fg="white", width=14, font=("bold",11)).pack(side=tk.LEFT, padx=10)
        tk.Button(btns, text="Delete", command=self.delete_entry, bg="#e74c3c", fg="white", width=12, font=("bold",11)).pack(side=tk.LEFT, padx=10)
        tk.Button(btns, text="Export as TXT", command=self.export_txt, bg="#9b59b6", fg="white", width=16, font=("bold",11)).pack(side=tk.LEFT, padx=10)
        tk.Button(btns, text="Export as CSV", command=self.export_csv, bg="#e67e22", fg="white", width=16, font=("bold",11)).pack(side=tk.LEFT, padx=10)

        # Table
        cols = ("No", "Date & Time", "Preview")
        self.tree = ttk.Treeview(right, columns=cols, show="headings")
        self.tree.heading("No", text="No.")
        self.tree.heading("Date & Time", text="Date & Time")
        self.tree.heading("Preview", text="Entry Preview")
        self.tree.column("No", width=70, anchor="center")
        self.tree.column("Date & Time", width=180, anchor="center")
        self.tree.column("Preview", width=780)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=15)
        self.tree.bind("<Double-1>", lambda e: self.edit_entry())

        scroll = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.refresh_table()

    def refresh_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for i, e in enumerate(reversed(self.entries), 1):
            preview = e["content"].replace("\n", " ")[:150]
            if len(e["content"]) > 150:
                preview += "..."
            self.tree.insert("", "end", values=(i, e["datetime"], preview))

    def filter_by_date(self):
        date = self.cal.get_date()
        for i in self.tree.get_children():
            self.tree.delete(i)
        n = 1
        for e in reversed(self.entries):
            if e["datetime"].startswith(date):
                preview = e["content"].replace("\n", " ")[:150] + ("..." if len(e["content"])>150 else "")
                self.tree.insert("", "end", values=(n, e["datetime"], preview))
                n += 1

    def show_all(self):
        self.cal.selection_clear()
        self.refresh_table()

    def save_entry(self):
        content = self.text_box.get("1.0", tk.END).strip()
        dt = self.dt_var.get().strip()
        if not content:
            messagebox.showwarning("Empty", "Write something first!")
            return
        self.entries.append({"datetime": dt or datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "content": content})
        save_entries(self.entries)
        self.text_box.delete("1.0", tk.END)
        self.refresh_table()
        messagebox.showinfo("Saved!", "Entry saved")

    def edit_entry(self):
        sel = self.tree.selection()
        if not sel: 
            messagebox.showwarning("Select", "Select an entry")
            return
        dt = self.tree.item(sel[0])["values"][1]
        for i, e in enumerate(self.entries):
            if e["datetime"] == dt:
                self.dt_var.set(e["datetime"])
                self.text_box.delete("1.0", tk.END)
                self.text_box.insert("1.0", e["content"])
                self.entries.pop(i)
                save_entries(self.entries)
                self.refresh_table()
                messagebox.showinfo("Edit", "Now edit and click Save")
                break

    def delete_entry(self):
        sel = self.tree.selection()
        if not sel: return
        dt = self.tree.item(sel[0])["values"][1]
        self.entries = [e for e in self.entries if e["datetime"] != dt]
        save_entries(self.entries)
        self.refresh_table()

    def export_txt(self):
        if not self.entries:
            messagebox.showinfo("Empty", "No entries")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt")],
            initialfile=f"Diary_{datetime.now():%Y%m%d}.txt"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write("MY PERSONAL DIARY\n" + "="*60 + "\n\n")
                for e in reversed(self.entries):
                    f.write(f"Date & Time: {e['datetime']}\n")
                    f.write(f"{e['content']}\n")
                    f.write("-"*60 + "\n\n")
            messagebox.showinfo("Success", f"Saved TXT:\n{path}")

    def export_csv(self):
        if not self.entries:
            messagebox.showinfo("Empty", "No entries")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV File", "*.csv")],
            initialfile=f"Diary_{datetime.now():%Y%m%d}.csv"
        )
        if path:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Date & Time", "Entry"])
                for e in reversed(self.entries):
                    writer.writerow([e['datetime'], e['content']])
            messagebox.showinfo("Success", f"Saved CSV:\n{path}\nOpen in Excel!")

if __name__ == "__main__":
    root = tk.Tk()
    app = DiaryApp(root)
    root.mainloop()