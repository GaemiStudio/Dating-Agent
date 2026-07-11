"""
LLM Wrapper
Single entry point for all LLM calls in this project.
Routes to Ollama or Gemini based on LLM_PROVIDER in config.py.
Skills never import ollama or google.generativeai directly — they call chat() here.
"""

import os
import config


def chat(prompt: str) -> str:
    """Send a single-turn prompt, return the response text."""
    if config.LLM_PROVIDER == "ollama":
        return _ollama(prompt)
    elif config.LLM_PROVIDER == "gemini":
        return _gemini(prompt)
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{config.LLM_PROVIDER}'. "
            "Set it to 'ollama' or 'gemini' in config.py."
        )


def _ollama(prompt: str) -> str:
    import ollama
    response = ollama.chat(
        model=config.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"].strip()


def _gemini(prompt: str) -> str:
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. Add it to your .env file:\n"
            "  GEMINI_API_KEY=your_key_here\n"
            "Get a free key at https://aistudio.google.com"
        )
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(config.LLM_MODEL)
    response = model.generate_content(prompt)
    return response.text.strip()
