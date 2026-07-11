"""
IO Handler
All input and output lives here — speaking, listening, and text input.
No decisions, no LLM calls. Just moving words in and out.
"""

import sys
import subprocess
import speech_recognition as sr
from typing import Optional

import config

_recognizer = sr.Recognizer()
_tts_enabled = False  # set to True only when user picks voice mode


def speak(text: str) -> None:
    print(f"\nAgent: {text}")
    if _tts_enabled and sys.platform == "darwin":
        subprocess.run(["say", text])


def get_text_input() -> str:
    print("", flush=True)
    return input("You: ").strip()


def get_voice_input() -> Optional[str]:
    try:
        with sr.Microphone() as source:
            print("\n🎤 Listening... (speak now)")
            _recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = _recognizer.listen(source, timeout=config.VOICE_TIMEOUT)
        text = _recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.RequestError:
        speak("Sorry, I couldn't reach the speech service. Please try again.")
        return None
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that — could you say it again?")
        return None
    except Exception as e:
        print(f"Voice error: {e}")
        return None


def get_input(mode: str) -> Optional[str]:
    if mode == "voice":
        return get_voice_input()
    return get_text_input()


def select_input_mode() -> str:
    global _tts_enabled
    print("\n--- Dating Platform Onboarding ---")
    print("1. Voice Input 🎤")
    print("2. Text Input ⌨️")
    choice = input("Select input mode (1 or 2): ").strip()
    mode = "voice" if choice == "1" else "text"
    _tts_enabled = (mode == "voice")
    return mode
