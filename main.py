"""
Dating Platform Onboarding Agent
Casual coffee date conversation that naturally extracts profile information
"""

import json
import re
import random
import speech_recognition as sr
from typing import Optional
from datetime import datetime
# Using Ollama locally to avoid OpenAI API key requirements during testing
import ollama
import subprocess
from dotenv import load_dotenv

load_dotenv()

import config
from utils import (
    save_json, validate_field, clean_text,
    format_profile_for_display, get_completion_percentage
)

recognizer = sr.Recognizer()


class DatingProfileExtractor:
    """Tracks profile data and conversation history"""

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
            "created_at": datetime.now().isoformat()
        }
        self.conversation_history = []

    def add_to_history(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})

    def save_profile(self, filename: str = None):
        if filename is None:
            filename = config.PROFILE_SAVE_PATH
        save_json(self.profile, filename)
        print(f"Profile saved to {filename}")

    def get_profile_summary(self) -> str:
        return json.dumps(self.profile, indent=2)


class VoiceTextOnboardingAgent:
    """Onboarding agent with a casual coffee date conversation style"""

    REQUIRED_FIELDS = [
        "name", "age", "gender", "interested_in",
        "location", "bio", "interests", "relationship_goals"
    ]

    def __init__(self):
        self.profile = DatingProfileExtractor()
        self.input_mode = None

    def speak(self, text: str):
        print(f"\nAgent: {text}")
        subprocess.run(["say", text])

    def get_voice_input(self) -> Optional[str]:
        try:
            with sr.Microphone() as source:
                print("\n🎤 Listening... (speak now)")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=config.VOICE_TIMEOUT)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.RequestError:
            self.speak("Sorry, I couldn't reach the speech service. Please try again.")
            return None
        except sr.UnknownValueError:
            self.speak("Sorry, I didn't catch that — could you say it again?")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_text_input(self) -> str:
        print("", flush=True)
        return input("You: ").strip()

    def get_input(self) -> Optional[str]:
        if self.input_mode == "voice":
            return self.get_voice_input()
        return self.get_text_input()

    def select_input_mode(self) -> str:
        print("\n--- Dating Platform Onboarding ---")
        print("1. Voice Input 🎤")
        print("2. Text Input ⌨️")
        choice = input("Select input mode (1 or 2): ").strip()
        return "voice" if choice == "1" else "text"

    def extract_fields_from_answer(self, user_input: str, missing_fields: list) -> dict:
        """Scan a free-form answer for any extractable profile fields"""
        if not missing_fields:
            return {}

        prompt = f"""The user said: "{user_input}"

Extract any of these profile fields if they are clearly mentioned or strongly implied:
{', '.join(missing_fields)}

Rules:
- Only include fields you are confident about
- For "age", return just the number as a string
- For "interests", return a comma-separated string
- For "bio", return a short summary of what they said about themselves
- Return a JSON object with only the fields you found
- If nothing is extractable, return {{}}

Return ONLY valid JSON. Example: {{"name": "Alex", "location": "Seattle"}}"""

        response = ollama.chat(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        try:
            content = response["message"]["content"].strip()
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception:
            return {}

    def get_next_message(self, user_input: str, missing_fields: list) -> str:
        """Generate a combined response + next question in one natural message"""
        profile_so_far = {k: v for k, v in self.profile.profile.items()
                          if v and k != "created_at"}
        recent_history = self.profile.conversation_history[-6:]
        random_q = random.choice(config.RANDOM_QUESTIONS)
        missing_str = ', '.join(missing_fields)

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
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"].strip()

    def run_onboarding(self):
        """Main onboarding flow — casual coffee date style"""
        print(f"\n{config.WELCOME_MESSAGE}")
        self.input_mode = self.select_input_mode()

        opening = config.GREETING
        self.speak(opening)
        self.profile.add_to_history("agent", opening)

        max_turns = 20

        for _ in range(max_turns):
            missing = [f for f in self.REQUIRED_FIELDS
                       if not self.profile.profile.get(f)]
            if not missing:
                break

            user_input = self.get_input()
            if not user_input:
                self.speak("Sorry, I didn't catch that — what were you saying?")
                continue

            user_input = clean_text(user_input)
            self.profile.add_to_history("user", user_input)

            # Extract any profile fields from this answer
            extracted = self.extract_fields_from_answer(user_input, missing)
            for field, value in extracted.items():
                if field in self.REQUIRED_FIELDS and not self.profile.profile.get(field):
                    is_valid, _ = validate_field(field, str(value))
                    if is_valid:
                        self.profile.profile[field] = value

            # Re-check missing after extraction
            missing = [f for f in self.REQUIRED_FIELDS
                       if not self.profile.profile.get(f)]
            if not missing:
                break

            next_message = self.get_next_message(user_input, missing)
            self.speak(next_message)
            self.profile.add_to_history("agent", next_message)

        # Wrap up
        self.speak("I think I've got a pretty great picture of you now — let me put your profile together!")
        print(format_profile_for_display(self.profile.profile))

        completion = get_completion_percentage(self.profile.profile)
        print(f"\n✅ Profile Completion: {completion:.1f}%")

        self.profile.save_profile()
        self.speak(config.CLOSING_MESSAGE)


def main():
    try:
        if config.VERBOSE_MODE:
            print("=" * 60)
            print("Dating Platform Onboarding Agent")
            print("=" * 60)

        agent = VoiceTextOnboardingAgent()
        agent.run_onboarding()

        if config.VERBOSE_MODE:
            print("\n✅ Onboarding completed successfully!")
    except KeyboardInterrupt:
        print("\n\n⚠️  Onboarding cancelled. Your profile has been saved.")
    except Exception as e:
        print(f"\n❌ Error during onboarding: {e}")
        if config.VERBOSE_MODE:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
