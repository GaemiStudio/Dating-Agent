"""
Configuration settings for the Dating Onboarding Agent
"""

# LLM Configuration
LLM_MODEL = "gpt-4"
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
VERBOSE_MODE = True

# Validation Rules
MIN_BIO_LENGTH = 10
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 50
MIN_AGE = 18
MAX_AGE = 120

# Greeting Messages
WELCOME_MESSAGE = "✨ Welcome to our dating platform!"
GREETING = "Great to meet you! I'm here to help you set up your profile. Let's start with some basics. What's your name?"
CLOSING_MESSAGE = "Your profile has been created successfully! Welcome to our community!"
SAVE_MESSAGE = "Your profile has been saved."
