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

    assert DEFAULT_TYPING_INTERVAL == 0.05
    assert DEFAULT_OCR_POLL_INTERVAL == 0.5


def test_wait_delay() -> None:
    with patch("src.engine.actions.time.sleep") as mock_sleep:
        from src.engine.actions import wait_delay

        wait_delay(2.5)
        mock_sleep.assert_called_once_with(2.5)


def test_run_command_success() -> None:
    with patch("src.engine.actions.subprocess.run") as mock_run:
        from src.engine.actions import run_command

        mock_run.return_value = MagicMock(returncode=0, stdout="hello\n", stderr="")
        result = run_command("echo hello")
        assert result == "hello\n"
        mock_run.assert_called_once()


def test_run_command_failure() -> None:
    with patch("src.engine.actions.subprocess.run") as mock_run:
        from src.engine.actions import run_command

        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="command not found"
        )
        with pytest.raises(RuntimeError, match="Command failed"):
            run_command("bad_command")


def test_run_command_timeout() -> None:
    import subprocess

    with patch(
        "src.engine.actions.subprocess.run",
        side_effect=subprocess.TimeoutExpired("cmd", 5),
    ):
        from src.engine.actions import run_command

        with pytest.raises(RuntimeError, match="timed out"):
            run_command("slow_command", timeout=5)


