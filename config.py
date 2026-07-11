"""
Configuration settings for the Dating Onboarding Agent
"""

# LLM Configuration
# Switch providers by changing LLM_PROVIDER and LLM_MODEL together:
#   Ollama (local, free): LLM_PROVIDER = "ollama", LLM_MODEL = "mistral"
#   Gemini (cloud, free tier): LLM_PROVIDER = "gemini", LLM_MODEL = "gemini-1.5-flash"
LLM_PROVIDER = "ollama"
LLM_MODEL = "mistral"
LLM_TEMPERATURE = 0.7

# Speech Configuration
SPEECH_RATE = 150  # Words per minute (50-200)
SPEECH_VOLUME = 1.0  # 0.0 to 1.0
VOICE_TIMEOUT = 10  # Seconds to listen

# Profile Configuration
PROFILE_FIELDS = [
    ("name", "What's your name?"),
    ("age", "How old are you?"),
    ("gender", "What's your gender?"),
    ("interested_in", "Who are you interested in meeting?"),
    ("location", "Where are you located?"),
    ("bio", "Tell me a bit about yourself in a few sentences."),
    ("interests", "What are your main interests or hobbies?"),
    ("relationship_goals", "What are you looking for relationship-wise?"),
]

# Output Configuration
PROFILE_SAVE_PATH = "user_profile.json"
CONVERSATION_HISTORY_PATH = "conversation_history.json"
VERBOSE_MODE = False
MAX_TURNS = 20

# Validation Rules
MIN_BIO_LENGTH = 10
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 50
MIN_AGE = 18
MAX_AGE = 120

# Agent persona — sets the tone for all LLM-generated messages
AGENT_PERSONA = """You are a warm, witty onboarding assistant for a dating app.
Think casual coffee date, not job interview. You're genuinely curious about people.
Keep it light, real, and conversational. Never sound like a chatbot or a form."""

# Random fun questions to throw in naturally during conversation
RANDOM_QUESTIONS = [
    "Ok, totally random — if you could only eat one cuisine for the rest of your life, what are you picking?",
    "Morning person or more of a night owl?",
    "What's a hill you would absolutely die on?",
    "If you had a completely free Saturday with zero plans, what does your ideal day look like?",
    "What's something most people wouldn't guess about you just from looking at you?",
    "Would you rather explore a new city solo or with people you know?",
]

# Greeting Messages
WELCOME_MESSAGE = "✨ Welcome to our dating platform!"
GREETING = "Hey! So glad you're here. Think of this as a super chill coffee chat — I'll ask you a few things, you just talk. No forms, no pressure. Let's start easy: what's your name?"
CLOSING_MESSAGE = "Your profile is all set — welcome to the community! I hope you find someone amazing."
SAVE_MESSAGE = "Your profile has been saved."
