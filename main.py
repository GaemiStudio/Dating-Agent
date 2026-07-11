"""
Dating Platform Onboarding Agent — Orchestrator
Coordinates the conversation flow. Delegates everything:
  - I/O      → io_handler
  - Data     → ProfileStore
  - LLM work → skills/field_extractor, skills/conversation_director
  - End tasks → skills/vibe_analyzer, skills/match_estimator
"""

from dotenv import load_dotenv
load_dotenv()

import config
from io_handler import speak, get_input, select_input_mode
from profile_store import ProfileStore
from skills.field_extractor import extract_fields
from skills.conversation_director import get_next_message
from skills.vibe_analyzer import analyze_vibe
from skills.match_estimator import estimate_matches
from utils import validate_field, clean_text, format_profile_for_display, get_completion_percentage

REQUIRED_FIELDS = [
    "name", "age", "gender", "interested_in",
    "location", "bio", "interests", "relationship_goals",
]


class OnboardingAgent:
    """
    Thin orchestrator for the onboarding session.
    All I/O, data storage, and LLM work is delegated to dedicated modules.
    """

    def __init__(self):
        self.store = ProfileStore()
        self.input_mode = None

    def _setup(self) -> None:
        """Print welcome, pick input mode, deliver the opening line."""
        print(f"\n{config.WELCOME_MESSAGE}")
        self.input_mode = select_input_mode()
        speak(config.GREETING)
        self.store.add_to_history("agent", config.GREETING)

    def _conversation_loop(self) -> None:
        """
        Run until all required fields are filled or the turn limit is hit.
        Each turn: get input → extract fields → respond.
        """
        for turn in range(config.MAX_TURNS):
            missing = self.store.get_missing(REQUIRED_FIELDS)
            if not missing:
                break

            user_input = get_input(self.input_mode)
            if not user_input:
                speak("Sorry, I didn't catch that — what were you saying?")
                continue

            user_input = clean_text(user_input)
            self.store.add_to_history("user", user_input)

            if config.VERBOSE_MODE:
                print(f"\n[Turn {turn + 1} | Missing: {missing}]")

            # --- Field extraction (deterministic rules + LLM fallback) ---
            extracted = extract_fields(user_input, missing)
            for field, value in extracted.items():
                if field in REQUIRED_FIELDS and not self.store.profile.get(field):
                    is_valid, _ = validate_field(field, str(value))
                    if is_valid:
                        self.store.set_field(field, value)
                        if config.VERBOSE_MODE:
                            print(f"  ✓ {field}: {value}")

            missing = self.store.get_missing(REQUIRED_FIELDS)
            if not missing:
                break

            # --- Generate and deliver the next message ---
            next_message = get_next_message(
                user_input=user_input,
                missing_fields=missing,
                profile_so_far=self.store.get_filled(),
                recent_history=self.store.recent_history(),
            )
            speak(next_message)
            self.store.add_to_history("agent", next_message)

    def _wrap_up(self) -> None:
        """Display the completed profile, run skills, save."""
        speak("I think I've got a pretty great picture of you now — let me put your profile together!")

        print(format_profile_for_display(self.store.profile))
        completion = get_completion_percentage(self.store.profile)
        print(f"\n✅ Profile Completion: {completion:.1f}%")

        print("\n✨ Your Vibe\n" + "-" * 40)
        vibe = analyze_vibe(self.store.profile)
        print(vibe)
        speak(vibe)

        print("\n💫 Your Match Estimate\n" + "-" * 40)
        match_result = estimate_matches(self.store.profile)
        match_summary = (
            f"Based on our current community, you'd potentially match with around "
            f"{match_result['percentage']}% of people. "
            f"{match_result['interpretation']}"
        )
        print(match_summary)
        speak(match_summary)

        self.store.save()
        speak(config.CLOSING_MESSAGE)

    def run(self) -> None:
        self._setup()
        self._conversation_loop()
        self._wrap_up()


def _check_ollama() -> None:
    """Fail fast with a helpful message if Ollama isn't running."""
    import urllib.request
    try:
        urllib.request.urlopen("http://localhost:11434", timeout=3)
    except Exception:
        print("\n❌ Ollama is not reachable at http://localhost:11434")
        print("   Start it with: ollama serve")
        raise SystemExit(1)


def main():
    try:
        _check_ollama()

        if config.VERBOSE_MODE:
            print("=" * 60)
            print("Dating Platform Onboarding Agent")
            print("=" * 60)

        OnboardingAgent().run()

        if config.VERBOSE_MODE:
            print("\n✅ Onboarding completed successfully!")
    except KeyboardInterrupt:
        print("\n\n⚠️  Onboarding cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if config.VERBOSE_MODE:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
