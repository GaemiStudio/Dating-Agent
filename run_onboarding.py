"""
Onboarding Agent Runner

This script runs the main onboarding process for the dating platform.
It uses LangGraph for a conversational flow, making it feel like a mini date.
"""

import os
from app.db import init_db
from app.onboarding_graph import run_onboarding_graph
import uuid

def main():
    # Set up the database
    init_db()
    # Choose text or voice mode
    mode = input("Mode (text/voice) [text]: ").strip() or "text"
    # Generate a unique ID for this session
    session_id = str(uuid.uuid4())

    # Run the conversational onboarding using LangGraph
    profile = run_onboarding_graph(mode=mode, session_id=session_id)
    print("Onboarding complete! Profile extracted and saved.")

if __name__ == "__main__":
    main()
