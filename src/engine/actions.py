import pygetwindow as gw
import pyautogui

# Enforce pyautogui fail-safe as required by the alignment constraints
pyautogui.FAILSAFE = True

def focus_window(title):
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
            raise RuntimeError(f"Failed to focus window '{title}': {e}")

def type_text(text):
    """
    Types the specified text using pyautogui with a small safe interval.
    """
    pyautogui.write(text, interval=0.05)

def send_keystroke(keys):
    """
    Sends a keystroke combination.
    """
    pyautogui.hotkey(*keys)

