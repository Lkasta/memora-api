from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from models import User, db
from utils import clean_image_url

user_bp = Blueprint("user", __name__)


@user_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
def upload_user(user_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No data provided"}), 400

    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"error": "User not found!"}), 404

    if "username" in data:
        user.username = data["username"]

    if "lastname" in data:
        user.lastname = data["lastname"]

    if "email" in data:
        user.email = data["email"]

    if "password" in data:
        user.set_password(data["password"])

    if "profile_image_url" in data:
        user.profile_image_url = data["profile_image_url"]

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email já está em uso"}), 409

    return jsonify({
        "message": "User has been updated!"
    })


@user_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"error": "User not found!"}), 404

    return jsonify({
        "id": user.id,
        "name": user.username,
        "lastname": user.lastname,
        "email": user.email,
        "image": clean_image_url(user.profile_image_url),
    }), 200
