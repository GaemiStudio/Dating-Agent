"""
Conversation Director skill
Decides what the agent says next.
Receives all context it needs as arguments — no hidden state, no side effects.
"""

import json
import random
import ollama

import config


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

What you know about them so far: {json.dumps(profile_so_far)}
Still need to find out: {missing_str}
Recent conversation: {json.dumps(recent_history)}
They just said: "{user_input}"

Write your next message (2-3 sentences max):
1. Respond warmly to what they said — be genuine, reference the actual content
2. Then either:
   - Ask a natural follow-up if their answer opened something interesting
   - OR casually bring one of the missing fields into the conversation (don't make it feel like a form)
   - OR if the moment feels right, throw in this fun one: "{random_q}"
Sound like a real person on a coffee date, not a chatbot running through a checklist."""

    response = ollama.chat(
        model=config.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"].strip()
