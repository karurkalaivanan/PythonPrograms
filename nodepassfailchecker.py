import tkinter as tk
import webview

def open_website():
    url = url_entry.get()
    if url:
        webview.create_window("Web Browser", url)
        webview.start()

# Tkinter GUI
root = tk.Tk()
root.title("Web Browser in Tkinter")

tk.Label(root, text="Enter Website URL:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)
url_entry.insert(0, "https://www.google.com")  # Default URL

tk.Button(root, text="Open Website", command=open_website).pack(pady=10)

root.mainloop()
