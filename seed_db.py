"""
Seed the Database

This script loads demo user profiles from a JSON file and saves them to the database.
It's useful for testing and demos.
"""

import json
from app.db import init_db, SessionLocal
from app.models import User

def load_seeds(path="seeds.json"):
    """Load the seed data from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def seed_db(path="seeds.json"):
    """Add the seed users to the database."""
    init_db()  # Make sure the database tables exist
    seeds = load_seeds(path)  # Load the data from file
    with SessionLocal() as session:
        # Clear any existing users to start fresh
        session.query(User).delete()
        session.commit()

        users = []
        for s in seeds:
            # Create a User object from the seed data
            u = User(
                name=s.get("name"),
                age=int(s.get("age")) if s.get("age") else None,
                location=s.get("location"),
                gender=s.get("gender"),
                personality=s.get("personality"),
                looking_for=s.get("looking_for"),
                days_available=s.get("days_available"),
                age_range=s.get("age_range"),
                professions=s.get("professions"),
                favorite_foods=s.get("favorite_foods"),
                pets=s.get("pets"),
            )
            users.append(u)

        session.add_all(users)  # Add all users at once
        session.commit()  # Save to database

        # Print the IDs of the users we added
        for u in users:
            session.refresh(u)  # Get the ID from the database
            print("Inserted:", u.id, u.name)

if __name__ == "__main__":
    seed_db()
