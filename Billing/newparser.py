import tkinter as tk
from tkinter import filedialog, messagebox


def open_file():
    filepath = filedialog.askopenfilename(
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )

    if not filepath:
        return

    try:
        with open(filepath, "r") as f:
            lines = f.readlines()

        text_box.delete("1.0", tk.END)

        for line in lines:

            # Replace "_" with newline
            line = line.replace("_", "\n")

            parts = line.split("\n")

            for part in parts:

                if "7e" in part.lower():
                    frame = part.lower().split("7e", 1)[1]
                    cleaned = "7e " + frame.strip()
                    text_box.insert(tk.END, cleaned + "\n")
                else:
                    text_box.insert(tk.END, part.strip() + "\n")

        messagebox.showinfo("Success", "Processing completed")

    except Exception as e:
        messagebox.showerror("Error", str(e))


def save_file():
    data = text_box.get("1.0", tk.END)

    filepath = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")]
    )

    if not filepath:
        return

    with open(filepath, "w") as f:
        f.write(data)

    messagebox.showinfo("Saved", "File saved successfully")


root = tk.Tk()
root.title("DLMS Log Formatter")
root.geometry("900x550")


# Buttons
top = tk.Frame(root)
top.pack(pady=10)

tk.Button(top, text="Open File", width=15, command=open_file).pack(side=tk.LEFT, padx=10)
tk.Button(top, text="Save File", width=15, command=save_file).pack(side=tk.LEFT, padx=10)


# Text frame
frame = tk.Frame(root)
frame.pack(fill="both", expand=True, padx=10, pady=10)


# Scrollbars
scroll_y = tk.Scrollbar(frame)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

scroll_x = tk.Scrollbar(frame, orient="horizontal")
scroll_x.pack(side=tk.BOTTOM, fill=tk.X)


# Text box
text_box = tk.Text(
    frame,
    wrap="none",
    font=("Consolas", 10),
    yscrollcommand=scroll_y.set,
    xscrollcommand=scroll_x.set
)

text_box.pack(fill="both", expand=True)

scroll_y.config(command=text_box.yview)
scroll_x.config(command=text_box.xview)


root.mainloop()