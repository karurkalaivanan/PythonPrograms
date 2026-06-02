import sys
import os
import serial
import serial.tools.list_ports
import re
import subprocess
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QComboBox, QFileDialog, QMessageBox, QProgressBar, QTabWidget,
    QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread

# ===============================
#  ESP32 Flasher Core Threads
# ===============================

class ESP32EraserThread(QThread):
    """
    Thread to erase the flash memory of the ESP32.
    """
    log_signal = pyqtSignal(str)
    done_signal = pyqtSignal(bool)

    def __init__(self, port, chip, baud):
        super().__init__()
        self.port = port
        self.chip = chip
        self.baud = baud

    def run(self):
        try:
            self.log_signal.emit(f"🧹 Erasing flash on {self.port} ({self.chip}) at {self.baud} baud...\n")
            
            # Use subprocess to run esptool
            cmd = [
                sys.executable, "-m", "esptool",
                "--chip", self.chip,
                "--port", self.port,
                "--baud", self.baud,
                "erase_flash"
            ]
            
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                encoding='utf-8',
                errors='replace'
            )
            
            for line in iter(process.stdout.readline, ''):
                self.log_signal.emit(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                self.log_signal.emit("\n✅ Flash erase completed.")
                self.done_signal.emit(True)
            else:
                self.log_signal.emit(f"\n❌ Erase failed (Process returned code {process.returncode}).")
                self.done_signal.emit(False)
                
        except Exception as e:
            self.log_signal.emit(f"❌ Erase failed: {e}")
            self.done_signal.emit(False)


class ESP32FlashThread(QThread):
    """
    Thread to flash new firmware, capturing real-time progress.
    """
    log_signal = pyqtSignal(str)
    done_signal = pyqtSignal(bool)
    progress_signal = pyqtSignal(int)

    def __init__(self, port, chip, baud, bin_map):
        super().__init__()
        self.port = port
        self.chip = chip
        self.baud = baud
        self.bin_map = bin_map
        # Regex to capture esptool's progress percentage
        self.progress_re = re.compile(r"\((\d+) %\)")

    def run(self):
        try:
            args = [
                sys.executable, "-m", "esptool",
                "--chip", self.chip,
                "--port", self.port,
                "--baud", self.baud,
                "--before", "default_reset",
                "--after", "hard_reset",
                "write_flash", "-z"
            ]
            
            for addr, file in self.bin_map.items():
                args.extend([addr, file])
                self.log_signal.emit(f"📦 Mapping {file} @ {addr}")

            self.log_signal.emit("\n🚀 Flashing started...\n")
            
            process = subprocess.Popen(
                args, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                encoding='utf-8',
                errors='replace'
            )

            for line in iter(process.stdout.readline, ''):
                line_strip = line.strip()
                self.log_signal.emit(line_strip)
                
                # Check for progress
                match = self.progress_re.search(line_strip)
                if match:
                    progress = int(match.group(1))
                    self.progress_signal.emit(progress)
            
            process.wait()
            
            if process.returncode == 0:
                self.log_signal.emit("\n✅ Flashing completed successfully!")
                self.done_signal.emit(True)
            else:
                self.log_signal.emit(f"\n❌ Flashing failed (Process returned code {process.returncode}).")
                self.done_signal.emit(False)
                
        except Exception as e:
            self.log_signal.emit(f"\n❌ Flashing failed: {e}")
            self.done_signal.emit(False)


class SerialMonitorThread(QThread):
    """
    Thread to read from serial port and emit data.
    """
    log_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, port, baudrate):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self._stop_flag = False

    def run(self):
        try:
            with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                self.log_signal.emit(f"📡 Serial monitor started on {self.port} @ {self.baudrate} baud\n\n")
                while not self._stop_flag:
                    if ser.in_waiting:
                        try:
                            data = ser.read(ser.in_waiting).decode(errors="ignore")
                            self.log_signal.emit(data)
                        except Exception as e:
                            # Handle potential read errors without crashing
                            self.error_signal.emit(f"❌ Serial read error: {e}")
                    time.sleep(0.05) # Small sleep to prevent busy-waiting
            self.log_signal.emit("\n\n🛑 Serial monitor stopped.\n")
        except serial.SerialException as e:
            self.error_signal.emit(f"❌ Serial error: {e}")
        except Exception as e:
            self.error_signal.emit(f"❌ Serial monitor failed: {e}")

    def stop(self):
        self._stop_flag = True


# ===============================
#  GUI Application
# ===============================

