import pytest
from PySide6.QtWidgets import QApplication, QListWidget
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
