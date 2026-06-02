import sys
import os
import serial
import serial.tools.list_ports
import esptool
import threading
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QComboBox, QFileDialog, QMessageBox, QProgressBar, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread

# ===============================
#  ESP32 Flasher Core Threads
# ===============================

class ESP32EraserThread(QThread):
    log_signal = pyqtSignal(str)
    done_signal = pyqtSignal(bool)

    def __init__(self, port, chip):
        super().__init__()
        self.port = port
        self.chip = chip

    def run(self):
        try:
            self.log_signal.emit(f"🧹 Erasing flash on {self.port} ({self.chip})...")
            esptool.main(["--chip", self.chip, "--port", self.port, "--baud", "921600", "erase_flash"])
            self.log_signal.emit("✅ Flash erase completed.")
            self.done_signal.emit(True)
        except Exception as e:
            self.log_signal.emit(f"❌ Erase failed: {e}")
            self.done_signal.emit(False)


class ESP32FlashThread(QThread):
    log_signal = pyqtSignal(str)
    done_signal = pyqtSignal(bool)
    progress_signal = pyqtSignal(int)

    def __init__(self, port, chip, bin_map):
        super().__init__()
        self.port = port
        self.chip = chip
        self.bin_map = bin_map

    def run(self):
        try:
            args = [
                "--chip", self.chip,
                "--port", self.port,
                "--baud", "921600",
                "--before", "default_reset",
                "--after", "hard_reset",
                "write_flash", "-z"
            ]
            for addr, file in self.bin_map.items():
                args.extend([addr, file])
                self.log_signal.emit(f"📦 Mapping {file} @ {addr}")

            self.log_signal.emit("\n🚀 Flashing started...\n")
            esptool.main(args)
            self.log_signal.emit("✅ Flashing completed successfully!")
            self.done_signal.emit(True)
        except Exception as e:
            self.log_signal.emit(f"❌ Flashing failed: {e}")
            self.done_signal.emit(False)


class SerialMonitorThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, port, baudrate=115200):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self._stop_flag = False

    def run(self):
        try:
            with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                self.log_signal.emit(f"📡 Serial monitor started on {self.port} @ {self.baudrate} baud\n")
                while not self._stop_flag:
                    if ser.in_waiting:
                        data = ser.read(ser.in_waiting).decode(errors="ignore")
                        self.log_signal.emit(data)
                    time.sleep(0.1)
        except Exception as e:
            self.log_signal.emit(f"❌ Serial error: {e}")

    def stop(self):
        self._stop_flag = True


# ===============================
#  GUI Application
# ===============================

