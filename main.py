"""
Dating Platform Onboarding Agent — Orchestrator
Coordinates the conversation flow. Delegates everything:
  - I/O      → io_handler
  - Data     → ProfileStore
  - LLM work → skills/field_extractor, skills/conversation_director
  - End tasks → skills/vibe_analyzer, skills/match_estimator
"""

import logging
from dotenv import load_dotenv
load_dotenv()

import config

logging.basicConfig(
    level=logging.DEBUG if config.VERBOSE_MODE else logging.WARNING,
    format="[%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

from io_handler import speak, speak_streamed, get_input, select_input_mode
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
        Each turn: get input → extract fields → stream response.
        """
        for turn in range(config.MAX_TURNS):
            user_input = get_input(self.input_mode)
            if not user_input:
                speak("Sorry, I didn't catch that — what were you saying?")
                continue

            user_input = clean_text(user_input)
            self.store.add_to_history("user", user_input)

            missing = self.store.get_missing(REQUIRED_FIELDS)
            logger.debug(f"Turn {turn + 1} | Missing: {missing}")

            # --- Field extraction (deterministic rules + LLM fallback) ---
            extracted = extract_fields(user_input, missing)
            for field, value in extracted.items():
                if field in REQUIRED_FIELDS and not self.store.profile.get(field):
                    # Normalize list values (LLM sometimes returns arrays)
                    if isinstance(value, list):
                        value = ", ".join(str(v) for v in value)
                    is_valid, _ = validate_field(field, str(value))
                    if is_valid:
                        self.store.set_field(field, value)
                        logger.debug(f"Extracted {field}: {value}")

            missing = self.store.get_missing(REQUIRED_FIELDS)

            if not missing and turn >= config.MIN_TURNS:
                # All fields collected — acknowledge the user's last message
                # naturally before handing off to _wrap_up
                print("\nAgent: ", end="", flush=True)
                closing = get_next_message(
                    user_input=user_input,
                    missing_fields=[],
                    profile_so_far=self.store.get_filled(),
                    recent_history=self.store.recent_history(),
                    wrap_up=True,
                    stream=True,
                )
                speak_streamed(closing)
                self.store.add_to_history("agent", closing)
                break

            # --- Stream the next agent message ---
            print("\nAgent: ", end="", flush=True)
            next_message = get_next_message(
                user_input=user_input,
                missing_fields=missing,
                profile_so_far=self.store.get_filled(),
                recent_history=self.store.recent_history(),
                stream=True,
            )
            speak_streamed(next_message)
            self.store.add_to_history("agent", next_message)

    def _wrap_up(self) -> None:
        """Display the completed profile, run skills, save."""
        speak("I think I've got a pretty great picture of you now — let me put your profile together!")

        print(format_profile_for_display(self.store.profile))
        completion = get_completion_percentage(self.store.profile)
        print(f"\n✅ Profile Completion: {completion:.1f}%")

        # --- Vibe Analyzer (streamed) ---
        print("\n✨ Your Vibe\n" + "-" * 40)
        print("Agent: ", end="", flush=True)
        vibe = analyze_vibe(self.store.profile, stream=True)
        speak_streamed(vibe)

        # --- Match Estimator (deterministic output, no streaming needed) ---
        print("\n💫 Your Match Estimate\n" + "-" * 40)
        match_result = estimate_matches(self.store.profile)
        match_summary = (
            f"Based on our current community, you'd potentially match with around "
            f"{match_result['percentage']}% of people. "
            f"{match_result['interpretation']}"
        )
        speak(match_summary)

        self.store.save()
        speak(config.CLOSING_MESSAGE)

    def run(self) -> None:
        self._setup()
        self._conversation_loop()
        self._wrap_up()


def _check_ollama() -> None:
    """Fail fast with a helpful message if Ollama isn't running."""
    if config.LLM_PROVIDER != "ollama":
        return
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
        logger.info("Onboarding completed successfully.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Onboarding cancelled.")
    except SystemExit:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if config.VERBOSE_MODE:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
