"""
Match Estimator skill
Estimates what percentage of the user base a new profile might match with.
Uses hard rules first (no LLM), then one batched LLM call for soft scoring.
"""

import json
import re
import os

import config
from llm import chat

# Path to the sample profile database
PROFILES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_profiles.json")

# Profiles scoring 6+ out of 10 count as a soft match
SOFT_MATCH_THRESHOLD = 6

# Age gap larger than this is filtered out
MAX_AGE_GAP = 8

# Goal keywords that are mutually incompatible
INCOMPATIBLE_GOAL_PAIRS = [
    ("long-term", "casual"),
    ("marriage", "casual"),
    ("long-term", "hookup"),
    ("marriage", "hookup"),
]

# Keywords that mean "open to everyone"
OPEN_KEYWORDS = {"everyone", "anyone", "all", "open", "any", "non-binary"}


def _normalize(text: str) -> str:
    return text.lower().strip()


def _interested_in_gender(interested_in: str, gender: str) -> bool:
    """Check if 'interested_in' includes the given gender."""
    i = _normalize(interested_in)
    g = _normalize(gender)

    # Open to everyone
    if any(k in i for k in OPEN_KEYWORDS):
        return True

    # Direct keyword match
    if g in i:
        return True

    # Common synonyms
    if g in ("female", "woman", "girl") and any(k in i for k in ("wom", "fem", "girl", "lady")):
        return True
    if g in ("male", "man", "guy") and any(k in i for k in ("men", "man", "male", "guy")):
        return True

    return False


def _gender_compatible(a: dict, b: dict) -> bool:
    """Return True if A is interested in B's gender AND B is interested in A's gender."""
    return (
        _interested_in_gender(a.get("interested_in", ""), b.get("gender", ""))
        and _interested_in_gender(b.get("interested_in", ""), a.get("gender", ""))
    )


def _age_compatible(a: dict, b: dict) -> bool:
    try:
        return abs(int(a.get("age", 0)) - int(b.get("age", 0))) <= MAX_AGE_GAP
    except (ValueError, TypeError):
        return True


def _goals_compatible(a: dict, b: dict) -> bool:
    goal_a = _normalize(a.get("relationship_goals", ""))
    goal_b = _normalize(b.get("relationship_goals", ""))
    for pair in INCOMPATIBLE_GOAL_PAIRS:
        if pair[0] in goal_a and pair[1] in goal_b:
            return False
        if pair[1] in goal_a and pair[0] in goal_b:
            return False
    return True


def _soft_score(new_profile: dict, candidates: list) -> list:
    """
    One batched LLM call to score lifestyle/personality compatibility
    for all candidates that passed hard filters.
    Returns a list of scores (0-10) in the same order as candidates.
    """
    clean_new = {k: v for k, v in new_profile.items() if v and k != "created_at"}
    candidates_text = json.dumps(
        [{"id": i, "interests": p.get("interests", ""), "bio": p.get("bio", ""),
          "relationship_goals": p.get("relationship_goals", "")}
         for i, p in enumerate(candidates)],
        indent=2
    )

    prompt = f"""Score lifestyle and personality compatibility between this person and each candidate.

New profile:
Interests: {clean_new.get("interests", "")}
Bio: {clean_new.get("bio", "")}
Relationship goals: {clean_new.get("relationship_goals", "")}

Candidates:
{candidates_text}

For each candidate score compatibility 0-10 based on shared or complementary interests, lifestyle, and energy.
Return ONLY a JSON array of integer scores in order. Example: [7, 4, 9, 3]"""

    try:
        content = chat(prompt)
        bracket_match = re.search(r'\[([^\]]+)\]', content, re.DOTALL)
        if bracket_match:
            # Strip inline comments before extracting numbers
            inner = re.sub(r'//[^\n]*', '', bracket_match.group(1))
            scores = [int(n) for n in re.findall(r'\b\d+\b', inner)]
            if len(scores) == len(candidates):
                return scores
    except Exception:
        pass
    return [5] * len(candidates)


def _interpret(percentage: float) -> str:
    """Deterministic warm reframing of the match percentage — no LLM needed."""
    if percentage < 10:
        return (
            "You're genuinely one of a kind. Fewer people will match your energy, "
            "but the ones who do will feel like they found exactly what they were looking for."
        )
    elif percentage < 25:
        return (
            "Your vibe is distinctive and specific — that's a good thing. "
            "You'll connect deeply with a select group who really gets you."
        )
    elif percentage < 50:
        return (
            "You have a nice balance of depth and approachability. "
            "There's a solid group of people out there who would genuinely enjoy getting to know you."
        )
    elif percentage < 70:
        return (
            "You have a warm, open energy that a lot of people would feel comfortable around. "
            "You'll have plenty of good options."
        )
    else:
        return (
            "You're naturally easy to connect with — most people would enjoy your company. "
            "The challenge might be narrowing it down to the ones who really light you up."
        )


def estimate_matches(new_profile: dict) -> dict:
    """
    Main entry point. Returns a dict with:
      - percentage: estimated match rate across the sample pool
      - hard_filter_passed: how many passed gender/age/goals checks
      - soft_matches: how many passed the LLM compatibility score
      - total_profiles: size of the sample pool
      - interpretation: a warm, deterministic reframing of the number
    """
    with open(PROFILES_PATH) as f:
        sample_profiles = json.load(f)

    total = len(sample_profiles)

    # Step 1 — hard filters (pure logic)
    candidates = [
        p for p in sample_profiles
        if _gender_compatible(new_profile, p)
        and _age_compatible(new_profile, p)
        and _goals_compatible(new_profile, p)
    ]

    # Step 2 — soft scoring (one LLM call for all candidates)
    if candidates:
        scores = _soft_score(new_profile, candidates)
        soft_matches = sum(1 for s in scores if s >= SOFT_MATCH_THRESHOLD)
    else:
        soft_matches = 0

    percentage = round((soft_matches / total) * 100, 1)

    return {
        "percentage": percentage,
        "total_profiles": total,
        "hard_filter_passed": len(candidates),
        "soft_matches": soft_matches,
        "interpretation": _interpret(percentage),
    }
