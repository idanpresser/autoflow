import json
from pathlib import Path

import pytest

from src.utils.config import (
    ValidationError,
    load_profile_from_file,
    save_profile_to_file,
    serialize_profile,
)


def test_serialize_profile_success() -> None:
    profile = {
        "profile_name": "Test Profile",
        "hotkey": "ctrl+alt+a",
        "steps": [{"type": "type_text", "text": "hello"}],
    }
    result = serialize_profile(profile)
    parsed = json.loads(result)
    assert parsed["profile_name"] == "Test Profile"
    assert parsed["hotkey"] == "ctrl+alt+a"
    assert parsed["steps"][0]["type"] == "type_text"


def test_serialize_profile_missing_keys() -> None:
    # Missing profile_name
    profile1 = {"hotkey": "ctrl+alt+a", "steps": []}
    with pytest.raises(ValidationError) as excinfo:
        serialize_profile(profile1)
    assert "profile_name" in str(excinfo.value)

    # Missing hotkey
    profile2 = {"profile_name": "Test Profile", "steps": []}
    with pytest.raises(ValidationError) as excinfo:
        serialize_profile(profile2)
    assert "hotkey" in str(excinfo.value)

    # Missing steps
    profile3 = {"profile_name": "Test Profile", "hotkey": "ctrl+alt+a"}
    with pytest.raises(ValidationError) as excinfo:
        serialize_profile(profile3)
    assert "steps" in str(excinfo.value)


def test_serialize_profile_invalid_steps() -> None:
    profile = {"profile_name": "Test Profile", "hotkey": "ctrl+alt+a", "steps": "not a list"}
    with pytest.raises(ValidationError) as excinfo:
        serialize_profile(profile)
    assert "steps must be a list" in str(excinfo.value)


def test_save_profile_to_file_success(tmp_path: Path) -> None:
    profile = {"profile_name": "My Macro Profile", "hotkey": "f9", "steps": []}
    # Save it
    file_path_str = save_profile_to_file(profile, tmp_path)
    file_path = Path(file_path_str)
    # Check that file exists
    assert file_path.exists()
    assert file_path.name == "My Macro Profile.json"

    # Read back and verify
    with file_path.open() as f:
        data = json.load(f)
    assert data["profile_name"] == "My Macro Profile"


def test_save_profile_to_file_validation_error(tmp_path: Path) -> None:
    profile = {
        "profile_name": "",  # Invalid (must be non-empty)
        "hotkey": "f9",
        "steps": [],
    }
    with pytest.raises(ValidationError):
        save_profile_to_file(profile, tmp_path)

    # Verify no files were created in tmp_path
    assert len(list(tmp_path.iterdir())) == 0


def test_load_profile_from_file_success(tmp_path: Path) -> None:
    profile = {
        "profile_name": "Loaded Profile",
        "hotkey": "f10",
        "steps": [{"type": "keystroke", "keys": ["enter"]}],
    }
    file_path = tmp_path / "Loaded Profile.json"
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(profile, f)

    loaded = load_profile_from_file(file_path)
    assert loaded["profile_name"] == "Loaded Profile"
    assert loaded["hotkey"] == "f10"
    assert len(loaded["steps"]) == 1


def test_load_profile_from_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        load_profile_from_file("non_existent_file.json")


def test_load_profile_from_file_validation_error(tmp_path: Path) -> None:
    # Missing hotkey
    profile = {"profile_name": "Bad Profile", "steps": []}
    file_path = tmp_path / "bad.json"
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(profile, f)

    with pytest.raises(ValidationError):
        load_profile_from_file(file_path)


def test_load_profile_from_file_malformed_json(tmp_path: Path) -> None:
    file_path = tmp_path / "malformed.json"
    with file_path.open("w", encoding="utf-8") as f:
        f.write("{invalid json")

    with pytest.raises(ValidationError):
        load_profile_from_file(file_path)


def test_step_type_enum() -> None:
    import pytest

    from src.utils.config import StepType, serialize_profile

    # Verify Enum values
    assert StepType.TYPE_TEXT == "type_text"
    assert StepType.KEYSTROKE == "keystroke"
    assert StepType.WAIT_FOR_TEXT == "wait_for_text"

    # Verify validation works with Enum or string
    profile_enum = {
        "profile_name": "Test Enum Profile",
        "hotkey": "f1",
        "steps": [{"type": StepType.TYPE_TEXT, "text": "hello"}]
    }
    # Should serialize without error
    assert serialize_profile(profile_enum) is not None

    # Verify invalid step type fails validation
    profile_invalid = {
        "profile_name": "Invalid Type Profile",
        "hotkey": "f1",
        "steps": [{"type": "invalid_type", "text": "hello"}]
    }
    with pytest.raises(ValidationError):
        serialize_profile(profile_invalid)

