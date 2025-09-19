from flask import Blueprint, request, jsonify
from models import db, User

user_bp = Blueprint("user", __name__)

@user_bp.route("/<int:user_id>", methods=["PUT"])
def upload_user(user_id):
  data = request.json

  if not data:
    return jsonify({"error": "No data provided"}), 400

  user = User.query.filter_by(id=user_id).first()

  if not user:
    return "User not fount!", 404
  
  username = data.get("username")
  lastname = data.get("lastname")
  email = data.get("email")
  password = data.get("password")

  if username:
    user.username = data["username"]
  
  if lastname:
    user.lastname = data["lastname"]
  
  if email:
    user.email = data["email"]
  
  if password:
    user.set_password(data["password"])

  db.session.commit()

  return jsonify({
    "message": "User has been updated!"
  })
