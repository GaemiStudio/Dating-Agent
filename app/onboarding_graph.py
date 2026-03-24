"""
LangGraph-based Conversational Onboarding Flow

This module defines a graph for the onboarding process, making it feel like a mini date:
interactive, engaging, with personality-driven responses.
"""

from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
import uuid

# Define the state for the conversation graph
class OnboardingState(TypedDict):
    session_id: str
    profile: dict  # Current extracted profile
    current_question_index: int
    questions: List[str]
    conversation_history: List[str]  # List of exchanges
    mode: str  # 'text' or 'voice'
    complete: bool

# Questions in order
QUESTIONS = [
    "Hi! I'm excited to help you get set up. What's your name?",
    "Great to meet you! How old are you?",
    "Where are you located? I'd love to know more about your area.",
    "What's your gender identity? Feel free to share as much as you're comfortable with.",
    "Tell me a bit about your personality—what makes you, you?",
    "What are you looking for in a relationship? Casual dates, something serious?",
    "What days work best for you to meet someone?",
    "What's your preferred age range for partners?",
    "Any professions you're drawn to in a partner?",
    "What's your favorite food? I love hearing about people's tastes!",
    "Do you have pets, or like them? What kind?"
]

def greet_user(state: OnboardingState) -> OnboardingState:
    """Start the conversation with a friendly greeting."""
    greeting = "Welcome to our dating platform! I'm here to get to know you better and set up your profile. Let's make this fun, like a mini chat over coffee. Ready?"
    if state['mode'] == 'voice':
        speak(greeting)
    else:
        print(greeting)
    state['conversation_history'].append(f"Agent: {greeting}")
    return state

def ask_question(state: OnboardingState) -> OnboardingState:
    """Ask the next question in a conversational way."""
    idx = state['current_question_index']
    if idx < len(state['questions']):
        question = state['questions'][idx]
        if state['mode'] == 'voice':
            speak(question)
        else:
            print(question)
        state['conversation_history'].append(f"Agent: {question}")
    return state

def process_answer(state: OnboardingState) -> OnboardingState:
    """Get user answer, extract info, update profile and memory."""
    from .agent import OnboardingAgent
    from .voice import speak, listen
    # from .vector_store import add_memory
    from .db import SessionLocal
    from .models import Message

    idx = state['current_question_index']
    question = state['questions'][idx]

    # Get user input
    if state['mode'] == 'voice':
        try:
            answer = listen()
        except:
            speak("I didn't catch that. Can you type it?")
            answer = input("Your answer: ")
    else:
        answer = input("Your answer: ")

    if not answer:
        answer = "Not provided"

    # Save to conversation DB
    with SessionLocal() as s:
        msg = Message(conversation_id=state['session_id'], role="user", content=answer)
        s.add(msg)
        s.commit()

    # Add to vector memory
    # Temporarily disable due to HF loading issues
    # add_memory(state['session_id'], answer, {"role": "user", "question": question})

    # Extract/update profile using agent
    agent = OnboardingAgent()
    full_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(state['questions'][:idx+1], [ans for ans in state['conversation_history'] if "User:" in ans] + [answer])])
    extracted = agent.extract_all(full_text, state['session_id'])
    state['profile'] = extracted.dict()

    # Generate insight every 3 questions
    if (idx + 1) % 3 == 0 and idx > 0:
        insight_prompt = f"Based on the following user profile data, give a short, positive insight about the user in 1-2 sentences. Be warm and encouraging.\nProfile: {state['profile']}\nInsight:"
        insight = agent.llm.invoke(insight_prompt)
        insight_text = str(insight).strip()
        if state['mode'] == 'voice':
            speak(insight_text)
        else:
            print(insight_text)
        state['conversation_history'].append(f"Agent: {insight_text}")

    # Add empathy/response
    import random
    responses = [
        "Got it!",
        "Thanks for sharing that.",
        "Okay, noted.",
        "Cool!",
        "Alright.",
        "Thanks!",
        "I see.",
        "Okay.",
        "Noted.",
        "Thanks for telling me.",
    ]
    response = random.choice(responses)
    if state['mode'] == 'voice':
        speak(response)
    else:
        print(response)
    state['conversation_history'].append(f"User: {answer}")
    state['conversation_history'].append(f"Agent: {response}")

    state['current_question_index'] += 1
    return state

def check_complete(state: OnboardingState) -> str:
    """Decide if onboarding is done or continue."""
    if state['current_question_index'] >= len(state['questions']):
        return "confirm"
    return "ask"

def confirm_profile(state: OnboardingState) -> OnboardingState:
    """Show profile summary and confirm."""
    profile = state['profile']
    summary = f"Based on our chat, here's what I have: Name: {profile.get('name', 'Unknown')}, Age: {profile.get('age', 'Unknown')}, Location: {profile.get('location', 'Unknown')}, etc. Does this look right?"
    if state['mode'] == 'voice':
        speak(summary)
    else:
        print(summary)
    state['conversation_history'].append(f"Agent: {summary}")

    # Simple confirmation (in real app, loop until yes)
    confirm = input("Confirm? (y/n): ").lower()
    if confirm == 'y':
        state['complete'] = True
    else:
        # Could add edit logic here
        state['complete'] = True  # For now, proceed
    return state

def save_profile(state: OnboardingState) -> OnboardingState:
    """Save the final profile to DB."""
    from .models import User, Conversation
    from .db import SessionLocal

    with SessionLocal() as s:
        user = User(**state['profile'])
        s.add(user)
        s.commit()
        s.refresh(user)
        # Link to conversation
        conv = s.query(Conversation).filter(Conversation.id == state['session_id']).first()
        if conv:
            conv.user_id = user.id
            s.commit()
        print(f"Profile saved! Your ID: {user.id}")
    return state

# Build the graph
def create_onboarding_graph():
    graph = StateGraph(OnboardingState)

    graph.add_node("greet", greet_user)
    graph.add_node("ask", ask_question)
    graph.add_node("process", process_answer)
    graph.add_node("confirm", confirm_profile)
    graph.add_node("save", save_profile)

    graph.set_entry_point("greet")
    graph.add_edge("greet", "ask")
    graph.add_edge("ask", "process")
    graph.add_conditional_edges("process", check_complete, {"ask": "ask", "confirm": "confirm"})
    graph.add_edge("confirm", "save")
    graph.add_edge("save", END)

    return graph.compile()

# Function to run the graph
def run_onboarding_graph(mode: str = "text", session_id: str = None) -> dict:
    from .db import SessionLocal
    from .models import Conversation

    if not session_id:
        session_id = str(uuid.uuid4())

    # Create conversation in DB
    with SessionLocal() as s:
        conv = Conversation(id=session_id)
        s.add(conv)
        s.commit()

    initial_state = OnboardingState(
        session_id=session_id,
        profile={},
        current_question_index=0,
        questions=QUESTIONS,
        conversation_history=[],
        mode=mode,
        complete=False
    )

    graph = create_onboarding_graph()
    final_state = graph.invoke(initial_state)
    return final_state['profile']