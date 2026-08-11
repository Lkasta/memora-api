"""List every user currently in the database.

Usage:
    python scripts/list_users.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import User


def main():
    app = create_app()
    with app.app_context():
        try:
            users = User.query.all()
        except Exception as exc:  # manual diagnostic script: report and exit cleanly
            print(f"Error accessing database: {exc}")
            return

        if not users:
            print("No users in database.")
            return

        for user in users:
            print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")


if __name__ == "__main__":
    main()
