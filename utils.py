"""
Utility functions for the Dating Onboarding Agent
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from config import MIN_NAME_LENGTH, MAX_NAME_LENGTH, MIN_AGE, MAX_AGE, MIN_BIO_LENGTH


def save_json(data: Dict[str, Any], filepath: str) -> bool:
    """
    Save data to JSON file
    
    Args:
        data: Dictionary to save
        filepath: Path to save file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving to {filepath}: {e}")
        return False


def load_json(filepath: str) -> Optional[Dict]:
    """
    Load data from JSON file
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        Loaded dictionary or None if file not found
    """
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    return None


def validate_name(name: str) -> tuple[bool, str]:
    """
    Validate user name
    
    Args:
        name: Name to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not name or not isinstance(name, str):
        return False, "Name must be a non-empty string"
    
    name = name.strip()
    if len(name) < MIN_NAME_LENGTH:
        return False, f"Name must be at least {MIN_NAME_LENGTH} characters"
    if len(name) > MAX_NAME_LENGTH:
        return False, f"Name must be less than {MAX_NAME_LENGTH} characters"
    
    return True, "Name is valid"


def validate_age(age: Any) -> tuple[bool, str]:
    """
    Validate user age
    
    Args:
        age: Age to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    try:
        age_int = int(age)
        if age_int < MIN_AGE:
            return False, f"You must be at least {MIN_AGE} years old"
        if age_int > MAX_AGE:
            return False, f"Age seems unrealistic (max {MAX_AGE})"
        return True, "Age is valid"
    except (ValueError, TypeError):
        return False, "Age must be a number"


def validate_bio(bio: str) -> tuple[bool, str]:
    """
    Validate user bio
    
    Args:
        bio: Bio text to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not bio or not isinstance(bio, str):
        return False, "Bio must be a non-empty string"
    
    bio = bio.strip()
    if len(bio) < MIN_BIO_LENGTH:
        return False, f"Bio must be at least {MIN_BIO_LENGTH} characters"
    
    return True, "Bio is valid"


_GENDER_KEYWORDS = {
    "men", "women", "male", "female", "everyone", "anyone",
    "non-binary", "all", "open", "both", "any", "man", "woman",
    "guy", "girl", "fem", "masc",
}


def validate_interested_in(value: str) -> tuple[bool, str]:
    if not value or not isinstance(value, str):
        return False, "interested_in must be a non-empty string"
    if any(kw in value.lower() for kw in _GENDER_KEYWORDS):
        return True, "interested_in is valid"
    return False, "interested_in should be a gender (e.g. 'women', 'men', 'everyone')"


def validate_field(field: str, value: Any) -> tuple[bool, str]:
    """
    General field validation dispatcher
    
    Args:
        field: Field name
        value: Field value
    
    Returns:
        Tuple of (is_valid, message)
    """
    validators = {
        "name": validate_name,
        "age": validate_age,
        "bio": validate_bio,
        "interested_in": validate_interested_in,
    }
    
    if field in validators:
        return validators[field](value)
    
    # Default validation - just check it's not empty
    if value and str(value).strip():
        return True, f"{field} is valid"
    return False, f"{field} cannot be empty"


def clean_text(text: str) -> str:
    """
    Clean and normalize text input
    
    Args:
        text: Text to clean
    
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    return " ".join(text.strip().split())


def format_profile_for_display(profile: Dict[str, Any]) -> str:
    """
    Format profile data for display
    
    Args:
        profile: Profile dictionary
    
    Returns:
        Formatted string
    """
    output = "\n📋 Your Profile:\n"
    output += "=" * 50 + "\n"
    
    for key, value in profile.items():
        if key != "created_at" and value:
            formatted_key = key.replace("_", " ").title()
            output += f"{formatted_key}: {value}\n"
    
    if profile.get("created_at"):
        output += f"Created: {profile['created_at']}\n"
    
    output += "=" * 50
    return output


def get_completion_percentage(profile: Dict[str, Any]) -> float:
    """
    Calculate profile completion percentage
    
    Args:
        profile: Profile dictionary
    
    Returns:
        Completion percentage (0-100)
    """
    total_fields = len([k for k in profile.keys() if k != "created_at"])
    filled_fields = len([v for k, v in profile.items() if k != "created_at" and v and str(v).strip()])
    
    if total_fields == 0:
        return 0.0
    
    return (filled_fields / total_fields) * 100


def create_backup(filepath: str) -> bool:
    """
    Create backup of existing file
    
    Args:
        filepath: Path to file to backup
    
    Returns:
        True if backup created, False otherwise
    """
    if not os.path.exists(filepath):
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}.backup_{timestamp}"
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        with open(backup_path, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False
