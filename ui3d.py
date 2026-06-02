import tkinter as tk
from tkinter import ttk
import serial
import threading
import re
import numpy as np

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt

# ---------------- SERIAL CONFIG ----------------
SERIAL_PORT = "COM6"      # Change COM port
BAUD_RATE = 115200

# ---------------- GLOBAL VALUES ----------------
x_val = 0
y_val = 0
z_val = 0

# ---------------- TKINTER WINDOW ----------------
root = tk.Tk()
root.title("Live 3D Motion Viewer")
root.geometry("1000x700")

# ---------------- LABELS ----------------
info_frame = ttk.Frame(root)
info_frame.pack(side=tk.TOP, fill=tk.X)

x_label = ttk.Label(info_frame, text="X: 0", font=("Arial", 14))
x_label.pack(side=tk.LEFT, padx=20)

y_label = ttk.Label(info_frame, text="Y: 0", font=("Arial", 14))
y_label.pack(side=tk.LEFT, padx=20)

z_label = ttk.Label(info_frame, text="Z: 0", font=("Arial", 14))
z_label.pack(side=tk.LEFT, padx=20)

status_label = ttk.Label(info_frame, text="Waiting...", font=("Arial", 14))
status_label.pack(side=tk.LEFT, padx=20)

# ---------------- MATPLOTLIB FIGURE ----------------
fig = plt.figure(figsize=(7, 6))
ax = fig.add_subplot(111, projection='3d')

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# ---------------- CREATE CUBE ----------------
cube_vertices = np.array([
    [-1, -1, -1],
    [ 1, -1, -1],
    [ 1,  1, -1],
    [-1,  1, -1],
    [-1, -1,  1],
    [ 1, -1,  1],
    [ 1,  1,  1],
    [-1,  1,  1]
])

faces = [
    [cube_vertices[j] for j in [0,1,2,3]],
    [cube_vertices[j] for j in [4,5,6,7]],
    [cube_vertices[j] for j in [0,1,5,4]],
    [cube_vertices[j] for j in [2,3,7,6]],
    [cube_vertices[j] for j in [1,2,6,5]],
    [cube_vertices[j] for j in [4,7,3,0]]
]

# ---------------- ROTATION FUNCTIONS ----------------
def rotation_matrix_x(angle):
    rad = np.radians(angle)
    return np.array([
        [1, 0, 0],
        [0, np.cos(rad), -np.sin(rad)],
        [0, np.sin(rad), np.cos(rad)]
    ])

def rotation_matrix_y(angle):
    rad = np.radians(angle)
    return np.array([
        [np.cos(rad), 0, np.sin(rad)],
        [0, 1, 0],
        [-np.sin(rad), 0, np.cos(rad)]
    ])

def rotation_matrix_z(angle):
    rad = np.radians(angle)
    return np.array([
        [np.cos(rad), -np.sin(rad), 0],
        [np.sin(rad), np.cos(rad), 0],
        [0, 0, 1]
    ])

# ---------------- UPDATE 3D OBJECT ----------------
def update_plot():
    global x_val, y_val, z_val

    ax.clear()

    # Rotation matrices
    Rx = rotation_matrix_x(y_val)
    Ry = rotation_matrix_y(x_val)
    Rz = rotation_matrix_z(z_val)

    rotation = Rx @ Ry @ Rz

    rotated_vertices = np.dot(cube_vertices, rotation.T)

    cube_faces = [
        [rotated_vertices[j] for j in [0,1,2,3]],
        [rotated_vertices[j] for j in [4,5,6,7]],
        [rotated_vertices[j] for j in [0,1,5,4]],
        [rotated_vertices[j] for j in [2,3,7,6]],
        [rotated_vertices[j] for j in [1,2,6,5]],
        [rotated_vertices[j] for j in [4,7,3,0]]
    ]

    ax.add_collection3d(
        Poly3DCollection(
            cube_faces,
            facecolors='cyan',
            linewidths=1,
            edgecolors='black',
            alpha=0.7
        )
    )

    ax.set_xlim([-3, 3])
    ax.set_ylim([-3, 3])
    ax.set_zlim([-3, 3])

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    ax.set_title("Live 3D Motion")

    canvas.draw()

    root.after(50, update_plot)

# ---------------- SERIAL READER THREAD ----------------
def serial_thread():
    global x_val, y_val, z_val

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        status_label.config(text="Connected")

        while True:
            line = ser.readline().decode(errors='ignore').strip()

            print(line)

            match = re.search(r'X:(-?\d+)\s+Y:(-?\d+)\s+Z:(-?\d+)', line)

            if match:
                x_val = int(match.group(1))
                y_val = int(match.group(2))
                z_val = int(match.group(3))

                x_label.config(text=f"X: {x_val}")
                y_label.config(text=f"Y: {y_val}")
                z_label.config(text=f"Z: {z_val}")

            if "Move detected" in line:
                status_label.config(text="Movement Detected")

            if "stable" in line:
                status_label.config(text="Stable Position")

    except Exception as e:
        status_label.config(text=f"Error: {e}")
        print(e)

# ---------------- START THREAD ----------------
threading.Thread(target=serial_thread, daemon=True).start()

# ---------------- START PLOT ----------------
update_plot()

# ---------------- MAIN LOOP ----------------
root.mainloop()
