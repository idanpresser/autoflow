import sys
from os.path import abspath, dirname
import pytest
from PySide6.QtWidgets import QApplication

sys.path.insert(0, abspath(dirname(__file__)))

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
