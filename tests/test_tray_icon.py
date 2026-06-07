import pytest
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QCloseEvent
from src.ui.tray_icon import SystemTrayIcon
from src.ui.main_window import MainWindow

def test_system_tray_icon(qapp):
    window = MainWindow()
    tray = SystemTrayIcon(window)
    assert isinstance(tray, QSystemTrayIcon)
    
    menu = tray.contextMenu()
    assert menu is not None
    assert isinstance(menu, QMenu)
    
    actions = menu.actions()
    action_texts = [act.text() for act in actions]
    assert any("Restore" in text for text in action_texts)
    assert any("Exit" in text for text in action_texts)

def test_main_window_close_event_minimizes(qapp):
    window = MainWindow()
    window.show()
    assert window.isVisible() is True
    
    event = QCloseEvent()
    window.closeEvent(event)
    
    assert event.isAccepted() is False
    assert window.isVisible() is False
