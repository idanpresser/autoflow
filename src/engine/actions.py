import logging
import subprocess
import time

import pyautogui
import pygetwindow as gw

logger = logging.getLogger(__name__)

# Enforce pyautogui fail-safe as required by the alignment constraints
pyautogui.FAILSAFE = True


def focus_window(title: str) -> None:
    """
    Finds a window with the given title and brings it to the foreground.
    Raises RuntimeError if no window is found.
    """
    windows = gw.getWindowsWithTitle(title)
    if not windows:
        raise RuntimeError(f"Window with title '{title}' not found")

    win = windows[0]
    try:
        if hasattr(win, "isMinimized") and win.isMinimized:
            win.restore()
        win.activate()
    except Exception:
        try:
            win.restore()
            win.activate()
        except Exception as e:
            raise RuntimeError(f"Failed to focus window '{title}': {e}") from e


DEFAULT_TYPING_INTERVAL = 0.05


def type_text(text: str) -> None:
    """
    Types the specified text using pyautogui with a small safe interval.
    """
    pyautogui.write(text, interval=DEFAULT_TYPING_INTERVAL)


def send_keystroke(keys: list[str]) -> None:
    """
    Sends a keystroke combination.
    """
    pyautogui.hotkey(*keys)


def copy_and_match(pattern: str) -> str | None:
    """
    Gets clipboard text via pyperclip.paste(), applies re.search(pattern, text),
    and returns the first captured group (or the full match if no groups).
    Returns None if no match is found.
    """
    import re

    import pyperclip

    text = pyperclip.paste()
    match = re.search(pattern, text)
    if not match:
        return None
    if match.groups():
        return match.group(1)
    return match.group(0)


def wait_delay(seconds: float) -> None:
    """
    Pauses execution for the specified number of seconds.
    """
    logger.info("Waiting for %.1f seconds", seconds)
    time.sleep(seconds)


def run_command(command: str, timeout: float = 60.0) -> str:
    """
    Executes a shell command and returns its stdout output.
    Raises RuntimeError if the command fails or times out.
    """
    logger.info("Running command: %s", command)
    try:
        result = subprocess.run(
            command,
            shell=True,  # noqa: S602
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            error_msg = result.stderr.strip() or f"Command exited with code {result.returncode}"
            raise RuntimeError(f"Command failed: {error_msg}")
        return result.stdout
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"Command timed out after {timeout}s: {command}") from e

