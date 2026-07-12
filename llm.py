"""
LLM Wrapper
Single entry point for all LLM calls in this project.
Routes to Ollama or Gemini based on LLM_PROVIDER in config.py.
Skills never import ollama or google.generativeai directly — they call chat() here.
"""

import os
import time
import logging

import config

logger = logging.getLogger(__name__)

MAX_RETRIES = 2
RETRY_DELAY = 2  # seconds between retries


def chat(prompt: str, stream: bool = False) -> str:
    """
    Send a single-turn prompt, return the response text.
    Set stream=True to print tokens live as they arrive.
    Retries up to MAX_RETRIES times on failure.
    """
    for attempt in range(MAX_RETRIES + 1):
        try:
            if config.LLM_PROVIDER == "ollama":
                return _ollama(prompt, stream)
            elif config.LLM_PROVIDER == "gemini":
                return _gemini(prompt, stream)
            else:
                raise ValueError(
                    f"Unknown LLM_PROVIDER '{config.LLM_PROVIDER}'. "
                    "Set it to 'ollama' or 'gemini' in config.py."
                )
        except ValueError:
            raise  # config errors should not be retried
        except Exception as e:
            if attempt < MAX_RETRIES:
                logger.warning(f"LLM call failed (attempt {attempt + 1}/{MAX_RETRIES + 1}): {e} — retrying in {RETRY_DELAY}s")
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"LLM call failed after {MAX_RETRIES + 1} attempts: {e}")
                raise


def _ollama(prompt: str, stream: bool) -> str:
    import ollama
    messages = [{"role": "user", "content": prompt}]
    if stream:
        chunks = ollama.chat(model=config.LLM_MODEL, messages=messages, stream=True)
        full = ""
        for chunk in chunks:
            token = chunk["message"]["content"]
            print(token, end="", flush=True)
            full += token
        print()
        return full.strip()
    else:
        response = ollama.chat(model=config.LLM_MODEL, messages=messages)
        return response["message"]["content"].strip()


def _gemini(prompt: str, stream: bool) -> str:
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
    if stream:
        response = model.generate_content(prompt, stream=True)
        full = ""
        for chunk in response:
            token = chunk.text
            print(token, end="", flush=True)
            full += token
        print()
        return full.strip()
    else:
        response = model.generate_content(prompt)
        return response.text.strip()
