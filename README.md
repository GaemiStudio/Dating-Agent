# Dating Platform Onboarding Agent

This is a simple AI-powered chatbot that helps new users sign up for a dating app. It asks questions to learn about the user (like name, age, what they're looking for) and saves this info in a database. It can talk via text or voice, and remembers things from the conversation to give better answers.

## What It Does

- **Conversational Flow**: Uses LangGraph to create a natural, mini-date-like experience with dynamic responses and empathy.
- **Asks Questions**: Asks about your name, age, location, personality, dating preferences, etc.
- **Uses AI**: Uses a language model (like ChatGPT but local) to understand your answers and fill in profile details.
- **Friendly & Professional**: The AI agent is warm and approachable but maintains a professional tone, listening carefully while cutting through to the core meaning.
- **Remembers Stuff**: Saves conversation history in a "vector memory" so it can reference what you said earlier.
- **Saves Data**: Stores user profiles in a SQLite database with unique IDs.
- **Voice Support**: Can speak questions and listen to your answers (if you have a microphone).
- **Demo Ready**: Comes with sample user profiles for testing.

## Quick Start

1. **Install Python stuff** (if you don't have them):
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up the database**:
   ```bash
   python3 seed_db.py  # Load demo users
   ```

3. **Run the onboarding**:
   ```bash
   python3 run_onboarding.py
   ```
   Choose "text" or "voice" mode.

4. **Look at profiles**:
   ```bash
   python3 list_profiles.py --limit 5
   ```

## Files Explained

- `run_onboarding.py`: The main program that runs the chatbot using LangGraph for flow.
- `app/onboarding_graph.py`: Defines the conversational graph with nodes for greeting, questioning, etc.
- `app/agent.py`: The AI brain that extracts info from conversations.
- `app/db.py`: Sets up the database connection.
- `app/models.py`: Defines what data we store (users, conversations).
- `app/vector_store.py`: Handles remembering conversation details.
- `app/voice.py`: Makes the computer talk and listen.
- `list_profiles.py`: A tool to view saved user profiles.
- `seed_db.py`: Loads demo data into the database.
- `seeds.json`: Sample user profiles for testing.
- `demo_users.db`: A copy of the database with demo data.

## How It Works (Simple Version)

1. You start the program.
2. It asks you questions one by one.
3. Your answers get saved and sent to an AI model.
4. The AI pulls out key info (like "name: John, age: 25").
5. Everything gets stored in a database.
6. The AI remembers your answers for future questions.

## Notes

- The AI part needs Ollama running (a local AI server). Install it from ollama.ai and run `ollama serve`.
- Voice mode needs a microphone and speakers.
- This is a demo, so it uses fake data and simple AI prompts.
- Demo data is available in `demo_users.db` and can be seeded with `python seed_db.py`.