"""Quick manual check of the database connection and schema.

Usage:
    python scripts/check_db.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect

from app import create_app
from models import User, db


def main():
    app = create_app()
    with app.app_context():
        print("Checking database status...")
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables found: {tables}")

        if "users" not in tables:
            print("CRITICAL: 'users' table does not exist!")
            return

        users = User.query.all()
        print(f"Total users in 'users' table: {len(users)}")
        for user in users:
            print(f" - {user.email} (ID: {user.id})")


if __name__ == "__main__":
    main()
