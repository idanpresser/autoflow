from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from src.ui.main_window import MainWindow
from src.ui.tray_icon import SystemTrayIcon


def test_system_tray_icon(qapp: QApplication) -> None:
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


def test_main_window_close_event_minimizes(qapp: QApplication) -> None:
    window = MainWindow()
    window.show()
    assert window.isVisible() is True

    event = QCloseEvent()
    window.closeEvent(event)

    assert event.isAccepted() is False
    assert window.isVisible() is False
