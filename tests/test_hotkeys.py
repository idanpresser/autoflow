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

def test_hotkey_spawns_runner(qapp):
    from src.ui.main_window import MainWindow
    from unittest.mock import patch
    
    window = MainWindow()
    
    with patch("src.ui.main_window.register_hotkey") as mock_register:
        with patch("src.engine.runner.WorkflowRunner.start") as mock_start:
            window.setup_hotkey("ctrl+shift+p")
            mock_register.assert_called_once()
            
            # Trigger callback
            callback = mock_register.call_args[0][1]
            callback()
            
            qapp.processEvents()
            
            mock_start.assert_called_once()
            assert window.runner is not None

