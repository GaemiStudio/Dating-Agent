"""
Dating Platform Onboarding Agent
Uses voice and text input to extract user profile information
"""

import json
import speech_recognition as sr
from typing import Optional
from datetime import datetime
# Using Ollama locally to avoid OpenAI API key requirements during testing
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from langchain.agents import create_agent
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration and utilities
import config
from utils import (
    save_json, load_json, validate_field, clean_text,
    format_profile_for_display, get_completion_percentage
)

# Initialize LLM
llm = ChatOllama(
    model=config.LLM_MODEL,
    temperature=config.LLM_TEMPERATURE,
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
        self.setup_agent()
    
    def setup_agent(self):
        """Initialize LangChain agent with tools"""
        
        @tool
        def extract_user_info(user_input: str, field: str) -> str:
            """Extract specific user information from input"""
            extraction_prompt = PromptTemplate(
                input_variables=["user_input", "field"],
                template="""Extract the {field} from the following user input.
                Return ONLY the extracted value, nothing else.
                User input: {user_input}
                Extracted {field}:"""
            )
            chain = extraction_prompt | llm | StrOutputParser()
            return chain.invoke({"user_input": user_input, "field": field}).strip()

        @tool
        def validate_profile_data(field: str, value: str) -> dict:
            """Validate extracted profile data"""
            validation_prompt = PromptTemplate(
                input_variables=["field", "value"],
                template="""Validate the following dating profile field value.
                Field: {field}
                Value: {value}
                Return a JSON response with 'valid' (true/false) and 'message' keys."""
            )
            chain = validation_prompt | llm | StrOutputParser()
            result = chain.invoke({"field": field, "value": value})
            try:
                return json.loads(result)
            except:
                return {"valid": True, "message": "Accepted"}

        @tool
        def generate_next_question(current_fields_filled: str) -> str:
            """Generate the next question based on what's been filled"""
            question_prompt = PromptTemplate(
                input_variables=["filled_fields"],
                template="""You are an onboarding agent for a dating platform.
                These fields have been filled already: {filled_fields}
                Generate a friendly, engaging next question to ask the user.
                Ask about profile completion or interests.
                Keep it conversational and warm."""
            )
            chain = question_prompt | llm | StrOutputParser()
            return chain.invoke({"filled_fields": current_fields_filled}).strip()

        tools = [extract_user_info, validate_profile_data, generate_next_question]

        self.agent = create_agent(llm, tools)
    
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
                    confirmation = f"Got it! I've noted that for {field}."
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
    
    def extract_field(self, field: str, user_input: str) -> str:
        """Extract field using LLM"""
        extraction_prompt = PromptTemplate(
            input_variables=["field", "user_input"],
            template="""Extract the {field} from this user input.
            Return ONLY the extracted value as a string, nothing else.
            User input: {user_input}"""
        )
        chain = extraction_prompt | llm | StrOutputParser()
        return chain.invoke({"field": field, "user_input": user_input}).strip()


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
