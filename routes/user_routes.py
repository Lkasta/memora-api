from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User

user_bp = Blueprint("user", __name__)

@user_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
def upload_user(user_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json

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

    db.session.commit()

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
        "image": user.profile_image_url
    }), 200
