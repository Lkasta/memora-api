from app import create_app
from models import db, User
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    print("Checking Database Status...")
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Tables found: {tables}")
    
    if 'users' in tables:
        users = User.query.all()
        print(f"Total users in 'users' table: {len(users)}")
        for u in users:
            print(f" - {u.email} (ID: {u.id})")
    else:
        print("CRITICAL: 'users' table does not exist!")
