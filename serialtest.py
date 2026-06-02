import os
import sys
import serial
import serial.tools.list_ports
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QComboBox, QLabel, QPushButton, QPlainTextEdit, QListWidget, QTabWidget,
    QGroupBox, QFormLayout, QLineEdit, QCheckBox, QStatusBar, QMessageBox,
    QFileDialog, QToolBar, QTextEdit, QInputDialog, QDoubleSpinBox, QStyle,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings, QSize
from PyQt6.QtGui import (
    QAction,
    QActionGroup,
    QColor,
    QFont,
    QPalette,
    QTextCharFormat,
    QTextCursor,
    QKeySequence,
)


# Line endings appended to ASCII sends (and after HEX payloads)
LINE_ENDINGS = {
    "None": b"",
    "LF (\\n)": b"\n",
    "CR (\\r)": b"\r",
    "CR+LF (\\r\\n)": b"\r\n",
}

# HDLC-style flag; RX chunks are merged into one line per 7E...7E frame
RX_FRAME_FLAG = 0x7E
RX_IDLE_MS = 50

THEME_COLORS_LIGHT = {
    "normal": QColor("#2e7d32"),
    "send": QColor("#1565c0"),
    "rx": QColor("#c62828"),
    "info": QColor("#546e7a"),
    "error": QColor("#c62828"),
}

THEME_COLORS_DARK = {
    "normal": QColor("#81c784"),
    "send": QColor("#90caf9"),
    "rx": QColor("#ef5350"),
    "info": QColor("#b0bec5"),
    "error": QColor("#ef9a9a"),
}

HEX_THEME_COLORS_LIGHT = {
    "meta": QColor("#2e7d32"),
    "tx": QColor("#1565c0"),
    "rx": QColor("#c62828"),
}

HEX_THEME_COLORS_DARK = {
    "meta": QColor("#81c784"),
    "tx": QColor("#90caf9"),
    "rx": QColor("#ef5350"),
}


class SerialReader(QThread):
    """Background thread for reading serial data"""
    data_received = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)

    def __init__(self, serial_port):
        super().__init__()
        self.serial = serial_port
        self.running = True

    def run(self):
        while self.running and self.serial and self.serial.is_open:
            try:
                if self.serial.in_waiting > 0:
                    data = self.serial.read(self.serial.in_waiting)
                    if data:
                        self.data_received.emit(data)
            except Exception as e:
                self.error_occurred.emit(str(e))
                break

    def stop(self):
        self.running = False
        self.wait(500)


