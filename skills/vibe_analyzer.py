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

    prompt = f"""You are writing a quiet, warm personality vibe for someone's dating profile.

Based on the profile below, write a 3-4 sentence description of this person's energy and vibe.
Weave in the following naturally — don't list them as separate items, just let them flow:
- A color or palette that feels like them
- A season
- A time of day
- A sound or texture

Then close with one gentle, surprising observation about what very different kind of person or energy might actually complement them well.

Write in a quiet, warm tone — like a thoughtful friend describing someone they genuinely admire.
No bullet points. No headers. Just the description.

Profile:
{json.dumps(clean_profile, indent=2)}"""

    return chat(prompt, stream=stream)
