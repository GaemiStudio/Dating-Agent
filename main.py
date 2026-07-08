"""
Dating Platform Onboarding Agent
Uses voice and text input to extract user profile information
"""

import json
import speech_recognition as sr
from typing import Optional
from datetime import datetime
# Using Ollama locally to avoid OpenAI API key requirements during testing
import ollama
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration and utilities
import config
from utils import (
    save_json, validate_field, clean_text,
    format_profile_for_display, get_completion_percentage
)

# Initialize speech recognizer
recognizer = sr.Recognizer()


class DatingProfileExtractor:
    """Extracts and manages dating profile information"""
    
    def __init__(self):
        self.profile = {
            "name": None,
            "age": None,
            "gender": None,
            "interested_in": None,
            "location": None,
            "bio": None,
            "interests": [],
            "relationship_goals": None,
            "created_at": datetime.now().isoformat()
        }
        self.conversation_history = []
    
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})
    
    def save_profile(self, filename: str = None):
        """Save extracted profile to JSON file"""
        if filename is None:
            filename = config.PROFILE_SAVE_PATH
        save_json(self.profile, filename)
        print(f"Profile saved to {filename}")
    
    def get_profile_summary(self) -> str:
        """Return a summary of extracted profile data"""
        return json.dumps(self.profile, indent=2)


class VoiceTextOnboardingAgent:
    """Main onboarding agent with voice and text capabilities"""
    
    def __init__(self):
        self.profile = DatingProfileExtractor()
        self.input_mode = None
    
    def speak(self, text: str):
        """Convert text to speech"""
        print(f"Agent: {text}")
        subprocess.run(["say", text])
    
    def get_voice_input(self) -> Optional[str]:
        """Capture voice input from microphone"""
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
            self.speak("Sorry, I didn't understand that. Could you repeat?")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_text_input(self) -> str:
        """Get text input from user"""
        print("", flush=True)
        return input("You: ").strip()
    
    def select_input_mode(self) -> str:
        """Let user choose between voice and text"""
        print("\n--- Dating Platform Onboarding ---")
        print("1. Voice Input 🎤")
        print("2. Text Input ⌨️")
        choice = input("Select input mode (1 or 2): ").strip()
        return "voice" if choice == "1" else "text"
    
    def run_onboarding(self):
        """Main onboarding flow"""
        print(f"\n{config.WELCOME_MESSAGE}")
        self.input_mode = self.select_input_mode()
        
        # Initial greeting
        greeting = config.GREETING
        self.speak(greeting)
        self.profile.add_to_history("agent", greeting)
        
        # Onboarding questions from config
        for field, question in config.PROFILE_FIELDS:
            self.speak(question)
            self.profile.add_to_history("agent", question)
            
            # Get user input
            if self.input_mode == "voice":
                user_input = self.get_voice_input()
            else:
                user_input = self.get_text_input()
            
            if user_input:
                user_input = clean_text(user_input)
                self.profile.add_to_history("user", user_input)
                
                # Extract and validate information
                extracted = self.extract_field(field, user_input)
                is_valid, message = validate_field(field, extracted)
                
                if is_valid:
                    self.profile.profile[field] = extracted
                    confirmation = self.generate_response(field, extracted)
                else:
                    confirmation = f"I need you to be more specific about {field}. {message}"
                
                self.speak(confirmation)
                self.profile.add_to_history("agent", confirmation)
            else:
                retry = "Let me ask again."
                self.speak(retry)
        
        # Profile summary
        summary = "Great! Let me summarize your profile."
        self.speak(summary)
        print(format_profile_for_display(self.profile.profile))
        
        # Display completion percentage
        completion = get_completion_percentage(self.profile.profile)
        print(f"\n✅ Profile Completion: {completion:.1f}%")
        
        # Save profile
        self.profile.save_profile()
        
        closing = config.CLOSING_MESSAGE
        self.speak(closing)
    
    def generate_response(self, field: str, value: str) -> str:
        """Generate a warm, contextual response to the user's answer"""
        filled = {k: v for k, v in self.profile.profile.items()
                  if v and k != "created_at"}
        context = (f"What you know about them so far: {json.dumps(filled)}"
                   if filled else "This is the first thing they've shared.")

        prompt = f"""You are a warm, friendly dating app onboarding assistant having a natural conversation.
{context}
The user just shared their {field}: "{value}"

Write a genuine, personal response (1-2 sentences) that:
- Comments warmly on what they shared, referencing the actual content
- Feels natural and human, not scripted
- Adapts your tone based on what you already know about them
Do NOT ask another question. Just respond to what they said."""

        response = ollama.chat(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"].strip()

    def extract_field(self, field: str, user_input: str) -> str:
        """Extract field using LLM"""
        prompt = f"""Extract the {field} from this user input.
Return ONLY the extracted value as a string, nothing else.
User input: {user_input}"""
        response = ollama.chat(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"].strip()


def main():
    """Main entry point"""
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
