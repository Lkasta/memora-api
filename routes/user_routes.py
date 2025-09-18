from flask import Blueprint, request, jsonify
from models import db, User

user_bp = Blueprint("user", __name__)

@user_bp.route("/", methods=["PUT"])
def upload_user():
  data = request.json
  user_id = data["user_id"]
  print(f"user_id: {user_id}")

  user = User.query.filter_by(id=user_id).first()

  if not user:
    return "User not fount!", 404

  if data["username"]:
    user.username = data["username"]
  if data["password"]:
    user.set_password(data["password"])

  db.session.commit()

  return jsonify({
    "message": "User has been updated!"
  })