class SerialMonitor(QMainWindow):
    _BTN_ICON_SIZE = QSize(22, 22)

    def _decorate_button(self, btn: QPushButton, icon: QStyle.StandardPixmap) -> None:
        btn.setIcon(self.style().standardIcon(icon))
        btn.setIconSize(self._BTN_ICON_SIZE)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Serial Monitor - PyQt6")
        self.resize(1200, 800)

        self.ser = None
        self.reader = None
        self.log_file = None
        self.history = []
        self.show_timestamps = False
        self._settings = QSettings("Kalai", "SerialMonitor")
        self._last_history_load_path = self._settings.value("history/last_load_path", "", str)
        self._last_save_dir = self._settings.value("history/last_save_dir", "", str)
        self._last_open_dir = self._settings.value("history/last_open_dir", "", str)
        self._history_save_path = self._settings.value("history/last_save_path", "", str)
        self._last_log_save_dir = self._settings.value("ui/last_log_save_dir", "", str)
        self._last_stream_log_dir = self._settings.value("ui/last_stream_log_dir", "", str)
        self._stream_log_paused = False
        self._theme = "light"
        self._ascii_colors = dict(THEME_COLORS_LIGHT)
        self._hex_colors = dict(HEX_THEME_COLORS_LIGHT)

        self.setup_ui()
        self._auto_send_active = False
        self._auto_send_index = 0
        self._auto_send_timer = QTimer(self)
        self._auto_send_timer.timeout.connect(self._auto_send_tick)

        self._rx_buffer = bytearray()
        self._rx_idle_timer = QTimer(self)
        self._rx_idle_timer.setSingleShot(True)
        self._rx_idle_timer.timeout.connect(self._flush_rx_buffer)

        self._restore_serial_and_ui_settings()
        self.refresh_ports()
        self._restore_port_selection()
        self._reload_last_history_file_if_any()

        # Periodic port refresh
        self.port_timer = QTimer()
        self.port_timer.timeout.connect(self.refresh_ports)
        self.port_timer.start(2000)

    def setup_ui(self):
        # ==================== Menu bar ====================
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        self.action_save_log = QAction("&Save log...", self)
        self.action_save_log.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)
        )
        self.action_save_log.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.action_save_log.setStatusTip(
            "Save the currently visible output tab (ASCII, HEX, Decimal, or Binary) to a file."
        )
        self.action_save_log.triggered.connect(self.save_output_log)
        file_menu.addAction(self.action_save_log)

        file_menu.addSeparator()
        self.action_start_stream_log = QAction("Start &streaming log...", self)
        self.action_start_stream_log.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        )
        self.action_start_stream_log.setStatusTip(
            "Append ASCII output (RX, TX, status) to a file until you stop."
        )
        self.action_start_stream_log.triggered.connect(self.start_stream_log)
        file_menu.addAction(self.action_start_stream_log)

        self.action_pause_stream_log = QAction("&Pause streaming log", self)
        self.action_pause_stream_log.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
        )
        self.action_pause_stream_log.setCheckable(True)
        self.action_pause_stream_log.setEnabled(False)
        self.action_pause_stream_log.setStatusTip(
            "When checked, new lines are not written to the streaming log file."
        )
        self.action_pause_stream_log.triggered.connect(self._on_pause_stream_log_toggled)
        file_menu.addAction(self.action_pause_stream_log)

        self.action_stop_stream_log = QAction("St&op streaming log", self)
        self.action_stop_stream_log.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop)
        )
        self.action_stop_stream_log.setEnabled(False)
        self.action_stop_stream_log.setStatusTip("Close the streaming log file.")
        self.action_stop_stream_log.triggered.connect(self.stop_stream_log)
        file_menu.addAction(self.action_stop_stream_log)
        self._update_stream_log_actions()

        view_menu = menubar.addMenu("&View")
        self.action_timestamps = QAction("Show &timestamps in output", self)
        self.action_timestamps.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView)
        )
        self.action_timestamps.setCheckable(True)
        self.action_timestamps.setChecked(self.show_timestamps)
        self.action_timestamps.triggered.connect(self._on_timestamps_toggled)
        view_menu.addAction(self.action_timestamps)

        view_menu.addSeparator()
        theme_menu = view_menu.addMenu("&Theme")
        self._theme_group = QActionGroup(self)
        self._theme_group.setExclusive(True)
        self.action_theme_light = QAction("&Light", self)
        self.action_theme_light.setCheckable(True)
        self._theme_group.addAction(self.action_theme_light)
        self.action_theme_light.triggered.connect(lambda _: self._set_theme("light"))
        self.action_theme_dark = QAction("&Dark", self)
        self.action_theme_dark.setCheckable(True)
        self._theme_group.addAction(self.action_theme_dark)
        self.action_theme_dark.triggered.connect(lambda _: self._set_theme("dark"))
        theme_menu.addAction(self.action_theme_light)
        theme_menu.addAction(self.action_theme_dark)

        # ==================== Top Toolbar ====================
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Port selection
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(120)
        toolbar.addWidget(QLabel(" Port: "))
        toolbar.addWidget(self.port_combo)

        # Baudrate
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        self.baud_combo.setCurrentText("115200")
        toolbar.addWidget(QLabel(" Baud: "))
        toolbar.addWidget(self.baud_combo)

        toolbar.addWidget(QLabel(" Data: "))
        self.databits_combo = QComboBox()
        self.databits_combo.addItems(["5", "6", "7", "8"])
        self.databits_combo.setCurrentText("8")
        toolbar.addWidget(self.databits_combo)

        toolbar.addWidget(QLabel(" Parity: "))
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["None", "Even", "Odd", "Mark", "Space"])
        toolbar.addWidget(self.parity_combo)

        toolbar.addWidget(QLabel(" Stop: "))
        self.stop_combo = QComboBox()
        self.stop_combo.addItems(["1", "1.5", "2"])
        self.stop_combo.setCurrentText("1")
        toolbar.addWidget(self.stop_combo)

        toolbar.addWidget(QLabel(" End: "))
        self.end_combo = QComboBox()
        self.end_combo.addItems(list(LINE_ENDINGS.keys()))
        self.end_combo.setCurrentText("LF (\\n)")
        toolbar.addWidget(self.end_combo)

        toolbar.addSeparator()

        # Connect / Disconnect
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_serial)
        self._decorate_button(self.connect_btn, QStyle.StandardPixmap.SP_MediaPlay)
        toolbar.addWidget(self.connect_btn)

        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self.disconnect_serial)
        self.disconnect_btn.setEnabled(False)
        self._decorate_button(self.disconnect_btn, QStyle.StandardPixmap.SP_MediaStop)
        toolbar.addWidget(self.disconnect_btn)

        toolbar.addSeparator()
        self.refresh_btn = QPushButton("Refresh Ports")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        self._decorate_button(self.refresh_btn, QStyle.StandardPixmap.SP_BrowserReload)
        toolbar.addWidget(self.refresh_btn)

        # ==================== Main Splitter ====================
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(main_splitter)

        # Left Panel - Controls & History
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Send Section
        send_group = QGroupBox("Send Command")
        send_layout = QVBoxLayout(send_group)

        self.send_mode = QComboBox()
        self.send_mode.addItems(["ASCII", "HEX"])
        send_layout.addWidget(self.send_mode)

        self.entry = QLineEdit()
        self.entry.returnPressed.connect(self.send_command)
        send_layout.addWidget(self.entry)

        btn_layout = QHBoxLayout()
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_command)
        self._decorate_button(self.send_btn, QStyle.StandardPixmap.SP_ArrowForward)
        btn_layout.addWidget(self.send_btn)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.toggle_pause)
        self._decorate_button(self.pause_btn, QStyle.StandardPixmap.SP_MediaPause)
        btn_layout.addWidget(self.pause_btn)

        send_layout.addLayout(btn_layout)

        auto_group = QGroupBox("Auto send (command history)")
        auto_layout = QFormLayout(auto_group)
        self.auto_interval_spin = QDoubleSpinBox()
        self.auto_interval_spin.setRange(0.05, 3600.0)
        self.auto_interval_spin.setValue(1.0)
        self.auto_interval_spin.setSuffix(" s")
        self.auto_interval_spin.setDecimals(2)
        self.auto_interval_spin.setSingleStep(0.1)
        self.auto_interval_spin.setToolTip(
            "Time between sends; cycles through all lines in the history list in order."
        )
        self.auto_interval_spin.valueChanged.connect(self._on_auto_interval_changed)
        auto_layout.addRow("Period:", self.auto_interval_spin)

        self.auto_send_btn = QPushButton("Start auto send")
        self.auto_send_btn.clicked.connect(self.toggle_auto_send)
        self._decorate_button(self.auto_send_btn, QStyle.StandardPixmap.SP_MediaPlay)
        auto_layout.addRow(self.auto_send_btn)

        # History
        history_group = QGroupBox("Command History")
        history_layout = QVBoxLayout(history_group)
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.send_from_history)
        history_layout.addWidget(self.history_list)

        reorder_row = QHBoxLayout()
        reorder_row.setSpacing(6)
        reorder_row.setContentsMargins(0, 0, 0, 0)
        self.history_up_btn = QPushButton("Up")
        self.history_up_btn.setToolTip("Move selected command up")
        self.history_up_btn.clicked.connect(self.history_move_up)
        self._decorate_button(self.history_up_btn, QStyle.StandardPixmap.SP_ArrowUp)
        reorder_row.addWidget(self.history_up_btn, 1)

        self.history_down_btn = QPushButton("Down")
        self.history_down_btn.setToolTip("Move selected command down")
        self.history_down_btn.clicked.connect(self.history_move_down)
        self._decorate_button(self.history_down_btn, QStyle.StandardPixmap.SP_ArrowDown)
        reorder_row.addWidget(self.history_down_btn, 1)

        self.history_edit_btn = QPushButton("Edit")
        self.history_edit_btn.setToolTip("Edit selected command")
        self.history_edit_btn.clicked.connect(self.edit_history_item)
        self._decorate_button(self.history_edit_btn, QStyle.StandardPixmap.SP_FileDialogContentsView)
        reorder_row.addWidget(self.history_edit_btn, 1)

        self.history_delete_btn = QPushButton("Delete")
        self.history_delete_btn.setToolTip("Remove selected command")
        self.history_delete_btn.clicked.connect(self.delete_history_item)
        self._decorate_button(self.history_delete_btn, QStyle.StandardPixmap.SP_TrashIcon)
        reorder_row.addWidget(self.history_delete_btn, 1)
        history_layout.addLayout(reorder_row)

        file_row = QHBoxLayout()
        file_row.setSpacing(6)
        file_row.setContentsMargins(0, 0, 0, 0)
        self.history_load_btn = QPushButton("Load")
        self.history_load_btn.clicked.connect(self.load_history)
        self._decorate_button(self.history_load_btn, QStyle.StandardPixmap.SP_DialogOpenButton)
        file_row.addWidget(self.history_load_btn, 1)

        self.history_save_btn = QPushButton("Save")
        self.history_save_btn.clicked.connect(self.save_history)
        self._decorate_button(self.history_save_btn, QStyle.StandardPixmap.SP_DialogSaveButton)
        file_row.addWidget(self.history_save_btn, 1)

        self.history_save_as_btn = QPushButton("Save As")
        self.history_save_as_btn.clicked.connect(self.save_history_as)
        self._decorate_button(self.history_save_as_btn, QStyle.StandardPixmap.SP_FileDialogStart)
        file_row.addWidget(self.history_save_as_btn, 1)

        self.history_clear_btn = QPushButton("Clear")
        self.history_clear_btn.clicked.connect(self.clear_history)
        self._decorate_button(self.history_clear_btn, QStyle.StandardPixmap.SP_DialogResetButton)
        file_row.addWidget(self.history_clear_btn, 1)

        history_layout.addLayout(file_row)

        left_layout.addWidget(send_group)
        left_layout.addWidget(auto_group)
        left_layout.addWidget(history_group)
        main_splitter.addWidget(left_panel)

        # Right Panel - Terminal Tabs
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.tabs = QTabWidget()
        right_layout.addWidget(self.tabs, 1)

        # Create tabs (ASCII uses QTextEdit for RX/TX colors)
        self.ascii_edit = self.create_ascii_output_widget()
        self.hex_edit = self.create_ascii_output_widget()
        self.dec_edit = self.create_output_widget(monospace=True)
        self.bin_edit = self.create_output_widget(monospace=True)

        self.tabs.addTab(self.ascii_edit, "ASCII")
        self.tabs.addTab(self.hex_edit, "HEX")
        self.tabs.addTab(self.dec_edit, "Decimal")
        self.tabs.addTab(self.bin_edit, "Binary")

        output_bar = QHBoxLayout()
        output_bar.addStretch()
        self.clear_output_btn = QPushButton("Clear output")
        self.clear_output_btn.setToolTip("Clear ASCII, HEX, Decimal, and Binary views")
        self.clear_output_btn.clicked.connect(self.clear_output_views)
        self._decorate_button(self.clear_output_btn, QStyle.StandardPixmap.SP_LineEditClearButton)
        output_bar.addWidget(self.clear_output_btn)
        right_layout.addLayout(output_bar)

        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([350, 850])

        # Status Bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.status_label = QLabel("Disconnected")
        self.stats_label = QLabel("RX: 0 | TX: 0")
        self.statusBar.addWidget(self.status_label)
        self.statusBar.addPermanentWidget(self.stats_label)

        self.rx_bytes = 0
        self.tx_bytes = 0

    def _restore_serial_and_ui_settings(self) -> None:
        s = self._settings
        baud = s.value("serial/baud", "115200", str)
        if self.baud_combo.findText(baud) >= 0:
            self.baud_combo.setCurrentText(baud)

        for combo, key, default in (
            (self.databits_combo, "serial/databits", "8"),
            (self.parity_combo, "serial/parity", "None"),
            (self.stop_combo, "serial/stopbits", "1"),
        ):
            val = s.value(key, default, str)
            if combo.findText(val) >= 0:
                combo.setCurrentText(val)

        end = s.value("serial/line_end", "LF (\\n)", str)
        if self.end_combo.findText(end) >= 0:
            self.end_combo.setCurrentText(end)

        mode = s.value("ui/send_mode", "ASCII", str)
        if self.send_mode.findText(mode) >= 0:
            self.send_mode.setCurrentText(mode)

        self.show_timestamps = s.value("ui/show_timestamps", False, bool)
        self.action_timestamps.setChecked(self.show_timestamps)

        theme = s.value("ui/theme", "light", str)
        if theme not in ("light", "dark"):
            theme = "light"
        self._theme = theme
        self.action_theme_light.setChecked(theme == "light")
        self.action_theme_dark.setChecked(theme == "dark")
        self._apply_theme()

        interval = float(s.value("ui/auto_interval_sec", 1.0))
        interval = max(0.05, min(3600.0, interval))
        self.auto_interval_spin.setValue(interval)

    def _restore_port_selection(self) -> None:
        port = self._settings.value("serial/port", "", str)
        if not port:
            return
        idx = self.port_combo.findText(port)
        if idx >= 0:
            self.port_combo.setCurrentIndex(idx)
        else:
            self.port_combo.insertItem(0, port)
            self.port_combo.setCurrentIndex(0)

    def _reload_last_history_file_if_any(self) -> None:
        path = self._last_history_load_path
        if not path or not os.path.isfile(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                cmds = [line.strip() for line in f if line.strip()]
            self.history_list.clear()
            self.history_list.addItems(cmds)
            self.history = list(cmds)
            self._history_save_path = path
        except OSError:
            pass

    def _persist_settings(self) -> None:
        s = self._settings
        s.setValue("serial/port", self.port_combo.currentText())
        s.setValue("serial/baud", self.baud_combo.currentText())
        s.setValue("serial/databits", self.databits_combo.currentText())
        s.setValue("serial/parity", self.parity_combo.currentText())
        s.setValue("serial/stopbits", self.stop_combo.currentText())
        s.setValue("serial/line_end", self.end_combo.currentText())
        s.setValue("ui/send_mode", self.send_mode.currentText())
        s.setValue("ui/show_timestamps", self.show_timestamps)
        s.setValue("ui/theme", getattr(self, "_theme", "light"))
        s.setValue("ui/auto_interval_sec", self.auto_interval_spin.value())
        s.setValue("history/last_load_path", getattr(self, "_last_history_load_path", ""))
        s.setValue("history/last_save_dir", getattr(self, "_last_save_dir", ""))
        s.setValue("history/last_open_dir", getattr(self, "_last_open_dir", ""))
        s.setValue("history/last_save_path", getattr(self, "_history_save_path", ""))
        s.setValue("ui/last_log_save_dir", getattr(self, "_last_log_save_dir", ""))
        s.setValue("ui/last_stream_log_dir", getattr(self, "_last_stream_log_dir", ""))

    def _set_theme(self, theme: str) -> None:
        if theme not in ("light", "dark"):
            return
        self._theme = theme
        self.action_theme_light.setChecked(theme == "light")
        self.action_theme_dark.setChecked(theme == "dark")
        self._apply_theme()
        self._persist_settings()

    def _build_light_palette(self) -> QPalette:
        p = QPalette()
        p.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        p.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        p.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        p.setColor(QPalette.ColorRole.AlternateBase, QColor(233, 231, 227))
        p.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        p.setColor(QPalette.ColorRole.Button, QColor(239, 239, 239))
        p.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
        p.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
        p.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        p.setColor(QPalette.ColorRole.PlaceholderText, QColor(120, 120, 120))
        return p

    def _build_dark_palette(self) -> QPalette:
        p = QPalette()
        p.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        p.setColor(QPalette.ColorRole.WindowText, QColor(240, 240, 240))
        p.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        p.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
        p.setColor(QPalette.ColorRole.Text, QColor(230, 230, 230))
        p.setColor(QPalette.ColorRole.Button, QColor(58, 58, 58))
        p.setColor(QPalette.ColorRole.ButtonText, QColor(240, 240, 240))
        p.setColor(QPalette.ColorRole.Highlight, QColor(61, 90, 254))
        p.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        p.setColor(QPalette.ColorRole.ToolTipBase, QColor(45, 45, 45))
        p.setColor(QPalette.ColorRole.ToolTipText, QColor(240, 240, 240))
        p.setColor(QPalette.ColorRole.PlaceholderText, QColor(160, 160, 160))
        return p

    def _light_stylesheet(self) -> str:
        return """
QPlainTextEdit, QTextEdit {
    background-color: #ffffff;
    color: #1a1a1a;
    selection-background-color: #0d47a1;
    selection-color: #ffffff;
}
QListWidget {
    background-color: #ffffff;
    color: #1a1a1a;
}
"""

    def _dark_stylesheet(self) -> str:
        return """
QWidget { color: #e8e8e8; }
QPlainTextEdit, QTextEdit {
    background-color: #1a1a1a;
    color: #ececec;
    selection-background-color: #3d5afe;
    selection-color: #ffffff;
}
QLineEdit, QComboBox, QListWidget, QDoubleSpinBox {
    background-color: #2a2a2a;
    color: #ececec;
    border: 1px solid #444444;
    border-radius: 2px;
    padding: 2px;
}
QGroupBox {
    font-weight: 600;
    border: 1px solid #444444;
    margin-top: 10px;
    padding-top: 8px;
}
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
QPushButton {
    background-color: #3a3a3a;
    color: #eeeeee;
    border: 1px solid #555555;
    padding: 4px 10px;
    border-radius: 3px;
}
QPushButton:hover { background-color: #484848; }
QPushButton:pressed { background-color: #303030; }
QPushButton:disabled { color: #777777; }
QTabWidget::pane { border: 1px solid #444444; top: -1px; }
QTabBar::tab {
    background: #353535;
    color: #dddddd;
    border: 1px solid #444444;
    padding: 6px 14px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #1a1a1a;
    color: #ffffff;
    border-bottom-color: #1a1a1a;
}
QMenuBar { background-color: #2e2e2e; color: #eeeeee; }
QMenuBar::item:selected { background: #444444; }
QMenu { background-color: #2e2e2e; color: #eeeeee; }
QMenu::item:selected { background: #444444; }
QStatusBar { background-color: #2a2a2a; color: #cccccc; }
QToolBar { background-color: #2e2e2e; border: none; }
QSplitter::handle { background: #444444; }
"""

    def _apply_theme(self) -> None:
        app = QApplication.instance()
        if app is None:
            return
        if self._theme == "dark":
            self._ascii_colors = dict(THEME_COLORS_DARK)
            self._hex_colors = dict(HEX_THEME_COLORS_DARK)
            app.setPalette(self._build_dark_palette())
            app.setStyleSheet(self._dark_stylesheet())
        else:
            self._ascii_colors = dict(THEME_COLORS_LIGHT)
            self._hex_colors = dict(HEX_THEME_COLORS_LIGHT)
            app.setPalette(self._build_light_palette())
            app.setStyleSheet(self._light_stylesheet())

    def create_ascii_output_widget(self) -> QTextEdit:
        edit = QTextEdit()
        edit.setReadOnly(True)
        edit.setAcceptRichText(False)
        edit.document().setMaximumBlockCount(5000)
        edit.setFont(QFont("Consolas", 10))
        return edit

    def create_output_widget(self, monospace=False):
        edit = QPlainTextEdit()
        edit.setReadOnly(True)
        edit.setMaximumBlockCount(5000)  # Prevent memory issues
        if monospace:
            edit.setFont(QFont("Consolas", 10))
        else:
            edit.setFont(QFont("Segoe UI", 10))
        return edit

    def _append_ascii_colored(self, text: str, level: str = "normal") -> None:
        if not text:
            return
        color = self._ascii_colors.get(level, self._ascii_colors["normal"])
        edit = self.ascii_edit
        cursor = QTextCursor(edit.document())
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        cursor.setCharFormat(fmt)
        cursor.insertText(text)
        edit.setTextCursor(cursor)
        edit.ensureCursorVisible()

    def clear_output_views(self) -> None:
        self.ascii_edit.clear()
        self.hex_edit.clear()
        self.dec_edit.clear()
        self.bin_edit.clear()

    def save_output_log(self) -> None:
        idx = self.tabs.currentIndex()
        widget = self.tabs.widget(idx)
        if widget is None:
            return
        if isinstance(widget, QTextEdit):
            text = widget.toPlainText()
        elif isinstance(widget, QPlainTextEdit):
            text = widget.toPlainText()
        else:
            QMessageBox.warning(self, "Save log", "Cannot read this tab as text.")
            return

        tab = self.tabs.tabText(idx).lower().replace(" ", "_")
        default_name = f"serial_log_{tab}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        start = self._last_log_save_dir or ""
        suggest = os.path.join(start, default_name) if start else default_name

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save output log",
            suggest,
            "Text files (*.txt);;All files (*)",
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            self._last_log_save_dir = os.path.dirname(file_path) or self._last_log_save_dir
            self._persist_settings()
            self.statusBar.showMessage(f"Log saved: {file_path}", 5000)
        except OSError as e:
            QMessageBox.warning(self, "Save log", str(e))

    def refresh_ports(self):
        current = self.port_combo.currentText()
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo.clear()
        self.port_combo.addItems(ports)
        if current in ports:
            self.port_combo.setCurrentText(current)
        elif current:
            self.port_combo.insertItem(0, current)
            self.port_combo.setCurrentIndex(0)
        elif ports:
            self.port_combo.setCurrentIndex(0)

    def connect_serial(self):
        port = self.port_combo.currentText()
        if not port:
            QMessageBox.warning(self, "Error", "No port selected")
            return

        try:
            p = self._serial_params()
            databits = self.databits_combo.currentText()
            parity_ui = self.parity_combo.currentText()
            stop_ui = self.stop_combo.currentText()
            self.ser = serial.Serial(
                port=port,
                baudrate=int(self.baud_combo.currentText()),
                bytesize=p["bytesize"].get(databits, serial.EIGHTBITS),
                parity=p["parity"].get(parity_ui, serial.PARITY_NONE),
                stopbits=p["stopbits"].get(stop_ui, serial.STOPBITS_ONE),
                timeout=1,
            )
            self.reader = SerialReader(self.ser)
            self.reader.data_received.connect(self.handle_received_data)
            self.reader.error_occurred.connect(self.handle_error)
            self.reader.start()

            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.baud_combo.setEnabled(False)
            self.databits_combo.setEnabled(False)
            self.parity_combo.setEnabled(False)
            self.stop_combo.setEnabled(False)
            self.end_combo.setEnabled(False)
            self.status_label.setText(f"Connected to {port}")
            self.append_output(
                f"Connected to {port} @ {self.baud_combo.currentText()} "
                f"(Data {databits}, Parity {parity_ui}, Stop {stop_ui})\n",
                "info",
            )
            self._persist_settings()

        except Exception as e:
            QMessageBox.critical(self, "Connection Failed", str(e))

    def _line_ending_bytes(self) -> bytes:
        return LINE_ENDINGS.get(self.end_combo.currentText(), b"\n")

    @staticmethod
    def _serial_params():
        import serial as ser_mod

        return {
            "bytesize": {
                "5": ser_mod.FIVEBITS,
                "6": ser_mod.SIXBITS,
                "7": ser_mod.SEVENBITS,
                "8": ser_mod.EIGHTBITS,
            },
            "parity": {
                "None": ser_mod.PARITY_NONE,
                "Even": ser_mod.PARITY_EVEN,
                "Odd": ser_mod.PARITY_ODD,
                "Mark": ser_mod.PARITY_MARK,
                "Space": ser_mod.PARITY_SPACE,
            },
            "stopbits": {
                "1": ser_mod.STOPBITS_ONE,
                "1.5": ser_mod.STOPBITS_ONE_POINT_FIVE,
                "2": ser_mod.STOPBITS_TWO,
            },
        }

    def disconnect_serial(self):
        self._stop_auto_send()
        self._rx_idle_timer.stop()
        self._flush_rx_buffer()
        self._rx_buffer.clear()
        if self.reader:
            self.reader.stop()
            self.reader = None
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.ser = None

        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.baud_combo.setEnabled(True)
        self.databits_combo.setEnabled(True)
        self.parity_combo.setEnabled(True)
        self.stop_combo.setEnabled(True)
        self.end_combo.setEnabled(True)
        self.status_label.setText("Disconnected")
        self.append_output("Disconnected\n", "info")
        self._persist_settings()

    def _on_timestamps_toggled(self, checked: bool):
        self.show_timestamps = bool(checked)
        self._persist_settings()

    def _timestamp_prefix(self) -> str:
        now = datetime.now()
        return f"[{now.strftime('%Y-%m-%d %H:%M:%S')}.{now.microsecond // 1000:03d}] "

    def _with_timestamps(self, text: str) -> str:
        if not self.show_timestamps or not text:
            return text
        ts = self._timestamp_prefix()
        out_lines = []
        for line in text.splitlines(keepends=True):
            if line.endswith("\r\n"):
                body, eol = line[:-2], "\r\n"
            elif line.endswith("\n"):
                body, eol = line[:-1], "\n"
            elif line.endswith("\r"):
                body, eol = line[:-1], "\r"
            else:
                body, eol = line, ""
            out_lines.append(ts + body + eol)
        return "".join(out_lines)

    def handle_received_data(self, data: bytes):
        self.rx_bytes += len(data)
        self.update_stats()

        self._rx_buffer.extend(data)
        self._rx_idle_timer.stop()
        self._process_rx_frames()
        if self._rx_buffer:
            self._rx_idle_timer.start(RX_IDLE_MS)

    def _process_rx_frames(self) -> None:
        """Emit one display line per complete 0x7E-delimited frame."""
        while len(self._rx_buffer) >= 2:
            if self._rx_buffer[0] != RX_FRAME_FLAG:
                idx = self._rx_buffer.find(RX_FRAME_FLAG)
                if idx < 0:
                    return
                del self._rx_buffer[:idx]
                continue
            end = self._rx_buffer.find(RX_FRAME_FLAG, 1)
            if end < 0:
                return
            frame = bytes(self._rx_buffer[: end + 1])
            del self._rx_buffer[: end + 1]
            self._display_rx(frame)

    def _flush_rx_buffer(self) -> None:
        """After idle gap, show any bytes not yet forming a full frame."""
        if not self._rx_buffer:
            return
        data = bytes(self._rx_buffer)
        self._rx_buffer.clear()
        self._display_rx(data)

    def _display_rx(self, data: bytes) -> None:
        if not data:
            return
        self.append_ascii_frame(data, "RX")
        self.append_hex_frame(data, "RX")
        self.append_decimal(data)
        self.append_binary(data)

    def append_output(self, text: str, level="normal"):
        """Append to ASCII tab"""
        if level == "info":
            body = f"[INFO] {text.strip()}"
        elif level == "error":
            body = text.rstrip("\n\r")
            if body:
                body = body + "\n"
        else:
            body = text
        display = self._with_timestamps(body)
        self._append_ascii_colored(display, level)
        self._stream_log_write(display)

    def _hex_timestamp(self) -> str:
        now = datetime.now()
        return f"{now.strftime('%d-%m-%Y %H:%M:%S')}.{now.microsecond // 1000:03d} "

    def _format_hex_bytes(self, data: bytes) -> str:
        return " ".join(f"{b:02X}" for b in data)

    def _format_ascii_bytes(self, data: bytes) -> str:
        return "".join(chr(b) if 32 <= b <= 126 else "." for b in data)

    def append_ascii_frame(self, data: bytes, direction: str) -> None:
        """ASCII tab: same layout as HEX tab, printable bytes only."""
        if not data:
            return
        prefix = ""
        if self.show_timestamps:
            prefix = self._hex_timestamp()
        prefix += f"[{direction}] - "
        data_level = "send" if direction == "TX" else "rx"
        self._append_ascii_colored(prefix, "normal")
        body = self._format_ascii_bytes(data) + "\n"
        self._append_ascii_colored(body, data_level)
        self._stream_log_write(prefix + body)

    def _append_hex_colored(self, text: str, color_key: str) -> None:
        if not text:
            return
        color = self._hex_colors.get(color_key, self._hex_colors["meta"])
        edit = self.hex_edit
        cursor = QTextCursor(edit.document())
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        cursor.setCharFormat(fmt)
        cursor.insertText(text)
        edit.setTextCursor(cursor)
        edit.ensureCursorVisible()

    def append_hex_frame(self, data: bytes, direction: str) -> None:
        """HEX tab: timestamp [TX|RX] - space-separated bytes (colored)."""
        if not data:
            return
        tag = "tx" if direction == "TX" else "rx"
        prefix = ""
        if self.show_timestamps:
            prefix = self._hex_timestamp()
        prefix += f"[{direction}] - "
        self._append_hex_colored(prefix, "meta")
        self._append_hex_colored(self._format_hex_bytes(data) + "\n", tag)

    def append_decimal(self, data: bytes):
        """Decimal byte dump (aligned like HEX tab)."""
        lines = []
        for i in range(0, len(data), 16):
            chunk = data[i : i + 16]
            dec_str = " ".join(f"{b:3d}" for b in chunk)
            lines.append(f"{i:08X}  {dec_str}")

        if not lines:
            return
        block = "\n".join(lines)
        if self.show_timestamps:
            ts = self._timestamp_prefix()
            block = "\n".join(ts + ln for ln in lines)
        self.dec_edit.appendPlainText(block)

    def append_binary(self, data: bytes):
        """Binary representation per byte (8 bits), 16 bytes per row."""
        lines = []
        for i in range(0, len(data), 16):
            chunk = data[i : i + 16]
            bin_str = " ".join(f"{b:08b}" for b in chunk)
            lines.append(f"{i:08X}  {bin_str}")

        if not lines:
            return
        block = "\n".join(lines)
        if self.show_timestamps:
            ts = self._timestamp_prefix()
            block = "\n".join(ts + ln for ln in lines)
        self.bin_edit.appendPlainText(block)

    def _update_stream_log_actions(self) -> None:
        active = self.log_file is not None
        self.action_start_stream_log.setEnabled(not active)
        self.action_pause_stream_log.setEnabled(active)
        self.action_stop_stream_log.setEnabled(active)
        if not active:
            self.action_pause_stream_log.blockSignals(True)
            self.action_pause_stream_log.setChecked(False)
            self.action_pause_stream_log.setText("&Pause streaming log")
            self.action_pause_stream_log.blockSignals(False)

    def _stream_log_write(self, text: str) -> None:
        f = self.log_file
        if f is None or self._stream_log_paused or not text:
            return
        try:
            f.write(text)
            if not text.endswith("\n"):
                f.write("\n")
            f.flush()
        except OSError:
            QMessageBox.warning(
                self,
                "Streaming log",
                "Write failed; streaming log has been stopped.",
            )
            self.stop_stream_log()

    def start_stream_log(self) -> None:
        if self.log_file is not None:
            QMessageBox.information(
                self,
                "Streaming log",
                "A streaming log is already open. Stop it before starting a new one.",
            )
            return
        default_name = f"serial_stream_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        start = self._last_stream_log_dir or ""
        suggest = os.path.join(start, default_name) if start else default_name
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Start streaming log",
            suggest,
            "Log files (*.log);;Text files (*.txt);;All files (*)",
        )
        if not path:
            return
        try:
            self.log_file = open(path, "a", encoding="utf-8", newline="\n")
            self._stream_log_paused = False
            self.action_pause_stream_log.blockSignals(True)
            self.action_pause_stream_log.setChecked(False)
            self.action_pause_stream_log.setText("&Pause streaming log")
            self.action_pause_stream_log.blockSignals(False)
            self.log_file.write(
                f"\n{'=' * 60}\n[Stream log started {datetime.now().isoformat(timespec='seconds')}]\n"
                f"{'=' * 60}\n"
            )
            self.log_file.flush()
            self._last_stream_log_dir = os.path.dirname(path) or self._last_stream_log_dir
            self._update_stream_log_actions()
            self._persist_settings()
            self.statusBar.showMessage(f"Streaming log: {path}", 5000)
        except OSError as e:
            self.log_file = None
            QMessageBox.warning(self, "Streaming log", str(e))

    def _on_pause_stream_log_toggled(self, checked: bool = False) -> None:
        if self.log_file is None:
            self.action_pause_stream_log.blockSignals(True)
            self.action_pause_stream_log.setChecked(False)
            self.action_pause_stream_log.blockSignals(False)
            return
        self._stream_log_paused = bool(checked)
        self.action_pause_stream_log.setText(
            "&Resume streaming log" if self._stream_log_paused else "&Pause streaming log"
        )
        line = (
            f"[Logging paused {datetime.now().isoformat(timespec='seconds')}]\n"
            if self._stream_log_paused
            else f"[Logging resumed {datetime.now().isoformat(timespec='seconds')}]\n"
        )
        try:
            self.log_file.write(line)
            self.log_file.flush()
        except OSError:
            pass
        self.statusBar.showMessage(
            "Streaming log paused" if self._stream_log_paused else "Streaming log resumed",
            3000,
        )

    def stop_stream_log(self) -> None:
        if self.log_file is None:
            return
        try:
            self.log_file.write(
                f"[Stream log stopped {datetime.now().isoformat(timespec='seconds')}]\n"
            )
            self.log_file.flush()
            self.log_file.close()
        except Exception:
            pass
        self.log_file = None
        self._stream_log_paused = False
        self.action_pause_stream_log.blockSignals(True)
        self.action_pause_stream_log.setChecked(False)
        self.action_pause_stream_log.setText("&Pause streaming log")
        self.action_pause_stream_log.blockSignals(False)
        self._update_stream_log_actions()
        self._persist_settings()
        self.statusBar.showMessage("Streaming log stopped.", 3000)

    def send_command_text(
        self,
        cmd: str,
        *,
        add_to_history: bool = True,
        clear_entry: bool = False,
    ) -> bool:
        if not self.ser or not self.ser.is_open:
            return False
        cmd = cmd.strip()
        le = self._line_ending_bytes()

        try:
            if self.send_mode.currentText() == "HEX":
                if not cmd:
                    if not le:
                        return False
                    payload = le
                else:
                    clean = "".join(cmd.split())
                    if len(clean) % 2 != 0:
                        raise ValueError("HEX must have an even number of digits")
                    payload = bytes.fromhex(clean) + le
            else:
                if not cmd and not le:
                    return False
                payload = cmd.encode("utf-8", errors="replace") + le

            self.ser.write(payload)
            self.tx_bytes += len(payload)
            self.update_stats()

            self.append_ascii_frame(payload, "TX")
            self.append_hex_frame(payload, "TX")

            if add_to_history and cmd and cmd not in self.history:
                self.history.append(cmd)
                self.history_list.addItem(cmd)

            if clear_entry:
                self.entry.clear()
            return True

        except Exception as e:
            self.append_output(f"Send Error: {e}\n", "error")
            return False

    def send_command(self):
        if not self.ser or not self.ser.is_open:
            return
        cmd = self.entry.text().strip()
        self.send_command_text(cmd, add_to_history=True, clear_entry=True)

    def send_from_history(self, item):
        self.entry.setText(item.text())
        self.send_command()

    def _on_auto_interval_changed(self, value: float) -> None:
        if self._auto_send_timer.isActive():
            ms = max(50, int(float(value) * 1000))
            self._auto_send_timer.setInterval(ms)

    def _stop_auto_send(self) -> None:
        if not self._auto_send_active:
            return
        self._auto_send_timer.stop()
        self._auto_send_active = False
        self.auto_send_btn.setText("Start auto send")
        self._decorate_button(self.auto_send_btn, QStyle.StandardPixmap.SP_MediaPlay)
        self.auto_interval_spin.setEnabled(True)

    def toggle_auto_send(self) -> None:
        if self._auto_send_active:
            self._stop_auto_send()
            return
        if not self.ser or not self.ser.is_open:
            QMessageBox.warning(self, "Auto send", "Connect to a serial port first.")
            return
        if self.history_list.count() == 0:
            QMessageBox.information(
                self,
                "Auto send",
                "Add or load commands in the history list first.",
            )
            return
        self._auto_send_index = 0
        sec = self.auto_interval_spin.value()
        self._auto_send_timer.setInterval(max(50, int(sec * 1000)))
        self._auto_send_timer.start()
        self._auto_send_active = True
        self.auto_send_btn.setText("Stop auto send")
        self._decorate_button(self.auto_send_btn, QStyle.StandardPixmap.SP_MediaStop)
        self.auto_interval_spin.setEnabled(False)
        self._auto_send_tick()

    def _auto_send_tick(self) -> None:
        if not self.ser or not self.ser.is_open:
            self._stop_auto_send()
            return
        n = self.history_list.count()
        if n == 0:
            self._stop_auto_send()
            self.append_output("Auto send stopped (history empty).\n", "info")
            return
        cmd = self.history_list.item(self._auto_send_index).text().strip()
        self._auto_send_index = (self._auto_send_index + 1) % n
        if not cmd:
            return
        self.send_command_text(cmd, add_to_history=False, clear_entry=False)

    def toggle_pause(self):
        # TODO: Implement pause/resume logic
        pass

    def update_stats(self):
        self.stats_label.setText(f"RX: {self.rx_bytes:,} | TX: {self.tx_bytes:,}")

    def _sync_history_from_list(self) -> None:
        self.history = [self.history_list.item(i).text() for i in range(self.history_list.count())]

    def _write_history_file(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            for i in range(self.history_list.count()):
                f.write(self.history_list.item(i).text() + "\n")
        self._last_save_dir = os.path.dirname(file_path) or self._last_save_dir

    def history_move_up(self) -> None:
        row = self.history_list.currentRow()
        if row <= 0:
            return
        item = self.history_list.takeItem(row)
        self.history_list.insertItem(row - 1, item)
        self.history_list.setCurrentRow(row - 1)
        self._sync_history_from_list()

    def history_move_down(self) -> None:
        row = self.history_list.currentRow()
        if row < 0 or row >= self.history_list.count() - 1:
            return
        item = self.history_list.takeItem(row)
        self.history_list.insertItem(row + 1, item)
        self.history_list.setCurrentRow(row + 1)
        self._sync_history_from_list()

    def delete_history_item(self) -> None:
        row = self.history_list.currentRow()
        if row < 0:
            QMessageBox.information(self, "Delete", "Select a command to delete.")
            return
        self.history_list.takeItem(row)
        self._sync_history_from_list()

    def edit_history_item(self) -> None:
        item = self.history_list.currentItem()
        if not item:
            QMessageBox.information(self, "Edit", "Select a command to edit.")
            return
        text, ok = QInputDialog.getText(
            self, "Edit Command", "Command:", text=item.text()
        )
        if not ok:
            return
        new_text = text.strip()
        if not new_text:
            QMessageBox.warning(self, "Edit", "Command cannot be empty.")
            return
        item.setText(new_text)
        self._sync_history_from_list()

    def load_history(self):
        start = self._last_open_dir or ""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load History", start, "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    cmds = [line.strip() for line in f if line.strip()]
                self.history_list.clear()
                self.history_list.addItems(cmds)
                self.history = list(cmds)
                self._last_open_dir = os.path.dirname(file_path) or self._last_open_dir
                self._last_history_load_path = file_path
                self._history_save_path = file_path
                self._persist_settings()
            except Exception as e:
                QMessageBox.warning(self, "Load Error", str(e))

    def save_history(self):
        if not self.history_list.count():
            QMessageBox.information(self, "Save", "No commands to save.")
            return
        path = getattr(self, "_history_save_path", "") or ""
        if path:
            try:
                self._write_history_file(path)
                self._persist_settings()
            except OSError as e:
                QMessageBox.warning(self, "Save Error", str(e))
            return
        self.save_history_as()

    def save_history_as(self):
        if not self.history_list.count():
            QMessageBox.information(self, "Save As", "No commands to save.")
            return
        start = self._last_save_dir or ""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save History As", start, "Text Files (*.txt)"
        )
        if not file_path:
            return
        try:
            self._write_history_file(file_path)
            self._history_save_path = file_path
            self._persist_settings()
        except OSError as e:
            QMessageBox.warning(self, "Save Error", str(e))

    def clear_history(self):
        self.history_list.clear()
        self.history.clear()
        self._last_history_load_path = ""
        self._history_save_path = ""
        self._persist_settings()

    def handle_error(self, error_msg):
        self.append_output(f"Error: {error_msg}\n", "error")
        if self.ser and self.ser.is_open:
            self.disconnect_serial()

    def closeEvent(self, event):
        self._stop_auto_send()
        self.stop_stream_log()
        self._persist_settings()
        self.disconnect_serial()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setOrganizationName("Kalai")
    app.setApplicationName("SerialMonitor")
    # Fusion gives consistent palette + QSS; light/dark from View → Theme (saved in settings).
    app.setStyle("Fusion")
    window = SerialMonitor()
    window.show()
    sys.exit(app.exec())