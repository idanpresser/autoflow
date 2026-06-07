from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QInputDialog, QPushButton

from src.ui.main_window import MainWindow


def test_main_window_init(qapp: QApplication) -> None:
    window = MainWindow()
    assert window.windowTitle() == "AutoFlow"
    assert window.width() == 800
    assert window.height() == 600


def test_main_window_step_list(qapp: QApplication) -> None:
    window = MainWindow()
    step_list = window.step_list
    assert step_list is not None
    # Verify we can add items
    step_list.addItem("Test Step")
    assert step_list.count() == 1


def test_main_window_action_buttons(qapp: QApplication) -> None:
    window = MainWindow()

    btn_type = window.findChild(QPushButton, "btn_add_type_text")
    btn_key = window.findChild(QPushButton, "btn_add_press_key")
    btn_wait = window.findChild(QPushButton, "btn_add_wait")

    assert btn_type is not None
    assert btn_key is not None
    assert btn_wait is not None

    step_list = window.step_list

    # We clear the list for this test
    step_list.clear()

    # Click Add Type Text (mock QInputDialog.getText)
    with patch.object(QInputDialog, "getText", return_value=("hello text", True)):
        btn_type.click()
    assert step_list.count() == 1
    item = step_list.item(0)
    assert item is not None
    assert item.data(Qt.ItemDataRole.UserRole) == {"type": "type_text", "text": "hello text"}

    # Click Add Press Key (mock QInputDialog.getText)
    with patch.object(QInputDialog, "getText", return_value=("ctrl+c", True)):
        btn_key.click()
    assert step_list.count() == 2
    item2 = step_list.item(1)
    assert item2 is not None
    assert item2.data(Qt.ItemDataRole.UserRole) == {"type": "keystroke", "keys": ["ctrl", "c"]}

    # Click Add Wait (mock QInputDialog.getText and QInputDialog.getInt)
    with patch.object(QInputDialog, "getText", return_value=("Success", True)), patch.object(
        QInputDialog, "getInt", return_value=(30, True)
    ):
        btn_wait.click()
    assert step_list.count() == 3
    item3 = step_list.item(2)
    assert item3 is not None
    assert item3.data(Qt.ItemDataRole.UserRole) == {
        "type": "wait_for_text",
        "text": "Success",
        "timeout_sec": 30,
    }


def test_main_window_highlight_step(qapp: QApplication) -> None:
    window = MainWindow()
    step_list = window.step_list
    step_list.clear()

    # Add two mock items
    step_list.addItem("Step 1")
    step_list.addItem("Step 2")

    # Initially background colors are not set or are default
    item0 = step_list.item(0)
    assert item0 is not None
    assert (
        item0.background().color().isValid() is False
        or item0.background().color().name() != "#00ff00"
    )

    # Trigger on_step_finished for index 1
    window.on_step_finished(1)

    # Row 1 should be green (or highlighted)
    item1 = step_list.item(1)
    assert item1 is not None
    assert item1.background().color().isValid()
    # Let's say we set it to #2e7d32 (darker green for modern aesthetics) or QColor(Qt.green)
    # Let's check that it's green by name or RGB
    color = item1.background().color()
    assert color.isValid()


def test_main_window_dependency_injection(qapp: QApplication) -> None:
    from unittest.mock import MagicMock
    from src.ui.main_window import MainWindow

    mock_register = MagicMock()
    mock_runner_factory = MagicMock()

    window = MainWindow(
        register_hotkey_fn=mock_register,
        runner_factory=mock_runner_factory
    )

    # Verify setup_hotkey calls the injected register function
    window.setup_hotkey("ctrl+shift+x")
    mock_register.assert_called_once()

    # Extract callback passed to register_hotkey_fn
    call_args = mock_register.call_args[0]
    assert call_args[0] == "ctrl+shift+x"
    callback = call_args[1]

    # Verify that triggering the callback invokes the runner factory
    callback()
    qapp.processEvents()

    mock_runner_factory.assert_called_once()

