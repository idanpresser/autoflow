import json

class ValidationError(Exception):
    pass

def serialize_profile(profile_dict):
    """
    Serializes a profile dictionary into a JSON string,
    raising ValidationError if required fields are missing or malformed.
    """
    if not isinstance(profile_dict, dict):
        raise ValidationError("Profile must be a dictionary")
        
    if "profile_name" not in profile_dict:
        raise ValidationError("Missing required field: profile_name")
    if not isinstance(profile_dict["profile_name"], str) or not profile_dict["profile_name"].strip():
        raise ValidationError("profile_name must be a non-empty string")
        
    if "hotkey" not in profile_dict:
        raise ValidationError("Missing required field: hotkey")
    if not isinstance(profile_dict["hotkey"], str):
        raise ValidationError("hotkey must be a string")
        
    if "steps" not in profile_dict:
        raise ValidationError("Missing required field: steps")
    if not isinstance(profile_dict["steps"], list):
        raise ValidationError("steps must be a list")
        
    try:
        return json.dumps(profile_dict, indent=2)
    except Exception as e:
        raise ValidationError(f"JSON serialization failed: {e}")
