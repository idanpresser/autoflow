import json
from enum import Enum
from pathlib import Path
from typing import Any, cast


class ValidationError(Exception):
    pass


class StepType(str, Enum):
    TYPE_TEXT = "type_text"
    KEYSTROKE = "keystroke"
    WAIT_FOR_TEXT = "wait_for_text"


def serialize_profile(profile_dict: dict[str, Any]) -> str:
    """
    Serializes a profile dictionary into a JSON string,
    raising ValidationError if required fields are missing or malformed.
    """
    if not isinstance(profile_dict, dict):
        raise ValidationError("Profile must be a dictionary")

    if "profile_name" not in profile_dict:
        raise ValidationError("Missing required field: profile_name")
    if (
        not isinstance(profile_dict["profile_name"], str)
        or not profile_dict["profile_name"].strip()
    ):
        raise ValidationError("profile_name must be a non-empty string")

    if "hotkey" not in profile_dict:
        raise ValidationError("Missing required field: hotkey")
    if not isinstance(profile_dict["hotkey"], str):
        raise ValidationError("hotkey must be a string")

    if "steps" not in profile_dict:
        raise ValidationError("Missing required field: steps")
    if not isinstance(profile_dict["steps"], list):
        raise ValidationError("steps must be a list")

    for idx, step in enumerate(profile_dict["steps"]):
        if not isinstance(step, dict):
            raise ValidationError(f"Step at index {idx} must be a dictionary")
        if "type" not in step:
            raise ValidationError(f"Step at index {idx} is missing required field: type")
        
        step_type = step["type"]
        try:
            StepType(step_type)
        except ValueError:
            valid_types = [t.value for t in StepType]
            raise ValidationError(
                f"Step at index {idx} has invalid type: '{step_type}'. "
                f"Must be one of {valid_types}"
            ) from None

    try:
        return json.dumps(profile_dict, indent=2)
    except Exception as e:
        raise ValidationError(f"JSON serialization failed: {e}") from e


def save_profile_to_file(
    profile_dict: dict[str, Any], folder_path: str | Path
) -> str:
    """
    Validates, serializes, and saves the profile to a file named
    '{profile_name}.json' inside folder_path. Returns the path of the saved file.
    """
    serialized = serialize_profile(profile_dict)

    folder = Path(folder_path)
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{profile_dict['profile_name']}.json"
    file_path = folder / filename

    try:
        with file_path.open("w", encoding="utf-8") as f:
            f.write(serialized)
        return str(file_path)
    except Exception as e:
        raise OSError(f"Failed to write profile to file: {e}") from e


def load_profile_from_file(file_path: str | Path) -> dict[str, Any]:
    """
    Loads and validates a profile from the specified JSON file path.
    Raises FileNotFoundError if the file is missing, and ValidationError
    if the JSON is malformed or missing required keys.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Profile file not found: {file_path}")

    try:
        with path.open(encoding="utf-8") as f:
            profile_dict = cast(dict[str, Any], json.load(f))
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON format: {e}") from e
    except Exception as e:
        raise OSError(f"Failed to read file: {e}") from e

    # Run serialization validation (will raise ValidationError if validation fails)
    serialize_profile(profile_dict)

    return profile_dict
