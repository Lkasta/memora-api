"""Create a user directly in the database (bypasses the /auth/register API).

Usage:
    python scripts/create_user.py --username Jonas --email jonas@memora.com
    (you'll be prompted for a password so it never lands in shell history;
    pass --password to skip the prompt if you really need to)
"""
import argparse
import getpass
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import User, db


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--lastname", default=None)
    parser.add_argument(
        "--password",
        default=None,
        help="If omitted, you'll be prompted instead (recommended).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    password = args.password or getpass.getpass("Password: ")

    app = create_app()
    with app.app_context():
        email = args.email.strip().lower()
        if User.query.filter_by(email=email).first():
            print(f"A user with email {email!r} already exists.")
            return

        user = User(username=args.username, lastname=args.lastname, email=args.email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        print(f"Created user {user.email!r} (id={user.id}).")


if __name__ == "__main__":
    main()
