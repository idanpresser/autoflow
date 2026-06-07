import pytest
from unittest.mock import patch, MagicMock
from src.engine.actions import focus_window

def test_focus_window_found():
    mock_win = MagicMock()
    mock_win.isMinimized = False
    
    with patch("pygetwindow.getWindowsWithTitle", return_value=[mock_win]) as mock_get:
        focus_window("My App")
        mock_get.assert_called_once_with("My App")
        mock_win.activate.assert_called_once()

def test_focus_window_not_found():
    with patch("pygetwindow.getWindowsWithTitle", return_value=[]) as mock_get:
        with pytest.raises(RuntimeError) as exc_info:
            focus_window("Nonexistent App")
        assert "not found" in str(exc_info.value)

def test_type_text():
    with patch("pyautogui.write") as mock_write:
        from src.engine.actions import type_text
        type_text("hello text")
        mock_write.assert_called_once_with("hello text", interval=0.05)

def test_send_keystroke():
    with patch("pyautogui.hotkey") as mock_hotkey:
        from src.engine.actions import send_keystroke
        send_keystroke(["ctrl", "c"])
        mock_hotkey.assert_called_once_with("ctrl", "c")

