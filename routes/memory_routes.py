from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import Memory, db
from services.memory_images import (
    memory_file_keys,
    orphaned_file_keys,
    sync_memory_images,
)
from services.uploadthing import delete_files
from utils import clean_image_url

memory_bp = Blueprint("memory", __name__)


def _parse_event_date(value):
    """Accepts an ISO 8601 string (what the frontend has always sent) and
    returns a datetime, or None if it can't be parsed."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


@memory_bp.route("/", methods=["GET"])
@jwt_required()
def list_memories():
    user_id = int(get_jwt_identity())
    memories = Memory.query.filter_by(user_id=user_id).order_by(Memory.event_date.desc()).all()

    result = [
        {
            "id": m.id,
            "title": m.title,
            "content": m.content,
            "event_date": m.event_date.isoformat(),
            "user_id": m.user_id,
            "image": clean_image_url(m.image_url),
        }
        for m in memories
    ]

    return jsonify(result)


@memory_bp.route("/<int:memory_id>", methods=["GET"])
@jwt_required()
def get_unique_memory(memory_id):
    user_id = int(get_jwt_identity())
    memory = Memory.query.filter_by(id=memory_id, user_id=user_id).first()

    if not memory:
        return jsonify({"error": "Memory not found"}), 404

    return jsonify({
        "id": memory.id,
        "title": memory.title,
        "content": memory.content,
        "event_date": memory.event_date.isoformat(),
        "user_id": memory.user_id,
        "image": clean_image_url(memory.image_url),
    })


@memory_bp.route("/<int:memory_id>", methods=["PUT"])
@jwt_required()
def update_memory(memory_id):
    user_id = int(get_jwt_identity())
    memory = Memory.query.filter_by(id=memory_id, user_id=user_id).first()
    if not memory:
        return jsonify({"error": "Memory not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Nenhum dado fornecido"}), 400

    if "title" in data:
        title = (data["title"] or "").strip()
        if not title:
            return jsonify({"error": "title não pode ser vazio"}), 400
        memory.title = title

    if "content" in data:
        memory.content = data["content"]

    if "event_date" in data:
        event_date = _parse_event_date(data["event_date"])
        if event_date is None:
            return jsonify({"error": "event_date inválido, use o formato ISO 8601"}), 400
        memory.event_date = event_date

    if "image_url" in data:
        memory.image_url = data["image_url"]

    orphaned = sync_memory_images(memory)
    db.session.commit()

    # After the commit: an image dropped from the body (or a replaced cover)
    # only stops existing for real once the new content is safely stored.
    delete_files(orphaned)

    return jsonify({
        "message": "Memory updated successfully!",
        "memory": {"id": memory.id}
    })


@memory_bp.route("/", methods=["POST"])
@jwt_required()
def create_memory():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    event_date = _parse_event_date(data.get("event_date"))

    if not title or not data.get("event_date"):
        return jsonify({"error": "Campos obrigatórios: title, event_date"}), 400

    if event_date is None:
        return jsonify({"error": "event_date inválido, use o formato ISO 8601"}), 400

    new_memory = Memory(
        title=title,
        content=data.get("content"),
        event_date=event_date,
        user_id=user_id,
        image_url=data.get("image_url")
    )

    db.session.add(new_memory)
    sync_memory_images(new_memory)
    db.session.commit()
    return jsonify({"message": "Memory created!", "id": new_memory.id}), 201


@memory_bp.route("/<int:memory_id>", methods=["DELETE"])
@jwt_required()
def delete_memory(memory_id):
    user_id = int(get_jwt_identity())
    memory = Memory.query.filter_by(id=memory_id, user_id=user_id).first()

    if not memory:
        return jsonify({"error": "Memory not found"}), 404

    # Read the keys while the rows still exist; the delete cascades them away.
    file_keys = memory_file_keys(memory)

    db.session.delete(memory)
    db.session.flush()

    orphaned = orphaned_file_keys(file_keys)
    db.session.commit()

    delete_files(orphaned)

    return jsonify({"message": "Memory deleted successfully!", "id": memory_id})
