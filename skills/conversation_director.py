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
    wrap_up: bool = False,
    stream: bool = False,
) -> str:
    """
    Generate a warm response to user_input that also nudges toward
    one of the missing profile fields — without making it feel like a form.
    When wrap_up=True, produce a natural closing line with no questions.
    """
    rules_block = "\n".join(f"{i+1}. {r}" for i, r in enumerate(config.AGENT_RULES))

    if wrap_up:
        prompt = f"""{config.AGENT_PERSONA}

Core rules you must follow:
{rules_block}

You're finishing a casual onboarding chat on a dating app. The user just said: "{user_input}"

Recent conversation:
{json.dumps(recent_history[-4:], indent=2)}

Write a single warm closing response (1-2 sentences max). Acknowledge what they said naturally and make it feel like a genuine, friendly sign-off. Do NOT ask any questions — the chat is over."""
        return chat(prompt, stream=stream)

    random_q = random.choice(config.RANDOM_QUESTIONS)
    missing_str = ", ".join(missing_fields)

    prompt = f"""{config.AGENT_PERSONA}

Core rules you must follow:
{rules_block}

Already collected — do NOT ask about any of these again:
{json.dumps(profile_so_far)}

Still need (ask about these in order of priority):
{missing_str}

Recent conversation:
{json.dumps(recent_history)}

They just said: "{user_input}"

Write your reply:
- One brief, genuine reaction to what they said
- Then ask EXACTLY ONE question about the first item in the "still need" list, woven in naturally
- Only swap that for this fun question if fewer than 3 fields remain: "{random_q}" """

    return chat(prompt, stream=stream)
