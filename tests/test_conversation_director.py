"""
Tests for skills/conversation_director.py

LLM is mocked so these tests run without Ollama or Gemini.
"""

from unittest.mock import patch
from skills.conversation_director import get_next_message


def test_returns_string():
    with patch("skills.conversation_director.chat", return_value="Hey there!"):
        result = get_next_message(
            user_input="I love hiking",
            missing_fields=["age", "location"],
            profile_so_far={"name": "Alex"},
            recent_history=[],
        )
        assert isinstance(result, str)
        assert result == "Hey there!"

def test_calls_llm_once():
    with patch("skills.conversation_director.chat", return_value="Nice!") as mock_chat:
        get_next_message(
            user_input="test input",
            missing_fields=["age"],
            profile_so_far={},
            recent_history=[],
        )
        mock_chat.assert_called_once()

def test_stream_flag_passed_through():
    """stream=True should be forwarded to chat()."""
    with patch("skills.conversation_director.chat", return_value="streaming!") as mock_chat:
        get_next_message(
            user_input="hello",
            missing_fields=["age"],
            profile_so_far={},
            recent_history=[],
            stream=True,
        )
        _, kwargs = mock_chat.call_args
        assert kwargs.get("stream") is True

def test_empty_missing_fields_still_calls_llm():
    """Even with nothing left to ask, the director should still respond."""
    with patch("skills.conversation_director.chat", return_value="Great talking!") as mock_chat:
        result = get_next_message(
            user_input="thanks",
            missing_fields=[],
            profile_so_far={"name": "Alex", "age": "28"},
            recent_history=[],
        )
        mock_chat.assert_called_once()
        assert result == "Great talking!"
