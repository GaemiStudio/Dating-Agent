# Quick Start Guide

Get your dating platform onboarding agent running in 5 minutes! 

## Prerequisites
- Python 3.9+
- OpenAI API key (get free credits at [platform.openai.com](https://platform.openai.com))
- Microphone (for voice mode)

## Setup (macOS)

### 1. Clone into Project
```bash
cd /Users/sstep/Desktop/LangChain/"Dating Agent 1.0"
```

### 2. Run Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

### 3. Add Your OpenAI API Key
```bash
# Edit .env and add your key
nano .env

# Find this line and replace with your actual key:
# OPENAI_API_KEY=sk-your-actual-key-here
```

### 4. (Optional) Install Audio Support
```bash
brew install portaudio
pip install --upgrade pyaudio
```

## Running the Agent

### Text Mode (Recommended for First Run)
```bash
source venv/bin/activate
python main.py
# Select option 2 for text input
```

### Voice Mode
```bash
source venv/bin/activate
python main.py
# Select option 1 for voice input
# Speak clearly when prompted
```

## What Happens

1. **Welcome**: Agent greets you
2. **Questions**: Answers 8 profile questions
3. **Validation**: Checks your responses
4. **Summary**: Shows your profile
5. **Save**: Stores data in `user_profile.json`

## Output Example

```json
{
  "name": "Alex Johnson",
  "age": 28,
  "gender": "Male",
  "interested_in": "Women",
  "location": "San Francisco, CA",
  "bio": "Fun and adventurous tech enthusiast...",
  "interests": ["Hiking", "Cooking", "Gaming"],
  "relationship_goals": "Long-term relationship",
  "created_at": "2026-02-20T14:30:00"
}
```

## Troubleshooting

### "OPENAI_API_KEY not found"
- Make sure `.env` file exists
- Verify key is valid at platform.openai.com

### Speech Recognition Not Working
- Ensure microphone is connected
- Try text mode first
- Check System Preferences > Sound

### Module Import Errors
```bash
pip install -r requirements.txt
```

### Still Having Issues?
See detailed troubleshooting in [README.md](README.md#troubleshooting)

## Customization

Want to change questions or settings?

See [CUSTOMIZATION.md](CUSTOMIZATION.md) for:
- Custom profile fields
- Change greeting messages
- Adjust speech settings
- Database integration
- Multi-language support
- Image uploads
- And more!

## Common Tasks

### Clear Saved Profile
```bash
rm user_profile.json
```

### View Saved Profile
```bash
cat user_profile.json
```

### Test Configuration
```bash
python -c "import config; print(config.PROFILE_FIELDS)"
```

### Check Python Environment
```bash
which python3
python3 --version
```

## Next Steps

1. ✅ Run the agent successfully
2. 📝 Check `user_profile.json` output
3. 🎯 Customize to match your requirements
4. 🚀 Integrate into your application

## Cost Estimate

For 1000 onboarding sessions:

- **OpenAI API**: ~$3-5 (GPT-4) or ~$0.50 (GPT-3.5)
- **Google Speech Recognition**: Free
- **Hosting**: Depends on platform

## Need Help?

1. Check [README.md](README.md) for full documentation
2. Review [CUSTOMIZATION.md](CUSTOMIZATION.md) for extensions
3. Check error messages in terminal
4. Review OpenAI docs at docs.openai.com

---

**Ready?** Run `python main.py` now! 🚀
