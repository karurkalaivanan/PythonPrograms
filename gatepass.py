import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime
import csv
import os
import platform

CSV_FILE = "materials.csv"
CSV_MATERIAL = "materials_list.csv"


class MaterialGatePass:
    def __init__(self, root):
        self.root = root
        self.root.title("Material Inward & Outward Management")

        # Maximize Window Cross-Platform
        try:
            self.root.state("zoomed")  # Windows
        except tk.TclError:
            try:
                self.root.attributes("-zoomed", True)  # Linux
            except:
                self.root.state("normal")  # fallback

        self.material_list = []  # Stores material records
        self.load_data()  # Load data from CSV
        

        # Configure Grid for Auto-Resize
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)  # Make sure row 2 (the table) can expand


        # ======= UI Components =======

        # Material Name
        frame1 = ttk.Frame(root, padding=10)
        frame1.grid(row=0, column=0, sticky="ew")
        frame1.columnconfigure(1, weight=1)

        ttk.Label(frame1, text="Material Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.material_var = tk.StringVar()
        self.material_entry = ttk.Combobox(frame1, textvariable=self.material_var)
        self.material_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.material_entry['values'] = self.get_material_names()
        self.material_entry['values'] = self.get_material_names()
        self.material_entry.set('')  # Optional: Clear on start

        self.material_entry.set('')  # Optional: Clear on start

        # Quantity
        ttk.Label(frame1, text="Quantity:").grid(
            row=0, column=2, padx=5, pady=5, sticky="w"
        )
        self.qty_var = tk.IntVar()
        self.qty_entry = ttk.Entry(frame1, textvariable=self.qty_var, width=10)
        self.qty_entry.grid(row=0, column=3, padx=5, pady=5)

        # Date Selection
        ttk.Label(frame1, text="Date:").grid(
            row=0, column=4, padx=5, pady=5, sticky="w"
        )
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.date_entry = ttk.Entry(frame1, textvariable=self.date_var, width=15)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)

        self.date_button = ttk.Button(
            frame1, text="Pick Date", command=self.select_date
        )
        self.date_button.grid(row=0, column=6, padx=5, pady=5)

        # Transaction Type (Inward/Outward)
        ttk.Label(frame1, text="Type:").grid(
            row=0, column=7, padx=5, pady=5, sticky="w"
        )
        self.type_var = tk.StringVar(value="Inward")
        self.type_combobox = ttk.Combobox(
            frame1, textvariable=self.type_var, values=["Inward", "Outward"], width=10
        )
        self.type_combobox.grid(row=0, column=8, padx=5, pady=5)

        # Remark
        ttk.Label(frame1, text="Remark:").grid(
            row=0, column=9, padx=5, pady=5, sticky="w"
        )
        self.remark_var = tk.StringVar()
        self.remark_entry = ttk.Entry(frame1, textvariable=self.remark_var, width=30)
        self.remark_entry.grid(row=0, column=10, padx=5, pady=5)

        # Send By
        ttk.Label(frame1, text="Send By:").grid(
            row=0, column=11, padx=5, pady=5, sticky="w"
        )
        self.send_by_var = tk.StringVar()
        self.send_by_entry = ttk.Entry(frame1, textvariable=self.send_by_var, width=20)
        self.send_by_entry.grid(row=0, column=12, padx=5, pady=5)

        # Buttons
        self.add_button = ttk.Button(frame1, text="Add Entry", command=self.add_entry)
        self.add_button.grid(row=0, column=13, padx=5, pady=5)

        self.update_button = ttk.Button(
            frame1, text="Update Entry", command=self.update_entry
        )
        self.update_button.grid(row=0, column=14, padx=5, pady=5)
        self.update_button["state"] = "disabled"

        # Search Section
        frame2 = ttk.Frame(root, padding=10)
        frame2.grid(row=1, column=0, sticky="ew")
        frame2.columnconfigure(1, weight=1)

        ttk.Label(frame2, text="Search by Material or Date:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(frame2, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.search_button = ttk.Button(
            frame2, text="Search", command=self.search_entries
        )
        self.search_button.grid(row=0, column=2, padx=5, pady=5)

        self.show_all_button = ttk.Button(
            frame2, text="Show All", command=self.show_all_entries
        )
        self.show_all_button.grid(row=0, column=3, padx=5, pady=5)

        # Material List Table
        frame3 = ttk.Frame(root, padding=10)
        frame3.grid(row=2, column=0, sticky="nsew")
        frame3.columnconfigure(0, weight=1)
        frame3.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            frame3,
            columns=("Material", "Quantity", "Date", "Type", "Remark", "Send By"),
            show="headings",
        )
        self.tree.heading("Material", text="Material Name")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Remark", text="Remark")
        self.tree.heading("Send By", text="Send By")

        self.tree.column("Material", width=200)
        self.tree.column("Quantity", width=100)
        self.tree.column("Date", width=150)
        self.tree.column("Type", width=100)
        self.tree.column("Remark", width=250)
        self.tree.column("Send By", width=150)

        tree_scroll = ttk.Scrollbar(frame3, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=tree_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.on_row_selected)

        self.show_all_entries()

        self.delete_button = ttk.Button(frame1, text="Delete Entry", command=self.delete_entry)
        self.delete_button.grid(row=0, column=15, padx=5, pady=5)
    
    def delete_entry(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No item selected to delete.")
            return

        # Ask for password
        def verify_and_delete():
            if pwd_entry.get() == "admin123":  # <== Change this password as needed
                index = self.tree.index(selected[0])
                self.tree.delete(selected[0])
                del self.material_list[index]
                self.save_to_csv()
                self.clear_form()
                pwd_window.destroy()
                messagebox.showinfo("Success", "Entry deleted successfully.")
            else:
                messagebox.showerror("Error", "Incorrect password.")
                pwd_window.lift()

        # Create password popup
        pwd_window = tk.Toplevel(self.root)
        pwd_window.title("Confirm Delete")
        pwd_window.grab_set()  # Makes it modal

        ttk.Label(pwd_window, text="Enter password to confirm deletion:").pack(padx=10, pady=10)
        pwd_entry = ttk.Entry(pwd_window, show="*")
        pwd_entry.pack(padx=10, pady=5)
        ttk.Button(pwd_window, text="Delete", command=verify_and_delete).pack(pady=10)
        pwd_entry.focus()


    def get_material_names(self):
        # "Returns a list of unique material names from loaded data"
        return sorted(list(set(entry[0] for entry in self.material_list)))
   

    def select_date(self):
        # """Opens a calendar to pick a date"""
        top = tk.Toplevel(self.root)
        top.title("Select Date")

        def grab_date():
            selected_date = cal.selection_get()  # This returns a datetime.date object
            self.date_var.set(selected_date.strftime("%Y-%m-%d"))  # Enforce format
            top.destroy()

        cal = Calendar(
            top,
            selectmode="day",
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
            date_pattern="yyyy-mm-dd"  # This affects what is shown, not what is returned
        )
        cal.pack(pady=10)
        ttk.Button(top, text="Select", command=grab_date).pack(pady=5)


    def add_entry(self):
        """Adds a new entry to the material list and saves to CSV"""
        material = self.material_var.get().strip()
        qty = self.qty_var.get()
        date = self.date_var.get()
        trans_type = self.type_var.get()
        remark = self.remark_var.get().strip()
        send_by = self.send_by_var.get().strip()

        if not material or not date:
            messagebox.showerror("Error", "Material name and date are required!")
            return

        entry = (material, qty, date, trans_type, remark, send_by)
        self.material_list.append(entry)
        self.tree.insert("", tk.END, values=entry)
        self.save_to_csv()

        self.clear_form()
        # Refresh the material name combobox suggestions
        self.material_entry['values'] = self.get_material_names()


    def on_row_selected(self, event):
        """Populates form when a row is selected"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item["values"]

            self.material_var.set(values[0])
            self.qty_var.set(values[1])
            self.date_var.set(values[2])
            self.type_var.set(values[3])
            self.remark_var.set(values[4])
            self.send_by_var.set(values[5])

            self.update_button["state"] = "normal"
            self.add_button["state"] = "disabled"

    def update_entry(self):
        """Updates selected entry"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No item selected to update.")
            return

        index = self.tree.index(selected[0])

        updated_entry = (
            self.material_var.get().strip(),
            self.qty_var.get(),
            self.date_var.get(),
            self.type_var.get(),
            self.remark_var.get().strip(),
            self.send_by_var.get().strip(),
        )

        if not updated_entry[0] or not updated_entry[2]:
            messagebox.showerror("Error", "Material name and date are required!")
            return

        # Update memory and UI
        self.material_list[index] = updated_entry
        self.tree.item(selected[0], values=updated_entry)
        self.save_to_csv()

        self.clear_form()

        self.update_button["state"] = "disabled"
        self.add_button["state"] = "normal"
        self.tree.selection_remove(selected[0])

    def search_entries(self):
        """Searches materials by name or date"""
        query = self.search_var.get().strip().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)

        for entry in self.material_list:
            if query in entry[0].lower() or query in entry[2]:
                self.tree.insert("", tk.END, values=entry)

    def show_all_entries(self):
        """Displays all entries in the table"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        for entry in self.material_list:
            self.tree.insert("", tk.END, values=entry)

    def save_to_csv(self):
        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                ["Material", "Quantity", "Date", "Type", "Remark", "Send By"]
            )
            writer.writerows(self.material_list)

    def load_data(self):
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, "r") as file:
                reader = csv.reader(file)
                next(reader, None)
                self.material_list = [tuple(row) for row in reader]

    def clear_form(self):
        self.material_var.set("")
        self.qty_var.set(0)
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.type_var.set("Inward")
        self.remark_var.set("")
        self.send_by_var.set("")


if __name__ == "__main__":
    root = tk.Tk()
    app = MaterialGatePass(root)
    root.mainloop()
