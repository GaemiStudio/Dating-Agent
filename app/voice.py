"""
Voice Input and Output

This module handles speaking (text-to-speech) and listening (speech-to-text).
It uses libraries to make the computer talk and understand voice input.
"""

import time
try:
    import speech_recognition as sr  # For listening to voice
    import pyttsx3  # For speaking text
except Exception:
    # If libraries aren't installed, set to None
    sr = None
    pyttsx3 = None

def speak(text: str):
    """Make the computer speak the given text."""
    if pyttsx3 is None:
        # If no voice library, just print the text
        print("[TTS]", text)
        return
    # Set up the speech engine
    engine = pyttsx3.init()
    engine.say(text)  # Say the text
    engine.runAndWait()  # Wait for it to finish speaking

def listen(timeout: int = 5) -> str:
    """Listen to the user speak and return what they said as text."""
    if sr is None:
        raise RuntimeError("speech_recognition not installed")
    # Set up the recognizer
    r = sr.Recognizer()
    with sr.Microphone() as source:  # Use the microphone
        r.adjust_for_ambient_noise(source, duration=0.5)  # Tune for background noise
        print("Listening...")  # Let user know we're listening
        audio = r.listen(source, timeout=timeout)  # Listen for up to timeout seconds
    try:
        # Try to understand the speech using Google's service
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        # If we couldn't understand, return empty string
        return ""
