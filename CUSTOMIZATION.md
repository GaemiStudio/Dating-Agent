# Customization Guide

## Quick Customization

### Change Profile Fields

Edit `config.py` and modify the `PROFILE_FIELDS` list:

```python
PROFILE_FIELDS = [
    ("field_name", "Question to ask?"),
    ("another_field", "Another question?"),
]
```

### Modify Greeting Messages

Update these in `config.py`:
```python
WELCOME_MESSAGE = "Your custom welcome message"
GREETING = "Your custom greeting"
CLOSING_MESSAGE = "Your custom closing message"
```

### Adjust Speech Settings

```python
SPEECH_RATE = 150      # 50-200 words per minute
SPEECH_VOLUME = 1.0    # 0.0 to 1.0
VOICE_TIMEOUT = 10     # Seconds to wait for voice input
```

### Change LLM Model

```python
LLM_MODEL = "gpt-4"        # or "gpt-3.5-turbo" for lower cost
LLM_TEMPERATURE = 0.7      # 0.0-1.0: lower = more deterministic
```

---

## Advanced Customization

### Add Custom Validation

Edit `utils.py` and add a validator:

```python
def validate_custom_field(value: str) -> tuple[bool, str]:
    """Validate custom field"""
    if some_condition:
        return True, "Valid"
    return False, "Invalid reason"
```

Then update `validate_field()` function:
```python
def validate_field(field: str, value: Any) -> tuple[bool, str]:
    validators = {
        "name": validate_name,
        "age": validate_age,
        "custom_field": validate_custom_field,  # Add this
    }
    # ... rest of code
```

### Custom Agent Tools

Add new tools in `main.py`:

```python
@tool
def custom_tool(input_text: str) -> str:
    """Your custom tool description"""
    # Your logic here
    return result

# Add to tools list in setup_agent()
tools = [extract_user_info, validate_profile_data, 
         generate_next_question, custom_tool]
```

### Database Integration

Replace JSON saving with database:

```python
def save_profile(self, filename: str = None):
    """Save profile to database"""
    # Instead of save_json(self.profile, filename)
    db.insert("profiles", self.profile)
    print("Profile saved to database")
```

Add to `requirements.txt`:
- PostgreSQL: `psycopg2-binary`
- MongoDB: `pymongo`
- Firebase: `firebase-admin`

### Conditional Questions

Modify `run_onboarding()` to ask different questions based on previous answers:

```python
for field, question in config.PROFILE_FIELDS:
    # Skip certain questions based on conditions
    if field == "interested_in" and profile["gender"] == "Other":
        question = "Who would you like to meet?"
    
    self.speak(question)
```

### Multi-Language Support

Create language configs:

```python
# config_es.py for Spanish
PROFILE_FIELDS = [
    ("nombre", "¿Cuál es tu nombre?"),
    ("edad", "¿Cuántos años tienes?"),
]

# In main.py
language = os.getenv("LANGUAGE", "en")
if language == "es":
    import config_es as config
```

### Add Image Upload

```python
def capture_profile_image(self) -> Optional[str]:
    """Capture profile image"""
    import cv2
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    
    filename = f"profile_{self.profile.profile['name']}.jpg"
    cv2.imwrite(filename, frame)
    return filename

# In run_onboarding()
self.profile.profile["photo"] = self.capture_profile_image()
```

### Add Email/Phone Verification

```python
def verify_email(self, email: str) -> bool:
    """Send verification email"""
    import smtplib
    from email.mime.text import MIMEText
    
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(os.getenv("EMAIL"), os.getenv("EMAIL_PASSWORD"))
    
    msg = MIMEText(f"Verify code: 123456")
    msg["Subject"] = "Email Verification"
    msg["From"] = os.getenv("EMAIL")
    
    server.sendmail(os.getenv("EMAIL"), email, msg.as_string())
    server.quit()
    return True
```

### Enhanced Error Handling

Create retry logic in `main.py`:

```python
def get_voice_input_with_retry(self, max_retries: int = 3) -> Optional[str]:
    """Get voice input with retry logic"""
    for attempt in range(max_retries):
        user_input = self.get_voice_input()
        if user_input:
            return user_input
        self.speak(f"Let me try again. Attempt {attempt + 1} of {max_retries}")
    
    self.speak("Using text mode instead")
    return self.get_text_input()
```

### Add Analytics Tracking

```python
def track_event(self, event: str, data: dict = None):
    """Track user events for analytics"""
    event_data = {
        "timestamp": datetime.now().isoformat(),
        "event": event,
        "data": data
    }
    # Send to analytics service (Google Analytics, Mixpanel, etc.)
    
# Usage
self.track_event("profile_started", {"input_mode": self.input_mode})
self.track_event("field_completed", {"field": "name"})
self.track_event("onboarding_completed", self.profile.profile)
```

---

## Environment Setup

Add to `.env` for extended features:

```
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://user:pass@localhost/db
EMAIL=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
ANALYTICS_KEY=your-analytics-key
LANGUAGE=en
```

---

## Testing

Create `test_main.py`:

```python
import sys
import json
from utils import validate_name, validate_age, validate_bio

def test_validators():
    assert validate_name("John")[0] == True
    assert validate_name("J")[0] == False
    assert validate_age(25)[0] == True
    assert validate_age(15)[0] == False
    print("✓ All validators passed")

if __name__ == "__main__":
    test_validators()
```

Run tests:
```bash
python test_main.py
```

---

## Performance Tips

1. **Cache LLM responses** for common questions
2. **Use GPT-3.5-turbo** instead of GPT-4 for faster/cheaper inference
3. **Batch multiple API calls** when possible
4. **Implement request timeout** to prevent hanging

---

## Troubleshooting Customizations

- **Syntax Errors**: Validate Python syntax with `python -m py_compile file.py`
- **Import Errors**: Ensure all imports are in `requirements.txt`
- **Config Errors**: Check `config.py` for typos
- **LLM Errors**: Verify OpenAI API key in `.env`
