from flask import Blueprint, request, Response
from werkzeug.utils import secure_filename

from models import db, Image

img_bp = Blueprint("imgs", __name__)

@img_bp.route("/upload-img", methods=["POST"])
def upload():
  pic = request.files['pic']

  if not pic:
    return "No image uploaded!", 400
  
  filename = secure_filename(pic.filename)
  mimetype = pic.mimetype

  if not mimetype:
    return "Bad upload!", 400
  
  img = Image(img=pic.read(), filename=filename, mimetype=mimetype)
  db.session.add(img)
  db.session.commit()

  return "Image uploaded!", 200

@img_bp.route('/<int:image_id>')
def get_img(image_id):
  img = Image.query.filter_by(id=image_id).first()
  if not img:
    return 'Img Not Found!', 404

  return Response(img.img, mimetype=img.mimetype)
