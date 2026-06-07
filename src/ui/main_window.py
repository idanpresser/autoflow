from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QListWidget, QPushButton, QInputDialog, QListWidgetItem
)
from PySide6.QtCore import Qt, QObject, Signal, Slot
from PySide6.QtGui import QColor
from src.utils.hotkeys import register_hotkey
from src.engine.runner import WorkflowRunner

class HotkeyBridge(QObject):
    hotkey_triggered = Signal()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoFlow")
        self.resize(800, 600)
        
        # Central widget and layout
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)
        
        # Buttons panel (horizontal layout)
        buttons_layout = QHBoxLayout()
        
        self.btn_add_type = QPushButton("Add Type Text", central_widget)
        self.btn_add_type.setObjectName("btn_add_type_text")
        self.btn_add_type.clicked.connect(self.on_add_type_text)
        buttons_layout.addWidget(self.btn_add_type)
        
        self.btn_add_key = QPushButton("Add Press Key", central_widget)
        self.btn_add_key.setObjectName("btn_add_press_key")
        self.btn_add_key.clicked.connect(self.on_add_press_key)
        buttons_layout.addWidget(self.btn_add_key)
        
        self.btn_add_wait = QPushButton("Add Wait", central_widget)
        self.btn_add_wait.setObjectName("btn_add_wait")
        self.btn_add_wait.clicked.connect(self.on_add_wait)
        buttons_layout.addWidget(self.btn_add_wait)
        
        main_layout.addLayout(buttons_layout)
        
        # Step list widget
        self.step_list = QListWidget(central_widget)
        self.step_list.setObjectName("step_list")
        main_layout.addWidget(self.step_list)
        
        self.setCentralWidget(central_widget)

    def on_add_type_text(self):
        text, ok = QInputDialog.getText(self, "Add Type Text", "Enter text to type:")
        if ok and text:
            item = QListWidgetItem(f"Type Text: {text}", self.step_list)
            item.setData(Qt.UserRole, {"type": "type_text", "text": text})
            self.step_list.addItem(item)

    def on_add_press_key(self):
        keys_str, ok = QInputDialog.getText(self, "Add Press Key", "Enter keys (e.g. ctrl+c):")
        if ok and keys_str:
            keys = [k.strip() for k in keys_str.split('+') if k.strip()]
            item = QListWidgetItem(f"Press Key: {keys_str}", self.step_list)
            item.setData(Qt.UserRole, {"type": "keystroke", "keys": keys})
            self.step_list.addItem(item)

    def on_add_wait(self):
        text, ok1 = QInputDialog.getText(self, "Add Wait for Text", "Enter target text to wait for:")
        if ok1 and text:
            timeout, ok2 = QInputDialog.getInt(self, "Add Wait for Text", "Enter timeout in seconds:", 30, 1, 3600)
            if ok2:
                item = QListWidgetItem(f"Wait for Text: {text} ({timeout}s)", self.step_list)
                item.setData(Qt.UserRole, {"type": "wait_for_text", "text": text, "timeout_sec": timeout})
                self.step_list.addItem(item)

    def on_step_finished(self, index):
        if 0 <= index < self.step_list.count():
            item = self.step_list.item(index)
            item.setBackground(QColor("#2e7d32"))

    def setup_hotkey(self, hotkey_str):
        """
        Sets up the hotkey using HotkeyBridge for thread-safe cross-thread signal handling.
        """
        self.hotkey_bridge = HotkeyBridge()
        self.hotkey_bridge.hotkey_triggered.connect(self.start_current_workflow)
        
        def callback():
            self.hotkey_bridge.hotkey_triggered.emit()
            
        register_hotkey(hotkey_str, callback)

    def start_current_workflow(self):
        """
        Resets step list item backgrounds and spawns the runner thread.
        """
        steps = []
        for i in range(self.step_list.count()):
            item = self.step_list.item(i)
            steps.append(item.data(Qt.UserRole))
            
        # Reset colors
        for i in range(self.step_list.count()):
            self.step_list.item(i).setBackground(Qt.NoBrush)
            
        self.runner = WorkflowRunner(steps)
        self.runner.step_finished.connect(self.on_step_finished)
        self.runner.start()


