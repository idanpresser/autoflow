from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QApplication


def test_register_hotkey_success() -> None:
    with patch("keyboard.add_hotkey") as mock_add:
        from src.utils.hotkeys import register_hotkey

        def callback() -> None:
            pass

        register_hotkey("ctrl+shift+r", callback)
        mock_add.assert_called_once_with("ctrl+shift+r", callback)


def test_register_hotkey_failure() -> None:
    with patch("keyboard.add_hotkey", side_effect=Exception("Invalid hotkey")):
        from src.utils.hotkeys import HotkeyRegistrationError, register_hotkey

        with pytest.raises(HotkeyRegistrationError) as exc_info:
            register_hotkey("invalid-key", lambda: None)
        assert "Failed to register hotkey" in str(exc_info.value)


def test_hotkey_spawns_runner(qapp: QApplication) -> None:
    from unittest.mock import patch

    from src.ui.main_window import MainWindow

    window = MainWindow()

    with patch("src.ui.main_window.register_hotkey") as mock_register, patch(
        "src.engine.runner.WorkflowRunner.start"
    ) as mock_start:
        window.setup_hotkey("ctrl+shift+p")
        mock_register.assert_called_once()

        # Trigger callback
        callback = mock_register.call_args[0][1]
        callback()

        qapp.processEvents()

        mock_start.assert_called_once()
        assert window.runner is not None
