import json
import os
from flask import Blueprint, jsonify, request

watchlist_bp = Blueprint("watchlist", __name__)

WATCHLIST_FILE = os.path.join(os.path.dirname(__file__), "..", "watchlist.json")
DEFAULT_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "default_watchlist.json")


def load_watchlist() -> list:
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r") as f:
            return json.load(f).get("tickers", [])
    with open(DEFAULT_FILE, "r") as f:
        return json.load(f).get("tickers", [])


def save_watchlist(tickers: list):
    with open(WATCHLIST_FILE, "w") as f:
        json.dump({"tickers": tickers}, f, indent=2)


@watchlist_bp.route("/")
def get_watchlist():
    return jsonify(load_watchlist())


@watchlist_bp.route("/", methods=["POST"])
def add_to_watchlist():
    data = request.json
    ticker = data.get("ticker", "").upper().strip()
    name = data.get("name", ticker)
    category = data.get("category", "")
    if not ticker:
        return jsonify({"error": "ticker required"}), 400
    tickers = load_watchlist()
    if any(t["ticker"] == ticker for t in tickers):
        return jsonify({"error": "already in watchlist"}), 409
    tickers.append({"ticker": ticker, "name": name, "category": category})
    save_watchlist(tickers)
    return jsonify({"ok": True, "ticker": ticker}), 201


@watchlist_bp.route("/<ticker>", methods=["DELETE"])
def remove_from_watchlist(ticker):
    ticker = ticker.upper()
    tickers = load_watchlist()
    new_list = [t for t in tickers if t["ticker"] != ticker]
    if len(new_list) == len(tickers):
        return jsonify({"error": "not found"}), 404
    save_watchlist(new_list)
    return jsonify({"ok": True})


@watchlist_bp.route("/reset", methods=["PUT"])
def reset_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        os.remove(WATCHLIST_FILE)
    return jsonify({"ok": True, "tickers": load_watchlist()})
