import json
import os
import time
from flask import Blueprint, jsonify, request
from services.viop_data import get_viop_history, get_viop_info
from services.indicators import calculate_all_indicators
from services.signals import generate_signal

viop_bp = Blueprint("viop", __name__)

DEFAULT_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "default_viop.json")
WATCHLIST_FILE = os.path.join(os.path.dirname(__file__), "..", "viop_watchlist.json")

_cache = {}
_cache_ts = {}
CACHE_TTL = 300
HEDGE_CACHE_TTL = 600


def _get_cached(key):
    if key in _cache and time.time() - _cache_ts.get(key, 0) < CACHE_TTL:
        return _cache[key]
    return None


def _get_cached_ttl(key, ttl):
    if key in _cache and time.time() - _cache_ts.get(key, 0) < ttl:
        return _cache[key]
    return None


def _set_cached(key, value):
    _cache[key] = value
    _cache_ts[key] = time.time()


def load_viop_watchlist() -> list:
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r") as f:
            return json.load(f).get("instruments", [])
    with open(DEFAULT_FILE, "r") as f:
        return json.load(f).get("instruments", [])


def save_viop_watchlist(instruments: list):
    with open(WATCHLIST_FILE, "w") as f:
        json.dump({"instruments": instruments}, f, indent=2)


@viop_bp.route("/watchlist")
def get_watchlist():
    return jsonify(load_viop_watchlist())


@viop_bp.route("/watchlist", methods=["POST"])
def add_to_watchlist():
    data = request.json
    symbol = data.get("symbol", "").strip()
    name = data.get("name", symbol)
    category = data.get("category", "Di\u011fer")
    currency = data.get("currency", "TRY")
    if not symbol:
        return jsonify({"error": "symbol required"}), 400
    instruments = load_viop_watchlist()
    if any(i["symbol"] == symbol for i in instruments):
        return jsonify({"error": "already in watchlist"}), 409
    instruments.append({"symbol": symbol, "name": name, "category": category, "currency": currency})
    save_viop_watchlist(instruments)
    return jsonify({"ok": True, "symbol": symbol}), 201


@viop_bp.route("/watchlist/<path:symbol>", methods=["DELETE"])
def remove_from_watchlist(symbol):
    instruments = load_viop_watchlist()
    new_list = [i for i in instruments if i["symbol"] != symbol]
    if len(new_list) == len(instruments):
        return jsonify({"error": "not found"}), 404
    save_viop_watchlist(new_list)
    return jsonify({"ok": True})


@viop_bp.route("/watchlist/reset", methods=["PUT"])
def reset_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        os.remove(WATCHLIST_FILE)
    return jsonify({"ok": True, "instruments": load_viop_watchlist()})


@viop_bp.route("/summary")
def summary():
    instruments = load_viop_watchlist()
    cache_key = "viop:summary:" + ",".join(i["symbol"] for i in instruments)
    cached = _get_cached(cache_key)
    if cached:
        return jsonify(cached)

    results = []
    for item in instruments:
        symbol = item["symbol"]
        price = None
        change_pct = None
        volume = None
        signal_data = {"signal": "N/A", "score": 0, "confidence": "LOW", "breakdown": {}}
        rsi_val = None
        try:
            df = get_viop_history(symbol, period="3mo")
            df = df.dropna(subset=["Close"])
            if len(df) >= 2:
                price = round(float(df["Close"].iloc[-1]), 4)
                prev = float(df["Close"].iloc[-2])
                change_pct = round((price - prev) / prev * 100, 2) if prev else 0
                volume = int(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0
            if len(df) >= 15:
                indicators = calculate_all_indicators(df)
                signal_data = generate_signal(indicators["latest"])
                rsi_val = indicators["latest"].get("rsi")
        except Exception:
            pass
        results.append({
            "symbol": symbol,
            "name": item.get("name", symbol),
            "category": item.get("category", ""),
            "currency": item.get("currency", "TRY"),
            "price": price,
            "change_pct": change_pct,
            "volume": volume,
            "signal": signal_data["signal"],
            "score": signal_data["score"],
            "confidence": signal_data["confidence"],
            "rsi": rsi_val,
        })
    _set_cached(cache_key, results)
    return jsonify(results)


@viop_bp.route("/hedge-signal")
def instrument_hedge_signal():
    """
    Uzman Claude agent ile opsiyon hedge analizi.
    URL: GET /api/viop/hedge-signal?symbol=XU030.IS
    """
    symbol = request.args.get("symbol", "").strip()
    if not symbol:
        return jsonify({"error": "symbol required"}), 400

    cache_key = f"viop:hedge:{symbol}"
    cached = _get_cached_ttl(cache_key, HEDGE_CACHE_TTL)
    if cached:
        return jsonify(cached)

    try:
        from services.hedge_agent import analyze_hedge

        df = get_viop_history(symbol, period="3mo")
        df = df.dropna(subset=["Close"])
        price = None
        change_pct = None
        rsi_val = None
        signal = "N/A"
        score = 0.0

        if len(df) >= 2:
            price = round(float(df["Close"].iloc[-1]), 4)
            prev = float(df["Close"].iloc[-2])
            change_pct = round((price - prev) / prev * 100, 2) if prev else 0

        if len(df) >= 15:
            indicators = calculate_all_indicators(df)
            signal_data = generate_signal(indicators["latest"])
            rsi_val = indicators["latest"].get("rsi")
            signal = signal_data["signal"]
            score = signal_data["score"]

        wl = load_viop_watchlist()
        meta = next((i for i in wl if i["symbol"] == symbol), {})
        name = meta.get("name", symbol)
        category = meta.get("category", "")

        result = analyze_hedge(
            symbol=symbol,
            name=name,
            category=category,
            price=price,
            change_pct=change_pct,
            rsi=rsi_val,
            signal=signal,
            score=score,
        )
        _set_cached(cache_key, result)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "hedge_signal": "N\u00d6TR",
            "confidence": "D\u00dc\u015e\u00dcK",
            "score": 0.0,
            "reasoning": str(e),
            "key_factors": [],
        }), 500


@viop_bp.route("/<path:symbol>/history")
def instrument_history(symbol):
    try:
        df = get_viop_history(symbol, period="6mo")
        dates = [str(d.date()) for d in df.index]
        return jsonify({
            "dates": dates,
            "open": [round(float(v), 4) for v in df["Open"]],
            "high": [round(float(v), 4) for v in df["High"]],
            "low": [round(float(v), 4) for v in df["Low"]],
            "close": [round(float(v), 4) for v in df["Close"]],
            "volume": [int(v) for v in df["Volume"]],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@viop_bp.route("/<path:symbol>/signal")
def instrument_signal(symbol):
    try:
        df = get_viop_history(symbol, period="3mo")
        indicators = calculate_all_indicators(df)
        signal = generate_signal(indicators["latest"])
        return jsonify(signal)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@viop_bp.route("/<path:symbol>")
def instrument_detail(symbol):
    cache_key = f"viop:detail:{symbol}"
    cached = _get_cached(cache_key)
    if cached:
        return jsonify(cached)
    try:
        info = get_viop_info(symbol)
        df = get_viop_history(symbol, period="6mo")
        indicators = calculate_all_indicators(df)
        signal = generate_signal(indicators["latest"])
        wl = load_viop_watchlist()
        meta = next((i for i in wl if i["symbol"] == symbol), {})
        result = {**info, "category": meta.get("category", ""), "indicators": indicators, "signal": signal}
        _set_cached(cache_key, result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
