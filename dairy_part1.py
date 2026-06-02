import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from tkcalendar import Calendar
import json
import os
from datetime import datetime, date
import tkinter as tk
from tkinter import messagebox, filedialog

# File for saving diary entries
DIARY_FILE = "professional_diary.json"

class ProfessionalDiary(ttk.Window):
    def __init__(self):
        super().__init__(themename="litera")  # clean & professional theme
        self.title("Daily Journal – Personal Events & Notes")
        self.geometry("1100x750")
        self.minsize(950, 650)
        self.position_center()

        # Load data
        self.diary_data = self.load_entries()
        self.current_date = None

        self.create_widgets()
        self.load_today()

    def create_widgets(self):
        # Header
        header = ttk.Label(
            self,
            text="Daily Journal",
            font=("Helvetica", 24, "bold"),
            bootstyle="primary",
            anchor="center"
        )
        header.pack(pady=(20, 10))

        # Main content
        main = ttk.Frame(self, padding=20)
        main.pack(fill="both", expand=True)

        # ── Left: Calendar + controls ──
        # Use plain tk.Frame as parent for Calendar to avoid ttkbootstrap conflict
        left = tk.Frame(main, width=340, bg="#f8f9fa")
        left.pack(side="left", fill="y", padx=(0, 20))

        ttk.Label(left, text="Calendar", font=("Helvetica", 16, "bold")).pack(pady=(0, 10))

        self.cal = Calendar(
            left,
            selectmode="day",
            date_pattern="yyyy-mm-dd",
            font="Helvetica 11",
            selectbackground="#4e73df",
            selectforeground="white",
            background="white",
            foreground="#343a40",
            weekendbackground="#e9ecef",
            othermonthforeground="#adb5bd",
            bordercolor="#dee2e6",
            headersforeground="#495057",
            normalbackground="white",
            normalforeground="#212529"
        )
        self.cal.pack(pady=10, fill="both", expand=True)

        # Mark dates with entries
        self.mark_dates()

        # Buttons below calendar
        btn_frame_left = ttk.Frame(left)
        btn_frame_left.pack(fill="x", pady=10)

        ttk.Button(btn_frame_left, text="Today", bootstyle=INFO, command=self.go_to_today).pack(side="left", padx=5)
        ttk.Button(btn_frame_left, text="New Entry", bootstyle=SUCCESS, command=self.clear_for_new).pack(side="left", padx=5)

        # ── Right: Editor + status ──
        right = ttk.Frame(main)
        right.pack(side="left", fill="both", expand=True)

        # Date & status
        top_right = ttk.Frame(right)
        top_right.pack(fill="x", pady=(0, 10))

        self.date_label = ttk.Label(
            top_right,
            text="Select a date from the calendar",
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        )
        self.date_label.pack(side="left")

        self.status_label = ttk.Label(top_right, text="", bootstyle="secondary")
        self.status_label.pack(side="right")

        # Editor
        self.editor = ScrolledText(
            right,
            font=("Consolas", 12),
            wrap="word",
            autohide=True,
            bootstyle="info"
        )
        self.editor.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        # Bottom buttons
        bottom = ttk.Frame(right)
        bottom.pack(fill="x", pady=10)

        ttk.Button(bottom, text="Save", bootstyle="success-outline", command=self.save_entry).pack(side="left", padx=5)
        ttk.Button(bottom, text="Clear", bootstyle="warning-outline", command=self.clear_editor).pack(side="left", padx=5)
        ttk.Button(bottom, text="Delete", bootstyle="danger-outline", command=self.delete_entry).pack(side="left", padx=5)
        ttk.Button(bottom, text="Export All", bootstyle="info-outline", command=self.export_all).pack(side="right", padx=5)

    def load_entries(self):
        if os.path.exists(DIARY_FILE):
            try:
                with open(DIARY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except:
                pass
        return {}

    def save_entries(self):
        try:
            with open(DIARY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.diary_data, f, indent=2, ensure_ascii=False)
            self.status_label.config(text="Saved successfully", bootstyle="success")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save:\n{e}")
            self.status_label.config(text="Save failed", bootstyle="danger")

    def mark_dates(self):
        for d_str in self.diary_data:
            try:
                y, m, d = map(int, d_str.split("-"))
                self.cal.calevent_create(date(y, m, d), "Entry exists", "has_entry")
            except:
                pass
        self.cal.tag_config("has_entry", background="#cce5ff", foreground="#004085")

    def on_date_select(self, event=None):
        self.current_date = self.cal.get_date()
        self.date_label.config(text=f" {self.current_date}")

        if self.current_date in self.diary_data:
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", self.diary_data[self.current_date])
            self.status_label.config(text="Loaded existing entry", bootstyle="info")
        else:
            self.editor.delete("1.0", tk.END)
            self.status_label.config(text="No entry yet – write something", bootstyle="secondary")

    def save_entry(self):
        if not self.current_date:
            messagebox.showwarning("No date", "Please select a date first.")
            return

        content = self.editor.get("1.0", tk.END).strip()
        if not content:
            messagebox.showinfo("Nothing to save", "The entry is empty.")
            return

        self.diary_data[self.current_date] = content
        self.save_entries()
        self.mark_dates()
        messagebox.showinfo("Saved", f"Entry saved for {self.current_date}")

    def delete_entry(self):
        if not self.current_date:
            return

        if self.current_date not in self.diary_data:
            messagebox.showinfo("No entry", "Nothing to delete on this date.")
            return

        if messagebox.askyesno("Confirm", f"Delete entry for {self.current_date}?"):
            del self.diary_data[self.current_date]
            self.save_entries()
            self.editor.delete("1.0", tk.END)
            self.mark_dates()
            self.status_label.config(text="Entry deleted", bootstyle="warning")

    def clear_editor(self):
        self.editor.delete("1.0", tk.END)

    def go_to_today(self):
        today = date.today().strftime("%Y-%m-%d")
        self.cal.selection_set(today)
        self.on_date_select()

    def clear_for_new(self):
        self.go_to_today()
        self.clear_editor()

    def export_all(self):
        if not self.diary_data:
            messagebox.showinfo("Nothing to export", "No entries yet.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("All files", "*.*")],
            title="Export Diary"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("Daily Journal Export\n")
                f.write("=" * 40 + "\n\n")
                for d in sorted(self.diary_data.keys()):
                    f.write(f"Date: {d}\n")
                    f.write("-" * 30 + "\n")
                    f.write(self.diary_data[d] + "\n\n")
            messagebox.showinfo("Export Successful", f"Saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

if __name__ == "__main__":
    app = ProfessionalDiary()
    app.mainloop()