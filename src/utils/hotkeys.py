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


def unregister_hotkey(hotkey_str: str) -> None:
    """
    Unregisters a previously registered global hotkey.
    Raises HotkeyRegistrationError if unregistration fails.
    """
    try:
        keyboard.remove_hotkey(hotkey_str)
    except Exception as e:
        raise HotkeyRegistrationError(
            f"Failed to unregister hotkey '{hotkey_str}': {e}"
        ) from e


def unregister_all() -> None:
    """
    Unregisters all previously registered global hotkeys.
    Raises HotkeyRegistrationError if unregistration fails.
    """
    try:
        keyboard.unhook_all_hotkeys()
    except Exception as e:
        raise HotkeyRegistrationError(
            f"Failed to unregister all hotkeys: {e}"
        ) from e
