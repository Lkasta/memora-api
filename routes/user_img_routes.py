from flask import Blueprint, request, Response, jsonify
from werkzeug.utils import secure_filename

from models import db, UserImage

user_img_bp = Blueprint("user_img", __name__)

@user_img_bp.route("/", methods=["POST"])
def upload():
  pic = request.files['pic']
  user_id = request.form.get("user_id")

  if not pic:
    return "No image uploaded!", 400
  
  filename = secure_filename(pic.filename)
  mimetype = pic.mimetype

  if not mimetype:
    return "Bad upload!", 400
  
  img = UserImage(img=pic.read(), filename=filename, mimetype=mimetype, user_id=user_id)
  db.session.add(img)
  db.session.commit()

  return "Image uploaded!", 200

@user_img_bp.route('/', methods=["GET"])
def get_img():
  user_id = request.form.get("user_id")

  img = UserImage.query.filter_by(user_id=user_id).first()
  if not img:
    return 'Img Not Found!', 404

  return Response(img.img, mimetype=img.mimetype)

@user_img_bp.route("/", methods=["PUT"])
def upload_img():
  new_pic = request.files['pic']
  new_filename = secure_filename(new_pic.filename)
  new_mimetype = new_pic.mimetype

  if not new_pic:
    return "No image uploaded!", 400

  user_id = request.form.get("user_id")

  img = UserImage.query.filter_by(user_id=user_id).first()

  if not img:
    return "Memory not found!", 404
  
  img.filename = new_filename
  img.mimetype = new_mimetype
  img.img = new_pic.read()

  db.session.commit()

  return jsonify({
    "message": "Image updated successfully!"
  })

@user_img_bp.route("/", methods=["DELETE"])
def delete_img():
  user_id = request.form.get("user_id")

  img = UserImage.query.filter_by(user_id=user_id).first()

  if not img:
    return "Image not found!", 404
  
  db.session.delete(img)
  db.session.commit()

  return jsonify({"message": "Image deleted successfully!"})
