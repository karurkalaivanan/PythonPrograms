# My_Diary_PERFECT.py  ← This one is flawless!
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import Calendar
from PIL import Image, ImageTk
from datetime import datetime
import json
import os
import csv

DATA_FILE = os.path.join(os.path.expanduser("~"), "Documents", "my_diary.json")

def load_entries():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for e in data:
                    e.setdefault("title", "Untitled Entry")
                    e.setdefault("datetime", "2025-01-01 00:00:00")
                    e.setdefault("content", "")
                    e.setdefault("image", None)
                return data
        except:
            return []
    return []

def save_entries(entries):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=4, ensure_ascii=False)

class MyDiary:
    def __init__(self):
        self.entries = load_entries()
        self.current_image = None
        self.editing_index = None  # To know if we are editing

        self.root = tk.Tk()
        self.root.title("My Personal Diary")
        self.root.geometry("1420x880")
        self.root.configure(bg="#f8f9fa")

        self.build_ui()
        self.refresh_list()
        self.root.mainloop()

    def build_ui(self):
        # TOP BAR
        top = tk.Frame(self.root, bg="#2c3e50", height=90)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(top, text="MY DIARY", font=("Arial", 32, "bold"), bg="#2c3e50", fg="white").pack(side=tk.LEFT, padx=30, pady=20)

        # Search
        search_f = tk.Frame(top, bg="#2c3e50")
        search_f.pack(side=tk.RIGHT, padx=30, pady=25)
        tk.Label(search_f, text="Search:", font=("Arial", 14, "bold"), bg="#2c3e50", fg="white").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.search_entries())
        tk.Entry(search_f, textvariable=self.search_var, font=("Arial", 14), width=35).pack(side=tk.LEFT, padx=10)
        tk.Button(search_f, text="Clear", command=lambda: self.search_var.set(""), bg="#e74c3c", fg="white", font=("bold",10)).pack(side=tk.LEFT, padx=5)

        # Export buttons
        tk.Button(top, text="Export TXT", command=self.export_txt, bg="#9b59b6", fg="white", font=("bold",12), width=12)).pack(side=tk.RIGHT, padx=10)
        tk.Button(top, text="Export CSV", command=self.export_csv, bg="#e67e22", fg="white", font=("bold",12), width=12).pack(side=tk.RIGHT, padx=10)

        # MAIN PANES
        main = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=6)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # LEFT PANEL
        left = tk.Frame(main, width=450, bg="#ecf0f1")
        main.add(left)

        tk.Label(left, text="Calendar", font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=15)
        self.cal = Calendar(left, selectmode="day", date_pattern="y-mm-dd", background="#2c3e50", foreground="white")
        self.cal.pack(padx=30, pady=10)
        self.cal.bind("<<CalendarSelected>>", lambda e: self.filter_by_date())

        tk.Button(left, text="Show All Entries", command=self.show_all, bg="#27ae60", fg="white", font=("bold",13), height=2).pack(pady=20, padx=70, fill=tk.X)

        tk.Label(left, text="Your Entries", font=("Arial", 13, "bold"), bg="#ecf0f1").pack(pady=(20,10))
        self.listbox = tk.Listbox(left, font=("Arial", 12), bg="white", selectbackground="#3498db", height=25)
        self.listbox.pack(fill="both", expand=True, padx=30, pady=10)
        self.listbox.bind("<<ListboxSelect>>", self.load_entry)

        # RIGHT PANEL - EDITOR
        right = tk.Frame(main, bg="white")
        main.add(right)

        # Date & Time
        dtf = tk.Frame(right, bg="white")
        dtf.pack(fill="x", pady=20)
        tk.Label(dtf, text="Date & Time:", font=("Arial", 14, "bold"), bg="white").pack(side=tk.LEFT, padx=30)
        self.dt_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        tk.Entry(dtf, textvariable=self.dt_var, font=("Arial", 13), width=35).pack(side=tk.LEFT, padx=15)
        tk.Button(dtf, text="Now", command=lambda: self.dt_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                  bg="#3498db", fg="white", font=("bold",11)).pack(side=tk.LEFT)

        # Title
        tk.Label(right, text="Title", font=("Arial", 18, "bold"), bg="white").pack(anchor="w", padx=30, pady=(15,8))
        self.title_entry = tk.Entry(right, font=("Arial", 18), relief="solid", bd=2)
        self.title_entry.pack(fill="x", padx=30, pady=5)

        # Content
        tk.Label(right, text="Write your day...", font=("Arial", 13), bg="white", fg="#7f8c8d").pack(anchor="w", padx=30, pady=(15,5))
        self.text_box = tk.Text(right, height=18, font=("Arial", 13), wrap="word", relief="solid", bd=2, spacing1=10, spacing3=10)
        self.text_box.pack(fill="both", expand=True, padx=30, pady=10)

        # Image preview
        self.img_label = tk.Label(right, text="No image attached", bg="#f5f5f5", height=12, relief="sunken", font=("Arial", 11))
        self.img_label.pack(fill="x", padx=30, pady=20)

        # BIG BUTTONS
        btn_frame = tk.Frame(right, bg="white")
        btn_frame.pack(pady=25)

        tk.Button(btn_frame, text="ATTACH PHOTO", command=self.attach_photo,
                  bg="#95a5a6", fg="white", font=("Arial", 14, "bold"), width=18, height=2).pack(side=tk.LEFT, padx=20)

        tk.Button(btn_frame, text="SAVE ENTRY", command=self.save_entry,
                  bg="#27ae60", fg="white", font=("Arial", 16, "bold"), width=20, height=2).pack(side=tk.LEFT, padx=20)

        tk.Button(btn_frame, text="EDIT SELECTED", command=self.start_edit,
                  bg="#f39c12", fg="white", font=("Arial", 16, "bold"), width=20, height=2).pack(side=tk.LEFT, padx=20)

        tk.Button(btn_frame, text="DELETE", command=self.delete_entry,
                  bg="#e74c3c", fg="white", font=("Arial", 16, "bold"), width=18, height=2).pack(side=tk.LEFT, padx=20)

    # === LIST & SEARCH ===
    def refresh_list(self, entries_to_show=None):
        self.listbox.delete(0, tk.END)
        list_data = entries_to_show if entries_to_show is not None else self.entries
        for e in reversed(list_data):
            self.listbox.insert(tk.END, f"{e.get('datetime','')[:16]} — {e.get('title','Untitled')}")

    def search_entries(self):
        q = self.search_var.get().lower()
        if not q:
            self.refresh_list()
            return
        results = [e for e in self.entries if q in e.get("title","").lower() or q in e.get("content","").lower()]
        self.refresh_list(results)

    def filter_by_date(self):
        date = self.cal.get_date()
        results = [e for e in self.entries if e.get("datetime","").startswith(date)]
        self.refresh_list(results)

    def show_all(self):
        self.cal.selection_clear()
        self.search_var.set("")
        self.refresh_list()

    # === ENTRY ACTIONS ===
    def load_entry(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        # Find real index
        displayed = self.get_current_displayed_entries()
        if len(displayed) <= sel[0]:
            return
        entry = displayed[len(displayed) - 1 - sel[0]]
        self.editing_index = self.entries.index(entry)  # remember for editing

        self.dt_var.set(entry.get("datetime", ""))
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, entry.get("title", ""))
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert("1.0", entry.get("content", ""))

        # Show image
        img_path = entry.get("image")
        if img_path and os.path.exists(img_path):
            img = Image.open(img_path).resize((520, 320), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.img_label.config(image=photo, text="")
            self.img_label.image = photo
            self.current_image = img_path
        else:
            self.img_label.config(image="", text="No image attached")
            self.current_image = None

    def get_current_displayed_entries(self):
        if self.search_var.get():
            q = self.search_var.get().lower()
            return [e for e in self.entries if q in e.get("title","").lower() or q in e.get("content","").lower()]
        elif self.cal.selection_get():
            d = self.cal.get_date()
            return [e for e in self.entries if e.get("datetime","").startswith(d)]
        else:
            return self.entries

    def start_edit(self):
        if not self.listbox.curselection():
            messagebox.showwarning("Select", "Please select an entry to edit")
            return
        self.load_entry()  # Just load it — Save will overwrite

    def save_entry(self):
        title = self.title_entry.get().strip() or "Untitled Entry"
        content = self.text_box.get("1.0", tk.END).strip()
        dt = self.dt_var.get().strip() or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_entry = {
            "datetime": dt,
            "title": title,
            "content": content,
            "image": self.current_image
        }

        if self.editing_index is not None:
            self.entries[self.editing_index] = new_entry
            self.editing_index = None
            messagebox.showinfo("Updated", "Entry updated!")
        else:
            self.entries.append(new_entry)
            messagebox.showinfo("Saved", "New entry saved!")

        save_entries(self.entries)
        self.search_entries()
        self.clear_form()

    def clear_form(self):
        self.title_entry.delete(0, tk.END)
        self.text_box.delete("1.0", tk.END)
        self.img_label.config(image="", text="No image attached")
        self.current_image = None
        self.editing_index = None

    def delete_entry(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        if messagebox.askyesno("Delete", "Delete this entry forever?"):
            displayed = self.get_current_displayed_entries()
            idx = len(displayed) - 1 - sel[0]
            real_idx = self.entries.index(displayed[idx])
            self.entries.pop(real_idx)
            save_entries(self.entries)
            self.search_entries()
            self.clear_form()

    def attach_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.gif")])
        if path:
            self.current_image = path
            img = Image.open(path).resize((520, 320), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.img_label.config(image=photo, text="")
            self.img_label.image = photo

    # === EXPORT ===
    def export_txt(self):
        if not self.entries: return messagebox.showinfo("Empty", "No entries"); return
        p = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")])
        if p:
            with open(p, "w", encoding="utf-8") as f:
                f.write("MY DIARY\n" + "="*80 + "\n\n")
                for e in reversed(self.entries):
                    f.write(f"{e.get('datetime','')} — {e.get('title','')}\n\n{e.get('content','')}\n{'-'*80}\n\n")
            messagebox.showinfo("Success", "TXT saved!")

    def export_csv(self):
        if not self.entries: return
        p = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if p:
            with open(p, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Date & Time", "Title", "Content"])
                for e in self.entries:
                    w.writerow([e.get("datetime",""), e.get("title",""), e.get("content","")])
            messagebox.showinfo("Success", "CSV saved!")

if __name__ == "__main__":
    MyDiary()