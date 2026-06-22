from flask import Blueprint, request, jsonify
from biscuit_agent import BiscuitAgent

chat_bp = Blueprint("chat", __name__)
_agent = BiscuitAgent()


@chat_bp.route("/message", methods=["POST"])
def message():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    messages = data.get("messages", [])
    context = data.get("context", "")

    if not messages:
        return jsonify({"error": "No messages"}), 400

    try:
        reply = _agent.chat(messages=messages, context=context)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
