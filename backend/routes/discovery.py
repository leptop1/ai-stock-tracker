from flask import Blueprint, jsonify, request
from services.discovery import discover_ai_stocks, search_stocks

discovery_bp = Blueprint("discovery", __name__)


@discovery_bp.route("/")
def discover():
    results = discover_ai_stocks()
    return jsonify(results)


@discovery_bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    results = search_stocks(q)
    return jsonify(results)
