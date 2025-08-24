from flask import Blueprint, request, jsonify
from models import db, Memory

memory_bp = Blueprint("memory", __name__)

@memory_bp.route("/", methods=["GET"])
def list_memories():
  memories = Memory.query.order_by(Memory.event_date.desc()).all()
  return jsonify([
    {
      "id": m.id,
      "title": m.title,
      "content": m.content,
      "event_date": m.event_date.isoformat(),
      "user_id": m.user_id
    } for m in memories
  ])

@memory_bp.route("/<int:memory_id>", methods=["GET"])
def get_unique_memory(memory_id):
  memory = Memory.query.get_or_404(memory_id)
  return jsonify({
    "id": memory.id,
    "title": memory.title,
    "content": memory.content,
    "event_date": memory.event_date.isoformat(),
    "user_id": memory.user_id
  })

@memory_bp.route("/", methods=["POST"])
def create_memory():
  data = request.json
  new_memory = Memory(
    title=data["title"],
    content=data.get("content"),
    event_date=data["event_date"],
    user_id=data["user_id"]
  )
  db.session.add(new_memory)
  db.session.commit()
  return jsonify({"message": "Memory created!", "id": new_memory.id}), 201