class ESP32FlasherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔥 ESP32/ESP32-S3 Flasher Tool")
        self.resize(1000, 700)

        # --- Core Components ---
        self.folder_path = None
        self.serial_thread = None
        self.flash_thread = None
        self.erase_thread = None
        
        # --- UI Widgets ---
        self.port_combo = QComboBox()
        self.chip_combo = QComboBox()
        self.flash_baud_combo = QComboBox()
        self.serial_baud_combo = QComboBox()
        
        self.refresh_btn = QPushButton("🔄 Refresh Ports")
        self.folder_btn = QPushButton("📁 Select Firmware Folder")
        self.erase_btn = QPushButton("🧹 Erase Flash")
        self.flash_btn = QPushButton("⚡ Flash Firmware")
        self.serial_btn = QPushButton("🛰️ Open Serial Monitor")
        self.save_log_btn = QPushButton("💾 Save Log")
        
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

        # === Top Controls Grid ===
        controls_layout = QGridLayout()

        # Row 0: Port, Chip, Refresh
        controls_layout.addWidget(QLabel("Port:"), 0, 0)
        controls_layout.addWidget(self.port_combo, 0, 1)
        controls_layout.addWidget(self.refresh_btn, 0, 2)
        controls_layout.addWidget(QLabel("Chip:"), 0, 3)
        self.chip_combo.addItems(["esp32", "esp32s2", "esp32s3", "esp32c3", "esp32c6"])
        self.chip_combo.setCurrentText("esp32s3")
        controls_layout.addWidget(self.chip_combo, 0, 4)

        # Row 1: Flash Baud, Serial Baud, Folder
        controls_layout.addWidget(QLabel("Flash Baud:"), 1, 0)
        self.flash_baud_combo.addItems(["921600", "460800", "115200"])
        controls_layout.addWidget(self.flash_baud_combo, 1, 1)
        self.folder_btn.clicked.connect(self.select_folder)
        controls_layout.addWidget(self.folder_btn, 1, 2)
        
        controls_layout.addWidget(QLabel("Serial Baud:"), 1, 3)
        self.serial_baud_combo.addItems(["115200", "9600", "74880", "230400", "921600"])
        controls_layout.addWidget(self.serial_baud_combo, 1, 4)

        # Set column 1 to stretch
        controls_layout.setColumnStretch(1, 1)
        controls_layout.setColumnStretch(4, 1)
        
        main_layout.addLayout(controls_layout)

        # === Action Buttons ===
        action_layout = QHBoxLayout()
        self.erase_btn.clicked.connect(self.erase_flash)
        action_layout.addWidget(self.erase_btn)
        
        self.flash_btn.clicked.connect(self.flash_firmware)
        action_layout.addWidget(self.flash_btn)
        
        self.serial_btn.clicked.connect(self.toggle_serial)
        action_layout.addWidget(self.serial_btn)
        
        self.save_log_btn.clicked.connect(self.save_log)
        action_layout.addWidget(self.save_log_btn)
        main_layout.addLayout(action_layout)

        # === Tabs (Logs & Serial) ===
        self.tabs.addTab(self.log_box, "Flasher Log")
        self.tabs.addTab(self.serial_box, "Serial Monitor")
        main_layout.addWidget(self.tabs)
        
        # === Progress Bar ===
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)
        
    def set_controls_enabled(self, enabled):
        """Enable or disable UI controls during operations."""
        self.port_combo.setEnabled(enabled)
        self.chip_combo.setEnabled(enabled)
        self.flash_baud_combo.setEnabled(enabled)
        self.refresh_btn.setEnabled(enabled)
        self.folder_btn.setEnabled(enabled)
        self.erase_btn.setEnabled(enabled)
        self.flash_btn.setEnabled(enabled)
        self.serial_btn.setEnabled(enabled)

    # ------------------------------
    # Port Handling
    # ------------------------------
    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        preferred_ports = []
        other_ports = []
        
        for p in sorted(ports, key=lambda x: x.device):
            desc = p.description.lower()
            if "esp32" in desc or "usb-jtag" in desc or "serial" in desc or "uart" in desc:
                preferred_ports.append(p.device)
            else:
                other_ports.append(p.device)
        
        self.port_combo.addItems(preferred_ports)
        self.port_combo.addItems(other_ports)

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
            # Try to pre-fill map
            self.get_bin_map(log_to_box=True)

    def get_bin_map(self, log_to_box=False):
        """Auto-detect typical ESP32 binary files"""
        if not self.folder_path:
            QMessageBox.warning(self, "Warning", "Select firmware folder first.")
            return None

        mapping = {}
        # Standard addresses
        address_map = {
            "bootloader": "0x0000",
            "partition": "0x8000",
            "boot_app0": "0xe000",
        }
        
        # Find files matching the keywords
        for file in os.listdir(self.folder_path):
            path = os.path.join(self.folder_path, file)
            for key, addr in address_map.items():
                if key in file and file.endswith(".bin"):
                    mapping[addr] = path
                    break
            else:
                # Assume main application file
                if file.endswith(".bin") and "bootloader" not in file and "partition" not in file:
                    mapping["0x10000"] = path

        if not mapping:
            QMessageBox.warning(self, "Warning", "No .bin files (bootloader, partition, app) found in folder.")
            return None
        
        if log_to_box:
            self.log_box.append("Found firmware files:")
            for addr, file in mapping.items():
                self.log_box.append(f"  -> {addr}: {os.path.basename(file)}")
            self.log_box.append("")
            
        return mapping

    def erase_flash(self):
        port = self.port_combo.currentText()
        chip = self.chip_combo.currentText()
        baud = self.flash_baud_combo.currentText()
        
        if "No" in port:
            QMessageBox.warning(self, "Warning", "No COM port selected.")
            return

        self.log_box.clear()
        self.tabs.setCurrentWidget(self.log_box)
        self.set_controls_enabled(False)

        self.erase_thread = ESP32EraserThread(port, chip, baud)
        self.erase_thread.log_signal.connect(self.log_box.append)
        self.erase_thread.done_signal.connect(self.on_operation_complete)
        self.erase_thread.start()

    def flash_firmware(self):
        port = self.port_combo.currentText()
        chip = self.chip_combo.currentText()
        baud = self.flash_baud_combo.currentText()
        
        bin_map = self.get_bin_map()
        if not bin_map:
            return

        self.log_box.clear()
        self.progress_bar.setValue(0)
        self.tabs.setCurrentWidget(self.log_box)
        self.set_controls_enabled(False)

        self.flash_thread = ESP32FlashThread(port, chip, baud, bin_map)
        self.flash_thread.log_signal.connect(self.log_box.append)
        self.flash_thread.progress_signal.connect(self.progress_bar.setValue)
        self.flash_thread.done_signal.connect(self.on_operation_complete)
        self.flash_thread.start()

    def on_operation_complete(self, success):
        """Re-enable controls when erase/flash thread is done."""
        self.set_controls_enabled(True)
        if not success:
            QMessageBox.warning(self, "Operation Failed", "The operation failed. Check the log for details.")
        if self.flash_thread and not success:
             self.progress_bar.setValue(0)
        self.flash_thread = None
        self.erase_thread = None

    # ------------------------------
    # Serial Monitor
    # ------------------------------
    def toggle_serial(self):
        # --- Stop Serial Monitor ---
        if self.serial_thread and self.serial_thread.isRunning():
            self.serial_thread.stop()
            self.serial_thread.wait() # Wait for thread to finish
            self.serial_thread = None
            self.serial_btn.setText("🛰️ Open Serial Monitor")
            self.set_controls_enabled(True) # Re-enable port/chip controls
        
        # --- Start Serial Monitor ---
        else:
            port = self.port_combo.currentText()
            baud = int(self.serial_baud_combo.currentText())
            
            if not port or "No" in port:
                QMessageBox.warning(self, "Warning", "Select a valid COM port.")
                return

            self.serial_box.clear()
            self.tabs.setCurrentWidget(self.serial_box)
            
            self.serial_thread = SerialMonitorThread(port, baud)
            self.serial_thread.log_signal.connect(self.serial_box.insertPlainText)
            self.serial_thread.error_signal.connect(self.on_serial_error)
            self.serial_thread.finished.connect(self.on_serial_closed) # Handle unexpected close
            self.serial_thread.start()
            
            self.serial_btn.setText("🛑 Close Serial Monitor")
            # Disable controls that would conflict with serial
            self.port_combo.setEnabled(False)
            self.erase_btn.setEnabled(False)
            self.flash_btn.setEnabled(False)
            
    def on_serial_error(self, error_msg):
        """Handle errors from the serial thread."""
        self.serial_box.append(f"\n--- {error_msg} ---\n")
        self.toggle_serial() # Stop the (now broken) thread

    def on_serial_closed(self):
        """Ensure UI is reset if thread closes unexpectedly."""
        if self.serial_thread: # Only if it wasn't a manual stop
            self.serial_thread = None
            self.serial_btn.setText("🛰️ Open Serial Monitor")
            self.set_controls_enabled(True)
            self.serial_box.append("\n\n--- 🔌 Serial connection closed. ---\n")

    # ------------------------------
    # Log Saving
    # ------------------------------
    def save_log(self):
        # Determine active tab
        active_tab = self.tabs.currentWidget()
        if active_tab == self.log_box:
            content = self.log_box.toPlainText()
            default_name = "ESP32_Flasher_Log.txt"
        elif active_tab == self.serial_box:
            content = self.serial_box.toPlainText()
            default_name = "ESP32_Serial_Log.txt"
        else:
            return

        if not content.strip():
            QMessageBox.information(self, "Info", "No log data to save.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Log", default_name, "Text Files (*.txt);;All Files (*)")
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                QMessageBox.information(self, "Success", f"Log saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save log:\n{e}")

    # ------------------------------
    # Close Event
    # ------------------------------
    def closeEvent(self, event):
        """Ensure background threads are stopped on exit."""
        if self.serial_thread and self.serial_thread.isRunning():
            self.serial_thread.stop()
            self.serial_thread.wait()
        
        if self.flash_thread and self.flash_thread.isRunning():
            self.flash_thread.terminate() # Less clean, but necessary if stuck
            self.flash_thread.wait()
            
        if self.erase_thread and self.erase_thread.isRunning():
            self.erase_thread.terminate()
            self.erase_thread.wait()
            
        event.accept()

# ===============================
#  Main
# ===============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ESP32FlasherApp()
    win.show()
    sys.exit(app.exec_())