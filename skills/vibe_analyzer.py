"""
Vibe Analyzer skill
Reads a completed dating profile and returns a sensory, poetic personality summary.
"""

import json

import config
from llm import chat


def analyze_vibe(profile: dict, stream: bool = False) -> str:
    """
    Given a dating profile, returns a short personality vibe summary written
    in sensory imagery — colors, seasons, time of day, sounds — plus one note
    on what contrasting element might complement them.
    """
    # Strip internal fields before sending to LLM
    clean_profile = {k: v for k, v in profile.items()
                     if v and k != "created_at"}

    prompt = f"""Write a personality vibe for someone's dating profile. Two sentences only — no labels, no headers, no "Sentence 1/2".

Capture their energy using one sensory detail (color, season, time of day, or texture) tied to who they actually are. Then one honest observation about what kind of person might complement them well.

Keep it short, warm, and grounded. No flowery language.

Profile:
{json.dumps(clean_profile, indent=2)}"""

    return chat(prompt, stream=stream)
