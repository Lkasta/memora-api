import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

from models import User, db

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not username or not email or not password:
        return jsonify({"error": "Campos obrigatórios: username, email, password"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email já existe"}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError:
        # Covers the race where two requests register the same email at once.
        db.session.rollback()
        return jsonify({"error": "Email já existe"}), 409

    return jsonify({"message": "Usuário registrado com sucesso!", "id": new_user.id}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Campos obrigatórios: email, password"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        logger.info("Login failed: no user for email %s", email)
        return jsonify({"error": "Credenciais inválidas"}), 401

    if not user.check_password(password):
        logger.info("Login failed: bad password for user_id %s", user.id)
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
