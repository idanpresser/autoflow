from collections.abc import Callable

import keyboard


class HotkeyRegistrationError(Exception):
    pass


def register_hotkey(hotkey_str: str, callback: Callable[[], None]) -> None:
    """
    Registers a global hotkey with the keyboard module.
    Raises HotkeyRegistrationError if registration fails.
    """
    try:
        keyboard.add_hotkey(hotkey_str, callback)
    except Exception as e:
        raise HotkeyRegistrationError(
            f"Failed to register hotkey '{hotkey_str}': {e}"
        ) from e
