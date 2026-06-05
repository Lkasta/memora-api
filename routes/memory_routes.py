import base64
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Memory

memory_bp = Blueprint("memory", __name__)

@memory_bp.route("/", methods=["GET"])
@jwt_required()
def list_memories():
    user_id = int(get_jwt_identity())
    memories = Memory.query.filter_by(user_id=user_id).order_by(Memory.event_date.desc()).all()

    result = []
    for m in memories:
        img_url = m.image_url
        if img_url and img_url.startswith("data:image/") and "base64,http" in img_url:
            img_url = img_url.split("base64,")[1]

        result.append({
            "id": m.id,
            "title": m.title,
            "content": m.content,
            "event_date": m.event_date.isoformat(),
            "user_id": m.user_id,
            "image": img_url  # Send the URL
        })

    return jsonify(result)

@memory_bp.route("/<int:memory_id>", methods=["GET"])
@jwt_required()
def get_unique_memory(memory_id):
    user_id = int(get_jwt_identity())
    memory = Memory.query.filter_by(id=memory_id, user_id=user_id).first()

    if not memory:
        return jsonify({"error": "Memory not found"}), 404

    img_url = memory.image_url
    if img_url and img_url.startswith("data:image/") and "base64,http" in img_url:
        img_url = img_url.split("base64,")[1]

    return jsonify({
        "id": memory.id,
        "title": memory.title,
        "content": memory.content,
        "event_date": memory.event_date.isoformat(),
        "user_id": memory.user_id,
        "image": img_url
    })

@memory_bp.route("/<int:memory_id>", methods=["PUT"])
@jwt_required()
def update_memory(memory_id):
    user_id = int(get_jwt_identity())
    memory = Memory.query.filter_by(id=memory_id, user_id=user_id).first()
    if not memory:
        return jsonify({"error": "Memory not found"}), 404

    data = request.json
    if not data:
        return jsonify({"error": "Nenhum dado fornecido"}), 400

    if "title" in data:
        memory.title = data["title"]
    if "content" in data:
        memory.content = data["content"]
    if "event_date" in data:
        memory.event_date = data["event_date"]
    if "image_url" in data:
        memory.image_url = data["image_url"]

    db.session.commit()
    return jsonify({
        "message": "Memory updated successfully!",
        "memory": {"id": memory.id}
    })

@memory_bp.route("/", methods=["POST"])
@jwt_required()
def create_memory():
    user_id = int(get_jwt_identity())
    data = request.json

    if not data or not data.get("title") or not data.get("event_date"):
        return jsonify({"error": "Campos obrigatórios: title, event_date"}), 400

    new_memory = Memory(
        title=data["title"],
        content=data.get("content"),
        event_date=data["event_date"],
        user_id=user_id,
        image_url=data.get("image_url")
    )

    db.session.add(new_memory)
    db.session.commit()
    return jsonify({"message": "Memory created!", "id": new_memory.id}), 201

@memory_bp.route("/<int:memory_id>", methods=["DELETE"])
@jwt_required()
def delete_memory(memory_id):
    user_id = int(get_jwt_identity())
    memory = Memory.query.filter_by(id=memory_id, user_id=user_id).first()

    if not memory:
        return jsonify({"error": "Memory not found"}), 404

    db.session.delete(memory)
    db.session.commit()

    return jsonify({"message": "Memory deleted successfully!", "id": memory_id})

