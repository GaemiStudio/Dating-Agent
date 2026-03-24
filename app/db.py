"""
Database Setup

This module sets up the database connection using SQLAlchemy.
It creates an engine to connect to the database and provides a session maker
for interacting with the database.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Get the database URL from environment, default to a local SQLite file
DATABASE_URL = os.getenv("DB_URL", "sqlite:///./users.db")

# Create the database engine (this is like the connection to the database)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a session maker (this helps us talk to the database)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our database models (tables)
Base = declarative_base()

def init_db():
    """Create all the database tables defined in our models."""
    Base.metadata.create_all(bind=engine)
