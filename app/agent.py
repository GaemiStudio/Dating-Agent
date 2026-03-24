"""
AI Agent for Onboarding

This module contains the OnboardingAgent class, which uses AI (via Ollama and LangChain)
to extract user profile information from conversations. It also uses vector memory
to remember past answers for better context.
"""

import os
from typing import Optional
from pydantic import BaseModel, ValidationError

# Ollama client support for langchain >=0.0.260 and langchain_ollama package
try:
    from langchain.llms import Ollama
except Exception:
    try:
        from langchain_ollama import Ollama
    except Exception:
        from langchain_ollama import OllamaLLM as Ollama

# from .vector_store import retrieve_memory

# Where to find the Ollama server
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Define what profile information we want to extract
class OnboardSchema(BaseModel):
    name: Optional[str]
    age: Optional[int]
    location: Optional[str]
    gender: Optional[str]
    personality: Optional[str]
    looking_for: Optional[str]
    days_available: Optional[str]
    age_range: Optional[str]
    professions: Optional[str]
    favorite_foods: Optional[str]
    pets: Optional[str]

class OnboardingAgent:
    def __init__(self, model: str = "llama2"):
        # Connect to the AI model
        self.llm = Ollama(model=model, base_url=OLLAMA_HOST)

    def extract_all(self, free_text: str, session_id: str = None) -> OnboardSchema:
        # If we have a session ID, get relevant past memories
        memory_context = ""
        # Temporarily disable memory due to HF loading issues
        # if session_id:
        #     memories = retrieve_memory(session_id, free_text, k=2)
        #     if memories:
        #         memory_context = "Previous context from this session:\n" + "\n".join(memories) + "\n\n"

        # Create a prompt for the AI to extract profile info
        prompt = (
            f"{memory_context}You are a friendly but professional dating platform onboarding assistant. "
            "You are an excellent listener who pays close attention to what users say, "
            "but you also cut through unnecessary words to understand the core meaning and context. "
            "Be warm and approachable, but maintain a professional tone suitable for a dating app. "
            "Your goal is to extract user profile data from conversational text. "
            "Return a JSON object with keys: name, age, location, gender, personality, looking_for, "
            "days_available, age_range, professions, favorite_foods, pets. If a field is not present, use null.\n"
            f"Text: '''{free_text}'''\n\nReturn only JSON."
        )
        # Ask the AI for the answer
        resp = self.llm.invoke(prompt)
        text = resp if isinstance(resp, str) else str(resp)
        # Default data
        default = {
            'name': None, 'age': None, 'location': None, 'gender': None, 'personality': None,
            'looking_for': None, 'days_available': None, 'age_range': None, 'professions': None,
            'favorite_foods': None, 'pets': None
        }
        try:
            # Try to parse the AI's response as JSON
            import json
            data = json.loads(text)
            # Fill missing fields with None
            data = {**default, **data}
            # Convert lists to strings for fields that expect strings
            for field in ['age_range', 'professions', 'days_available', 'pets']:
                if isinstance(data[field], list):
                    data[field] = ', '.join(map(str, data[field]))
        except Exception:
            # If it fails, ask AI to fix it
            reform = self.llm.invoke(
                "The previous output wasn't valid JSON. Reformat the following into strict JSON only:\n" + text
            )
            import json
            try:
                data = json.loads(reform)
                # Fill missing fields with None
                data = {**default, **data}
                # Convert lists to strings for fields that expect strings
                for field in ['age_range', 'professions', 'days_available', 'pets']:
                    if isinstance(data[field], list):
                        data[field] = ', '.join(map(str, data[field]))
            except Exception:
                # If still fails, return default
                data = default
                # Convert lists to strings for fields that expect strings
                for field in ['age_range', 'professions', 'days_available', 'pets']:
                    if isinstance(data[field], list):
                        data[field] = ', '.join(map(str, data[field]))

        try:
            # Make sure the data matches our expected format
            return OnboardSchema(**data)
        except ValidationError as e:
            raise
