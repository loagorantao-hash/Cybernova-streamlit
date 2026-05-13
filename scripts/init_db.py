"""
scripts/init_db.py
Initialize the SQLite database and seed 3 default users.
Run once: python scripts/init_db.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database.connection import init_db, get_session
from backend.database.models import User
from passlib.hash import bcrypt

DEFAULT_USERS = [
    {"username": "admin",   "email": "admin@cybernova.com",   "password": "Admin@2026!",   "role": "admin"},
    {"username": "analyst", "email": "analyst@cybernova.com", "password": "Analyst@2026!", "role": "analyst"},
    {"username": "user",    "email": "user@cybernova.com",    "password": "User@2026!",    "role": "website_user"},
]


def seed_users(session):
    for u in DEFAULT_USERS:
        existing = session.query(User).filter(User.email == u["email"]).first()
        if not existing:
            user = User(
                username=u["username"],
                email=u["email"],
                password_hash=bcrypt.hash(u["password"]),
                role=u["role"],
                is_active=True,
            )
            session.add(user)
            print(f"  Created: {u['username']} ({u['role']})")
        else:
            print(f"  Exists:  {u['username']} ({u['role']})")
    session.commit()


def main():
    print("Initializing CyberNova Analytics database...")
    init_db()
    print("Database schema created.")

    session = get_session()
    try:
        print("Seeding default users:")
        seed_users(session)
        print("\nDatabase initialization complete!")
        print("\nDefault credentials:")
        for u in DEFAULT_USERS:
            print(f"  {u['role']:15s} | {u['email']:30s} | {u['password']}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
    