class ESP32FlasherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔥 ESP32/ESP32-S3 Flasher Tool")
        self.resize(950, 650)

        self.port_combo = QComboBox()
        self.chip_combo = QComboBox()
        self.folder_path = None
        self.serial_thread = None

        self.tabs = QTabWidget()
        self.log_box = QTextEdit(readOnly=True)
        self.serial_box = QTextEdit(readOnly=True)
        self.progress_bar = QProgressBar()

        self.init_ui()
        self.refresh_ports()

    # ------------------------------
    # UI Setup
    # ------------------------------
    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # === Top Controls ===
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Port:"))
        top_layout.addWidget(self.port_combo)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_ports)
        top_layout.addWidget(refresh_btn)

        top_layout.addWidget(QLabel("Chip:"))
        self.chip_combo.addItems(["esp32", "esp32-s2", "esp32-s3", "esp32-c3"])
        self.chip_combo.setCurrentText("esp32-s3")
        top_layout.addWidget(self.chip_combo)

        folder_btn = QPushButton("📁 Select Firmware Folder")
        folder_btn.clicked.connect(self.select_folder)
        top_layout.addWidget(folder_btn)

        erase_btn = QPushButton("🧹 Erase Flash")
        erase_btn.clicked.connect(self.erase_flash)
        top_layout.addWidget(erase_btn)

        flash_btn = QPushButton("⚡ Flash Firmware")
        flash_btn.clicked.connect(self.flash_firmware)
        top_layout.addWidget(flash_btn)

        serial_btn = QPushButton("🛰️ Open Serial Monitor")
        serial_btn.clicked.connect(self.open_serial)
        top_layout.addWidget(serial_btn)

        save_btn = QPushButton("💾 Save Log")
        save_btn.clicked.connect(self.save_log)
        top_layout.addWidget(save_btn)

        main_layout.addLayout(top_layout)

        # === Tabs (Logs & Serial) ===
        self.tabs.addTab(self.log_box, "Flasher Log")
        self.tabs.addTab(self.serial_box, "Serial Monitor")
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.progress_bar)

    # ------------------------------
    # Port Handling
    # ------------------------------
    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for p in sorted(ports, key=lambda x: x.device):
            desc = p.description.lower()
            if "cdc" in desc or "esp32-s3" in desc:
                self.port_combo.insertItem(0, p.device)
            else:
                self.port_combo.addItem(p.device)
        if not ports:
            self.port_combo.addItem("No ports found")

    # ------------------------------
    # Flashing Logic
    # ------------------------------
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Firmware Folder")
        if folder:
            self.folder_path = folder
            self.log_box.append(f"📂 Selected Folder: {folder}\n")

    def get_bin_map(self):
        """Auto-detect typical ESP32 binary files"""
        if not self.folder_path:
            QMessageBox.warning(self, "Warning", "Select firmware folder first.")
            return None

        mapping = {}
        for file in os.listdir(self.folder_path):
            path = os.path.join(self.folder_path, file)
            if "bootloader" in file:
                mapping["0x0000"] = path
            elif "partition" in file:
                mapping["0x8000"] = path
            elif "boot_app0" in file:
                mapping["0xe000"] = path
            elif file.endswith(".bin"):
                mapping["0x10000"] = path

        if not mapping:
            QMessageBox.warning(self, "Warning", "No .bin files found in folder.")
            return None
        return mapping

    def erase_flash(self):
        port = self.port_combo.currentText()
        chip = self.chip_combo.currentText()
        if "No" in port:
            QMessageBox.warning(self, "Warning", "No COM port selected.")
            return
        self.log_box.append(f"🧹 Starting erase on {port} ({chip})...\n")

        self.eraser = ESP32EraserThread(port, chip)
        self.eraser.log_signal.connect(self.log_box.append)
        self.eraser.done_signal.connect(lambda _: self.log_box.append("✨ Erase done.\n"))
        self.eraser.start()

    def flash_firmware(self):
        port = self.port_combo.currentText()
        chip = self.chip_combo.currentText()
        bin_map = self.get_bin_map()
        if not bin_map:
            return

        self.flashing = ESP32FlashThread(port, chip, bin_map)
        self.flashing.log_signal.connect(self.log_box.append)
        self.flashing.done_signal.connect(lambda _: self.log_box.append("✅ Flashing Done.\n"))
        self.flashing.start()

    # ------------------------------
    # Serial Monitor
    # ------------------------------
    def open_serial(self):
        port = self.port_combo.currentText()
        if not port or "No" in port:
            QMessageBox.warning(self, "Warning", "Select a valid COM port.")
            return

        if self.serial_thread and self.serial_thread.isRunning():
            self.serial_thread.stop()
            self.serial_thread = None
            self.serial_box.append("🛑 Serial monitor stopped.\n")
        else:
            self.serial_thread = SerialMonitorThread(port)
            self.serial_thread.log_signal.connect(self.serial_box.insertPlainText)
            self.serial_thread.start()

    # ------------------------------
    # Log Saving
    # ------------------------------
    def save_log(self):
        content = self.log_box.toPlainText()
        if not content.strip():
            QMessageBox.information(self, "Info", "No log data to save.")
            return
        try:
            with open("ESP32_Flasher_Log.txt", "w", encoding="utf-8") as f:
                f.write(content)
            QMessageBox.information(self, "Success", "Log saved as ESP32_Flasher_Log.txt")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# ===============================
#  Main
# ===============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ESP32FlasherApp()
    win.show()
    sys.exit(app.exec_())
