from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    try:
        users = User.query.all()
        if not users:
            print("No users in database.")
        for user in users:
            print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
    except Exception as e:
        print(f"Error accessing database: {e}")
