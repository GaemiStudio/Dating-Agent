# Quick Start Guide

Get the dating platform onboarding agent running in under 5 minutes.

## Prerequisites

- Python 3.9+
- [Ollama](https://ollama.com) installed and running *(default — free, local, no API key)*
- *Or:* a [Gemini API key](https://aistudio.google.com) if you prefer cloud inference

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/GaemiStudio/Dating-Agent.git
cd Dating-Agent
```

### 2. Run the setup script

```bash
chmod +x setup.sh
./setup.sh
```

This creates a virtual environment and installs all dependencies.

### 3. Start Ollama and pull the model

```bash
# In a separate terminal — keep this running
ollama serve

# Pull the model (one-time, ~4 GB)
ollama pull mistral
```

### 4. Run the agent

```bash
source venv/bin/activate
python main.py
```

Select **option 2** (text input) for your first run.

---

## Using Gemini instead of Ollama

If you'd rather use Google Gemini (no local model required):

1. Add your key to `.env`:
   ```
   GEMINI_API_KEY=your-key-here
   ```
2. Update `config.py`:
   ```python
   LLM_PROVIDER = "gemini"
   LLM_MODEL    = "gemini-1.5-flash"
   ```

---

## (Optional) Voice input

Requires portaudio and pyaudio — see [README.md](README.md#voice-input) for install instructions.

---

## What to expect

1. The agent greets you and asks a few questions conversationally
2. It extracts your profile fields from your answers (no forms)
3. At the end it generates a personality vibe and a match estimate
4. Your profile is saved to `user_profile.json`

---

## Troubleshooting

### `ollama: connection refused`
Ollama isn't running. Open a terminal and run `ollama serve`, then try again.

### `mistral: model not found`
You haven't pulled the model yet. Run `ollama pull mistral`.

### `GEMINI_API_KEY not set`
You switched to the Gemini provider but haven't added the key to `.env`.

### Module import errors
```bash
pip install -r requirements.txt
```

### Speech recognition not working
Try text mode first (option 2). See [README.md](README.md#voice-input) for voice setup.

---

## Run the tests

```bash
python -m pytest tests/ -v
```

---

See [README.md](README.md) for full documentation and [CUSTOMIZATION.md](CUSTOMIZATION.md) to change fields, prompts, or LLM settings.
