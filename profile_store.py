"""
Profile Store
Data container for a single onboarding session.
Stores profile fields and conversation history — nothing else.
No LLM calls, no business logic, no I/O.
"""

import json
from datetime import datetime

import config
from utils import save_json


class ProfileStore:
    """Holds all mutable state for one onboarding session."""

    def __init__(self):
        self.profile = {
            "name": None,
            "age": None,
            "gender": None,
            "interested_in": None,
            "location": None,
            "bio": None,
            "interests": None,
            "relationship_goals": None,
            "created_at": datetime.now().isoformat(),
        }
        self.conversation_history = []

    def add_to_history(self, role: str, content: str) -> None:
        self.conversation_history.append({"role": role, "content": content})

    def set_field(self, field: str, value) -> None:
        self.profile[field] = value

    def get_filled(self) -> dict:
        """Return only non-empty profile fields, excluding created_at."""
        return {k: v for k, v in self.profile.items() if v and k != "created_at"}

    def get_missing(self, required_fields: list) -> list:
        """Return required fields that haven't been filled yet."""
        return [f for f in required_fields if not self.profile.get(f)]

    def recent_history(self, n: int = 6) -> list:
        return self.conversation_history[-n:]

    def save(self, path: str = None) -> None:
        target = path or config.PROFILE_SAVE_PATH
        save_json(self.profile, target)
        print(f"Profile saved to {target}")

    def summary(self) -> str:
        return json.dumps(self.profile, indent=2)
