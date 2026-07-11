"""
Conversation Director skill
Decides what the agent says next.
Receives all context it needs as arguments — no hidden state, no side effects.
"""

import json
import random

import config
from llm import chat


def get_next_message(
    user_input: str,
    missing_fields: list,
    profile_so_far: dict,
    recent_history: list,
) -> str:
    """
    Generate a warm response to user_input that also nudges toward
    one of the missing profile fields — without making it feel like a form.
    """
    random_q = random.choice(config.RANDOM_QUESTIONS)
    missing_str = ", ".join(missing_fields)

    prompt = f"""{config.AGENT_PERSONA}

Already collected — do NOT ask about any of these again:
{json.dumps(profile_so_far)}

Still need (ask about these in order of priority):
{missing_str}

Recent conversation:
{json.dumps(recent_history)}

They just said: "{user_input}"

Write your reply. Rules:
- Max 2 sentences total
- One brief, genuine reaction to what they said (don't over-explain or keep asking about the same topic)
- Then ask EXACTLY ONE question — about the first thing in the "still need" list above, woven in naturally
- Only swap that for the fun question below if fewer than 3 fields remain: "{random_q}"
- Never ask two questions in one message
- Never ask about something already in "already collected"
- Sound like a real person, not a checklist"""

    return chat(prompt)
