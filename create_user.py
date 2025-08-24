from app import create_app
from models import db, User

app = create_app()

with app.app_context():
  user = User(username="Jonas", email="jonas@memora.com")
  db.session.add(user)
  db.session.commit()
  print("Usuário criado com ID:", user.id)
