import pytest
import json
from src.utils.config import serialize_profile, ValidationError

def test_serialize_profile_success():
    profile = {
        "profile_name": "Test Profile",
        "hotkey": "ctrl+alt+a",
        "steps": [
            {"type": "type_text", "text": "hello"}
        ]
    }
    result = serialize_profile(profile)
    parsed = json.loads(result)
    assert parsed["profile_name"] == "Test Profile"
    assert parsed["hotkey"] == "ctrl+alt+a"
    assert parsed["steps"][0]["type"] == "type_text"

def test_serialize_profile_missing_keys():
    # Missing profile_name
    profile1 = {
        "hotkey": "ctrl+alt+a",
        "steps": []
    }
    with pytest.raises(ValidationError) as excinfo:
        serialize_profile(profile1)
    assert "profile_name" in str(excinfo.value)

    # Missing hotkey
    profile2 = {
        "profile_name": "Test Profile",
        "steps": []
    }
    with pytest.raises(ValidationError) as excinfo:
        serialize_profile(profile2)
    assert "hotkey" in str(excinfo.value)

    # Missing steps
    profile3 = {
        "profile_name": "Test Profile",
        "hotkey": "ctrl+alt+a"
    }
    with pytest.raises(ValidationError) as excinfo:
        serialize_profile(profile3)
    assert "steps" in str(excinfo.value)

def test_serialize_profile_invalid_steps():
    profile = {
        "profile_name": "Test Profile",
        "hotkey": "ctrl+alt+a",
        "steps": "not a list"
    }
    with pytest.raises(ValidationError) as excinfo:
        serialize_profile(profile)
    assert "steps must be a list" in str(excinfo.value)
