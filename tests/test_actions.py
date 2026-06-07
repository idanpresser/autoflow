from unittest.mock import MagicMock, patch

import pytest

from src.engine.actions import focus_window


def test_focus_window_found() -> None:
    mock_win = MagicMock()
    mock_win.isMinimized = False

    with patch("pygetwindow.getWindowsWithTitle", return_value=[mock_win]) as mock_get:
        focus_window("My App")
        mock_get.assert_called_once_with("My App")
        mock_win.activate.assert_called_once()


def test_focus_window_not_found() -> None:
    with patch("pygetwindow.getWindowsWithTitle", return_value=[]):
        with pytest.raises(RuntimeError) as exc_info:
            focus_window("Nonexistent App")
        assert "not found" in str(exc_info.value)


def test_type_text() -> None:
    with patch("pyautogui.write") as mock_write:
        from src.engine.actions import type_text

        type_text("hello text")
        mock_write.assert_called_once_with("hello text", interval=0.05)


def test_send_keystroke() -> None:
    with patch("pyautogui.hotkey") as mock_hotkey:
        from src.engine.actions import send_keystroke

        send_keystroke(["ctrl", "c"])
        mock_hotkey.assert_called_once_with("ctrl", "c")


def test_copy_and_match() -> None:
    with patch("pyperclip.paste", return_value="ErrorCode: 404 Not Found") as mock_paste:
        from src.engine.actions import copy_and_match

        result = copy_and_match(r"ErrorCode:\s*(\d+)")
        assert result == "404"
        mock_paste.assert_called_once()


def test_copy_and_match_no_match() -> None:
    with patch("pyperclip.paste", return_value="Success"):
        from src.engine.actions import copy_and_match

        result = copy_and_match(r"ErrorCode:\s*(\d+)")
        assert result is None


def test_extracted_constants() -> None:
    from src.engine.actions import DEFAULT_TYPING_INTERVAL
    from src.engine.runner import DEFAULT_OCR_POLL_INTERVAL
    from src.ui.main_window import HIGHLIGHT_SUCCESS_COLOR

    assert DEFAULT_TYPING_INTERVAL == 0.05
    assert DEFAULT_OCR_POLL_INTERVAL == 0.5
    assert HIGHLIGHT_SUCCESS_COLOR == "#2e7d32"

