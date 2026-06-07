from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QCloseEvent, QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


from src.engine.runner import WorkflowRunner
from src.utils.config import StepType
from src.utils.hotkeys import register_hotkey


class HotkeyBridge(QObject):
    hotkey_triggered = Signal()


HIGHLIGHT_SUCCESS_COLOR = "#2e7d32"

DARK_THEME_QSS = """
QMainWindow {
    background-color: #1e1e1e;
}
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Segoe UI", "Roboto", sans-serif;
    font-size: 13px;
}
QLabel {
    color: #b0b0b0;
    font-weight: 500;
}
QListWidget {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    padding: 4px;
    outline: none;
}
QListWidget::item {
    padding: 6px 10px;
    border-radius: 4px;
    margin: 2px 0;
}
QListWidget::item:selected {
    background-color: #4fc3f7;
    color: #1e1e1e;
}
QListWidget::item:hover {
    background-color: #3d3d3d;
}
QPushButton {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 500;
    min-height: 28px;
}
QPushButton:hover {
    background-color: #3d3d3d;
    border-color: #4fc3f7;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #4fc3f7;
    color: #1e1e1e;
}
QPushButton#btn_stop {
    background-color: #c62828;
    border-color: #e53935;
    color: #ffffff;
}
QPushButton#btn_stop:hover {
    background-color: #e53935;
}
QPushButton#btn_delete_step {
    background-color: #4a2020;
    border-color: #c62828;
    color: #ef9a9a;
}
QPushButton#btn_delete_step:hover {
    background-color: #c62828;
    color: #ffffff;
}
QComboBox {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    padding: 5px 10px;
    min-height: 24px;
}
QComboBox:hover {
    border-color: #4fc3f7;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    selection-background-color: #4fc3f7;
    selection-color: #1e1e1e;
}
QMenu {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
}
QMenu::item:selected {
    background-color: #4fc3f7;
    color: #1e1e1e;
}
"""


