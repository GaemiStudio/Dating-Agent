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

    prompt = f"""Write a 2-sentence personality vibe for someone's dating profile. Short, grounded, warm — not poetic or romantic.

Sentence 1: Capture their energy using one sensory detail — a color, season, time of day, or texture. Keep it specific to who they actually are.
Sentence 2: One honest observation about what kind of person might complement them well.

No metaphors. No flowery language. No paragraphs. Just two clear, warm sentences.

Profile:
{json.dumps(clean_profile, indent=2)}"""

    return chat(prompt, stream=stream)
