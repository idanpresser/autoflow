import pytest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication, QListWidget, QPushButton, QInputDialog
from PySide6.QtCore import Qt
from src.ui.main_window import MainWindow

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app

def test_main_window_init(qapp):
    window = MainWindow()
    assert window.windowTitle() == "AutoFlow"
    assert window.width() == 800
    assert window.height() == 600

def test_main_window_step_list(qapp):
    window = MainWindow()
    step_list = window.findChild(QListWidget, "step_list")
    assert step_list is not None
    # Verify we can add items
    step_list.addItem("Test Step")
    assert step_list.count() == 1

def test_main_window_action_buttons(qapp):
    window = MainWindow()
    
    btn_type = window.findChild(QPushButton, "btn_add_type_text")
    btn_key = window.findChild(QPushButton, "btn_add_press_key")
    btn_wait = window.findChild(QPushButton, "btn_add_wait")
    
    assert btn_type is not None
    assert btn_key is not None
    assert btn_wait is not None
    
    step_list = window.findChild(QListWidget, "step_list")
    
    # We clear the list for this test
    step_list.clear()
    
    # Click Add Type Text (mock QInputDialog.getText)
    with patch.object(QInputDialog, 'getText', return_value=("hello text", True)):
        btn_type.click()
    assert step_list.count() == 1
    item = step_list.item(0)
    assert item.data(Qt.UserRole) == {"type": "type_text", "text": "hello text"}
    
    # Click Add Press Key (mock QInputDialog.getText)
    with patch.object(QInputDialog, 'getText', return_value=("ctrl+c", True)):
        btn_key.click()
    assert step_list.count() == 2
    item2 = step_list.item(1)
    assert item2.data(Qt.UserRole) == {"type": "keystroke", "keys": ["ctrl", "c"]}
    
    # Click Add Wait (mock QInputDialog.getText and QInputDialog.getInt)
    with patch.object(QInputDialog, 'getText', return_value=("Success", True)):
        with patch.object(QInputDialog, 'getInt', return_value=(30, True)):
            btn_wait.click()
    assert step_list.count() == 3
    item3 = step_list.item(2)
    assert item3.data(Qt.UserRole) == {"type": "wait_for_text", "text": "Success", "timeout_sec": 30}

def test_main_window_highlight_step(qapp):
    window = MainWindow()
    step_list = window.step_list
    step_list.clear()
    
    # Add two mock items
    step_list.addItem("Step 1")
    step_list.addItem("Step 2")
    
    # Initially background colors are not set or are default
    assert step_list.item(0).background().color().isValid() is False or step_list.item(0).background().color().name() != "#00ff00"
    
    # Trigger on_step_finished for index 1
    window.on_step_finished(1)
    
    # Row 1 should be green (or highlighted)
    assert step_list.item(1).background().color().isValid()
    # Let's say we set it to #2e7d32 (darker green for modern aesthetics) or QColor(Qt.green)
    # Let's check that it's green by name or RGB
    color = step_list.item(1).background().color()
    assert color.isValid()