class MainWindow(QMainWindow):
    def __init__(
        self,
        register_hotkey_fn: Callable[[str, Callable[[], None]], None] | None = None,
        runner_factory: Callable[[list[dict[str, Any]]], WorkflowRunner] | None = None,
    ) -> None:
        super().__init__()
        self._register_hotkey_fn = (
            register_hotkey_fn if register_hotkey_fn is not None else register_hotkey
        )
        self._runner_factory = runner_factory if runner_factory is not None else WorkflowRunner
        self.runner: WorkflowRunner | None = None
        self.setWindowTitle("AutoFlow")
        self.resize(800, 600)

        # Apply dark theme
        self.setStyleSheet(DARK_THEME_QSS)

        # Central widget and layout
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # OCR Engine selection panel
        ocr_layout = QHBoxLayout()
        ocr_label = QLabel("OCR Engine:", central_widget)
        ocr_layout.addWidget(ocr_label)

        self.ocr_combo = QComboBox(central_widget)
        self.ocr_combo.setObjectName("ocr_combo")
        self.ocr_combo.addItem("Tesseract (Local)")
        self.ocr_combo.addItem("Mistral (Cloud)")

        import os
        default_provider = os.getenv("OCR_PROVIDER", "tesseract").lower().strip()
        if default_provider == "mistral":
            self.ocr_combo.setCurrentIndex(1)
        else:
            self.ocr_combo.setCurrentIndex(0)

        ocr_layout.addWidget(self.ocr_combo)
        ocr_layout.addStretch()
        main_layout.addLayout(ocr_layout)

        # --- Primary step-type buttons (row 1) ---
        buttons_layout = QHBoxLayout()

        self.btn_add_type = QPushButton("Add Type Text", central_widget)
        self.btn_add_type.setObjectName("btn_add_type_text")
        self.btn_add_type.clicked.connect(self.on_add_type_text)
        buttons_layout.addWidget(self.btn_add_type)

        self.btn_add_key = QPushButton("Add Press Key", central_widget)
        self.btn_add_key.setObjectName("btn_add_press_key")
        self.btn_add_key.clicked.connect(self.on_add_press_key)
        buttons_layout.addWidget(self.btn_add_key)

        self.btn_add_wait = QPushButton("Add Wait for Text", central_widget)
        self.btn_add_wait.setObjectName("btn_add_wait")
        self.btn_add_wait.clicked.connect(self.on_add_wait)
        buttons_layout.addWidget(self.btn_add_wait)

        self.btn_add_focus_window = QPushButton("Focus Window", central_widget)
        self.btn_add_focus_window.setObjectName("btn_add_focus_window")
        self.btn_add_focus_window.clicked.connect(self.on_add_focus_window)
        buttons_layout.addWidget(self.btn_add_focus_window)

        main_layout.addLayout(buttons_layout)

        # --- Additional step-type buttons (row 2) ---
        buttons_layout_2 = QHBoxLayout()

        self.btn_add_delay = QPushButton("Add Wait (Delay)", central_widget)
        self.btn_add_delay.setObjectName("btn_add_delay")
        self.btn_add_delay.clicked.connect(self.on_add_delay)
        buttons_layout_2.addWidget(self.btn_add_delay)

        self.btn_add_wait_image = QPushButton("Wait for Image", central_widget)
        self.btn_add_wait_image.setObjectName("btn_add_wait_image")
        self.btn_add_wait_image.clicked.connect(self.on_add_wait_image)
        buttons_layout_2.addWidget(self.btn_add_wait_image)

        self.btn_add_copy_parse = QPushButton("Copy && Parse", central_widget)
        self.btn_add_copy_parse.setObjectName("btn_add_copy_parse")
        self.btn_add_copy_parse.clicked.connect(self.on_add_copy_parse)
        buttons_layout_2.addWidget(self.btn_add_copy_parse)

        self.btn_add_run_command = QPushButton("Run Command", central_widget)
        self.btn_add_run_command.setObjectName("btn_add_run_command")
        self.btn_add_run_command.clicked.connect(self.on_add_run_command)
        buttons_layout_2.addWidget(self.btn_add_run_command)

        main_layout.addLayout(buttons_layout_2)

        # --- Control buttons (Stop, Delete) ---
        control_layout = QHBoxLayout()

        self.btn_stop = QPushButton("Stop", central_widget)
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.clicked.connect(self.on_stop_workflow)
        control_layout.addWidget(self.btn_stop)

        self.btn_delete_step = QPushButton("Delete Step", central_widget)
        self.btn_delete_step.setObjectName("btn_delete_step")
        self.btn_delete_step.clicked.connect(self.on_delete_step)
        control_layout.addWidget(self.btn_delete_step)

        control_layout.addStretch()
        main_layout.addLayout(control_layout)

        # Step list widget with drag-and-drop reordering
        self.step_list = QListWidget(central_widget)
        self.step_list.setObjectName("step_list")
        self.step_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.step_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.step_list.itemDoubleClicked.connect(self.on_edit_step)
        main_layout.addWidget(self.step_list)

        self.setCentralWidget(central_widget)

    # ------------------------------------------------------------------ #
    #  Step-type handlers
    # ------------------------------------------------------------------ #

    def on_add_type_text(self) -> None:
        text, ok = QInputDialog.getText(self, "Add Type Text", "Enter text to type:")
        if ok and text:
            item = QListWidgetItem(f"Type Text: {text}", self.step_list)
            item.setData(Qt.ItemDataRole.UserRole, {"type": StepType.TYPE_TEXT, "text": text})
            self.step_list.addItem(item)

    def on_add_press_key(self) -> None:
        keys_str, ok = QInputDialog.getText(self, "Add Press Key", "Enter keys (e.g. ctrl+c):")
        if ok and keys_str:
            keys = [k.strip() for k in keys_str.split("+") if k.strip()]
            item = QListWidgetItem(f"Press Key: {keys_str}", self.step_list)
            item.setData(Qt.ItemDataRole.UserRole, {"type": StepType.KEYSTROKE, "keys": keys})
            self.step_list.addItem(item)

    def on_add_wait(self) -> None:
        text, ok1 = QInputDialog.getText(
            self, "Add Wait for Text", "Enter target text to wait for:"
        )
        if ok1 and text:
            timeout, ok2 = QInputDialog.getInt(
                self, "Add Wait for Text", "Enter timeout in seconds:", 30, 1, 3600
            )
            if ok2:
                item = QListWidgetItem(f"Wait for Text: {text} ({timeout}s)", self.step_list)
                item.setData(
                    Qt.ItemDataRole.UserRole,
                    {"type": StepType.WAIT_FOR_TEXT, "text": text, "timeout_sec": timeout},
                )
                self.step_list.addItem(item)

    def on_add_focus_window(self) -> None:
        title, ok = QInputDialog.getText(
            self, "Focus Window", "Enter window title to focus:"
        )
        if ok and title:
            item = QListWidgetItem(f"Focus Window: {title}", self.step_list)
            item.setData(
                Qt.ItemDataRole.UserRole,
                {"type": StepType.FOCUS_WINDOW, "title": title},
            )
            self.step_list.addItem(item)

    def on_add_delay(self) -> None:
        seconds, ok = QInputDialog.getDouble(
            self, "Add Wait (Delay)", "Enter delay in seconds:", 1.0, 0.1, 3600.0, 1
        )
        if ok:
            item = QListWidgetItem(f"Wait: {seconds}s", self.step_list)
            item.setData(
                Qt.ItemDataRole.UserRole,
                {"type": StepType.WAIT, "seconds": seconds},
            )
            self.step_list.addItem(item)

    def on_add_wait_image(self) -> None:
        image_path, ok = QInputDialog.getText(
            self, "Wait for Image", "Enter image file path to wait for:"
        )
        if ok and image_path:
            timeout, ok2 = QInputDialog.getInt(
                self, "Wait for Image", "Enter timeout in seconds:", 30, 1, 3600
            )
            if ok2:
                item = QListWidgetItem(
                    f"Wait for Image: {image_path} ({timeout}s)", self.step_list
                )
                item.setData(
                    Qt.ItemDataRole.UserRole,
                    {
                        "type": StepType.WAIT_FOR_IMAGE,
                        "image_path": image_path,
                        "timeout_sec": timeout,
                    },
                )
                self.step_list.addItem(item)

    def on_add_copy_parse(self) -> None:
        pattern, ok = QInputDialog.getText(
            self, "Copy & Parse", "Enter regex pattern to parse from clipboard:"
        )
        if ok and pattern:
            item = QListWidgetItem(f"Copy & Parse: {pattern}", self.step_list)
            item.setData(
                Qt.ItemDataRole.UserRole,
                {"type": StepType.COPY_PARSE, "pattern": pattern},
            )
            self.step_list.addItem(item)

    def on_add_run_command(self) -> None:
        command, ok = QInputDialog.getText(
            self, "Run Command", "Enter command to run:"
        )
        if ok and command:
            item = QListWidgetItem(f"Run Command: {command}", self.step_list)
            item.setData(
                Qt.ItemDataRole.UserRole,
                {"type": StepType.RUN_COMMAND, "command": command},
            )
            self.step_list.addItem(item)

    # ------------------------------------------------------------------ #
    #  Step management
    # ------------------------------------------------------------------ #

    def on_delete_step(self) -> None:
        """Removes the currently selected step from the list."""
        current_row = self.step_list.currentRow()
        if current_row >= 0:
            self.step_list.takeItem(current_row)

    def on_edit_step(self, item: QListWidgetItem) -> None:
        """Opens a dialog to edit the double-clicked step."""
        data = item.data(Qt.ItemDataRole.UserRole)
        if data is None:
            return

        step_type = data.get("type")

        if step_type == StepType.TYPE_TEXT:
            text, ok = QInputDialog.getText(
                self, "Edit Type Text", "Enter text to type:", text=data.get("text", "")
            )
            if ok and text:
                item.setText(f"Type Text: {text}")
                item.setData(Qt.ItemDataRole.UserRole, {"type": StepType.TYPE_TEXT, "text": text})

        elif step_type == StepType.KEYSTROKE:
            keys_str, ok = QInputDialog.getText(
                self,
                "Edit Press Key",
                "Enter keys (e.g. ctrl+c):",
                text="+".join(data.get("keys", [])),
            )
            if ok and keys_str:
                keys = [k.strip() for k in keys_str.split("+") if k.strip()]
                item.setText(f"Press Key: {keys_str}")
                item.setData(
                    Qt.ItemDataRole.UserRole, {"type": StepType.KEYSTROKE, "keys": keys}
                )

        elif step_type == StepType.WAIT_FOR_TEXT:
            text, ok = QInputDialog.getText(
                self, "Edit Wait for Text", "Enter target text:", text=data.get("text", "")
            )
            if ok and text:
                timeout, ok2 = QInputDialog.getInt(
                    self,
                    "Edit Wait for Text",
                    "Enter timeout in seconds:",
                    data.get("timeout_sec", 30),
                    1,
                    3600,
                )
                if ok2:
                    item.setText(f"Wait for Text: {text} ({timeout}s)")
                    item.setData(
                        Qt.ItemDataRole.UserRole,
                        {"type": StepType.WAIT_FOR_TEXT, "text": text, "timeout_sec": timeout},
                    )

        elif step_type == StepType.FOCUS_WINDOW:
            title, ok = QInputDialog.getText(
                self, "Edit Focus Window", "Enter window title:", text=data.get("title", "")
            )
            if ok and title:
                item.setText(f"Focus Window: {title}")
                item.setData(
                    Qt.ItemDataRole.UserRole,
                    {"type": StepType.FOCUS_WINDOW, "title": title},
                )

        elif step_type == StepType.WAIT:
            seconds, ok = QInputDialog.getDouble(
                self,
                "Edit Wait (Delay)",
                "Enter delay in seconds:",
                data.get("seconds", 1.0),
                0.1,
                3600.0,
                1,
            )
            if ok:
                item.setText(f"Wait: {seconds}s")
                item.setData(
                    Qt.ItemDataRole.UserRole,
                    {"type": StepType.WAIT, "seconds": seconds},
                )

        elif step_type == StepType.WAIT_FOR_IMAGE:
            image_path, ok = QInputDialog.getText(
                self,
                "Edit Wait for Image",
                "Enter image file path:",
                text=data.get("image_path", ""),
            )
            if ok and image_path:
                timeout, ok2 = QInputDialog.getInt(
                    self,
                    "Edit Wait for Image",
                    "Enter timeout in seconds:",
                    data.get("timeout_sec", 30),
                    1,
                    3600,
                )
                if ok2:
                    item.setText(f"Wait for Image: {image_path} ({timeout}s)")
                    item.setData(
                        Qt.ItemDataRole.UserRole,
                        {
                            "type": StepType.WAIT_FOR_IMAGE,
                            "image_path": image_path,
                            "timeout_sec": timeout,
                        },
                    )

        elif step_type == StepType.COPY_PARSE:
            pattern, ok = QInputDialog.getText(
                self,
                "Edit Copy & Parse",
                "Enter regex pattern:",
                text=data.get("pattern", ""),
            )
            if ok and pattern:
                item.setText(f"Copy & Parse: {pattern}")
                item.setData(
                    Qt.ItemDataRole.UserRole,
                    {"type": StepType.COPY_PARSE, "pattern": pattern},
                )

        elif step_type == StepType.RUN_COMMAND:
            command, ok = QInputDialog.getText(
                self,
                "Edit Run Command",
                "Enter command:",
                text=data.get("command", ""),
            )
            if ok and command:
                item.setText(f"Run Command: {command}")
                item.setData(
                    Qt.ItemDataRole.UserRole,
                    {"type": StepType.RUN_COMMAND, "command": command},
                )

    # ------------------------------------------------------------------ #
    #  Workflow execution
    # ------------------------------------------------------------------ #

    def on_step_finished(self, index: int) -> None:
        if 0 <= index < self.step_list.count():
            item = self.step_list.item(index)
            item.setBackground(QColor(HIGHLIGHT_SUCCESS_COLOR))

    def on_stop_workflow(self) -> None:
        """Stops the currently running workflow, if any."""
        if self.runner is not None:
            self.runner.stop()

    def setup_hotkey(self, hotkey_str: str) -> None:
        """
        Sets up the hotkey using HotkeyBridge for thread-safe cross-thread signal handling.
        """
        self.hotkey_bridge = HotkeyBridge()
        self.hotkey_bridge.hotkey_triggered.connect(self.start_current_workflow)

        def callback() -> None:
            self.hotkey_bridge.hotkey_triggered.emit()

        self._register_hotkey_fn(hotkey_str, callback)

    def start_current_workflow(self) -> None:
        """
        Resets step list item backgrounds and spawns the runner thread.
        """
        from src.vision.ocr import TesseractVisionProvider, MistralVisionProvider

        steps = []
        for i in range(self.step_list.count()):
            item = self.step_list.item(i)
            steps.append(item.data(Qt.ItemDataRole.UserRole))

        # Reset colors
        for i in range(self.step_list.count()):
            self.step_list.item(i).setBackground(Qt.BrushStyle.NoBrush)

        # Resolve selected OCR provider from combobox
        selected_text = self.ocr_combo.currentText()
        if "Mistral" in selected_text:
            try:
                vision_provider = MistralVisionProvider()
            except ValueError as e:
                QMessageBox.warning(self, "OCR Configuration Error", str(e))
                return
        else:
            vision_provider = TesseractVisionProvider()

        self.runner = self._runner_factory(steps, vision_provider=vision_provider)
        self.runner.step_finished.connect(self.on_step_finished)
        self.runner.workflow_completed.connect(self._on_workflow_completed)
        self.runner.error_occurred.connect(self._on_error_occurred)
        self.runner.start()

    def _on_workflow_completed(self, message: str) -> None:
        """Displays a success message when the workflow completes."""
        QMessageBox.information(self, "Workflow Completed", message)

    def _on_error_occurred(self, error: str) -> None:
        """Displays an error message when the workflow encounters an error."""
        QMessageBox.critical(self, "Workflow Error", error)

    # ------------------------------------------------------------------ #
    #  Window events
    # ------------------------------------------------------------------ #

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """
        Overrides the close event to minimize to tray instead of closing.
        """
        event.ignore()
        self.hide()
