import pytest
from unittest.mock import patch

def test_register_hotkey_success():
    with patch("keyboard.add_hotkey") as mock_add:
        from src.utils.hotkeys import register_hotkey
        
        def callback():
            pass
            
        register_hotkey("ctrl+shift+r", callback)
        mock_add.assert_called_once_with("ctrl+shift+r", callback)

def test_register_hotkey_failure():
    with patch("keyboard.add_hotkey", side_effect=Exception("Invalid hotkey")):
        from src.utils.hotkeys import register_hotkey, HotkeyRegistrationError
        
        with pytest.raises(HotkeyRegistrationError) as exc_info:
            register_hotkey("invalid-key", lambda: None)
        assert "Failed to register hotkey" in str(exc_info.value)
