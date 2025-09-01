from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
  data = request.json

  if not data or not data.get("username") or not data.get("email") or not data.get("password"):
    return jsonify({"error": "Campos obrigatórios: username, email, password"}), 400

  if User.query.filter_by(email=data["email"]).first():
    return jsonify({"error": "Email já existe"}), 400

  new_user = User(
    username=data["username"],
    email=data["email"],
  )
  new_user.set_password(data["password"])

  db.session.add(new_user)
  db.session.commit()

  return jsonify({"message": "Usuário registrado com sucesso!", "id": new_user.id}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
  data = request.json

  if not data or not data.get("email") or not data.get("password"):
    return jsonify({"error": "Campos obrigatórios: email, password"}), 400

  user = User.query.filter_by(email=data["email"]).first()

  if not user or not user.check_password(data["password"]):
    return jsonify({"error": "Credenciais inválidas"}), 401

  access_token = create_access_token(identity=str(user.id))

  return jsonify({
    "message": "Login realizado com sucesso!",
    "token": access_token,
    "user": {
      "id": user.id,
      "username": user.username,
      "email": user.email,
    }
  })
