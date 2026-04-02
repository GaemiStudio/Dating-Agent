"""
Database Models

This module defines the structure of our database tables using SQLAlchemy.
We have models for Users, Conversations, and Messages.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base

def gen_uuid():
    """Generate a unique ID for database records."""
    return str(uuid.uuid4())

class User(Base):
    """Represents a user profile in the database."""
    __tablename__ = "users"  # Name of the table in the database

    # Columns in the table
    id = Column(String, primary_key=True, default=gen_uuid)  # Unique ID
    name = Column(String, nullable=True)  # User's name
    age = Column(Integer, nullable=True)  # User's age
    location = Column(String, nullable=True)  # Where they live
    gender = Column(String, nullable=True)  # Gender identity
    personality = Column(Text, nullable=True)  # Description of personality
    looking_for = Column(String, nullable=True)  # What kind of relationship
    days_available = Column(String, nullable=True)  # Available days
    age_range = Column(String, nullable=True)  # Preferred age range
    professions = Column(String, nullable=True)  # Preferred professions
    favorite_foods = Column(String, nullable=True)  # Favorite foods
    pets = Column(String, nullable=True)  # Pet preferences
    created_at = Column(DateTime, default=datetime.utcnow)  # When created

class Conversation(Base):
    """Represents a conversation session."""
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=gen_uuid)  # Session ID
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Link to user
    created_at = Column(DateTime, default=datetime.utcnow)  # When started
    messages = relationship("Message", back_populates="conversation")  # Messages in this convo

class Message(Base):
    """Represents a single message in a conversation."""
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=gen_uuid)  # Message ID
    conversation_id = Column(String, ForeignKey("conversations.id"))  # Which conversation
    role = Column(String)  # 'user' or 'agent'
    content = Column(Text)  # The message text
    created_at = Column(DateTime, default=datetime.utcnow)  # When sent
    conversation = relationship("Conversation", back_populates="messages")  # Link back
