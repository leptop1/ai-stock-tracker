import json
import os
import time
from flask import Blueprint, jsonify, request
from services.bist_data import get_bist_history, get_bist_info, get_bist_price, get_bist_prices_batch
from services.indicators import calculate_all_indicators
from services.signals import generate_signal

bist_bp = Blueprint("bist", __name__)

DEFAULT_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "default_bist.json")
WATCHLIST_FILE = os.path.join(os.path.dirname(__file__), "..", "bist_watchlist.json")
DATA_WATCHLIST_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "bist_watchlist.json")

_cache = {}
_cache_ts = {}
CACHE_TTL = 300
PRICE_CACHE_TTL = 30


def _get_cached(key):
    if key in _cache and time.time() - _cache_ts.get(key, 0) < CACHE_TTL:
        return _cache[key]
    return None


def _set_cached(key, value):
    _cache[key] = value
    _cache_ts[key] = time.time()


def load_default_bist_instruments() -> list:
    with open(DEFAULT_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("instruments", [])


def load_bist_watchlist() -> list:
    for path in (WATCHLIST_FILE, DATA_WATCHLIST_FILE, DEFAULT_FILE):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f).get("instruments", [])
    return []


def save_bist_watchlist(instruments: list):
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump({"instruments": instruments}, f, ensure_ascii=False, indent=2)


@bist_bp.route("/all")
def all_instruments():
    q = request.args.get("q", "").strip().lower()
    instruments = load_default_bist_instruments()
    if q:
        instruments = [i for i in instruments
                       if q in i["symbol"].lower() or q in i["name"].lower()]
    return jsonify(instruments)


@bist_bp.route("/watchlist")
def get_watchlist():
    return jsonify(load_bist_watchlist())


@bist_bp.route("/watchlist", methods=["POST"])
def add_to_watchlist():
    data = request.json
    symbol = data.get("symbol", "").strip().upper()
    if not symbol.endswith(".IS"):
        symbol = symbol + ".IS"
    name = data.get("name", symbol)
    category = data.get("category", "Diğer")
    if not symbol:
        return jsonify({"error": "symbol required"}), 400
    instruments = load_bist_watchlist()
    if any(i["symbol"] == symbol for i in instruments):
        return jsonify({"error": "already in watchlist"}), 409
    instruments.append({"symbol": symbol, "name": name, "category": category})
    save_bist_watchlist(instruments)
    return jsonify({"ok": True, "symbol": symbol}), 201


@bist_bp.route("/watchlist/<path:symbol>", methods=["DELETE"])
def remove_from_watchlist(symbol):
    instruments = load_bist_watchlist()
    new_list = [i for i in instruments if i["symbol"] != symbol]
    if len(new_list) == len(instruments):
        return jsonify({"error": "not found"}), 404
    save_bist_watchlist(new_list)
    return jsonify({"ok": True})


@bist_bp.route("/watchlist/reset", methods=["PUT"])
def reset_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        os.remove(WATCHLIST_FILE)
    return jsonify({"ok": True, "instruments": load_bist_watchlist()})


def _fetch_prices_batch(symbols: list[str]) -> dict:
    now = time.time()
    results = {}
    if len(symbols) > 50:
        return results
    uncached = []
    for sym in symbols:
        cache_key = f"price:{sym}"
        if cache_key in _cache and now - _cache_ts.get(cache_key, 0) < PRICE_CACHE_TTL:
            results[sym] = _cache[cache_key]
        else:
            uncached.append(sym)
    if uncached:
        fresh = get_bist_prices_batch(uncached)
        for sym, p in fresh.items():
            if p:
                _cache[f"price:{sym}"] = p
                _cache_ts[f"price:{sym}"] = now
                results[sym] = p
    return results


@bist_bp.route("/summary")
def summary():
    instruments = load_bist_watchlist()
    prices = _fetch_prices_batch([i["symbol"] for i in instruments])
    out = []
    for i in instruments:
        p = prices.get(i["symbol"])
        out.append({
            "symbol": i["symbol"],
            "name": i.get("name", i["symbol"]),
            "category": i.get("category", ""),
            "price": p.get("price") if p else None,
            "change_pct": None,
            "volume": p.get("volume") if p else None,
            "signal": "N/A", "score": 0, "confidence": "LOW",
            "rsi": None, "sma_20": None, "avg_volume_10": None,
        })
    return jsonify(out)


@bist_bp.route("/_ping")
def ping():
    return jsonify({"ok": True, "engine": "flask", "time": time.time()})


@bist_bp.route("/_dt")
def diag_endpoint():
    result = {"ok": True}
    # Step 1: get_bist_price
    try:
        result["s1"] = "get_bist_price"
        p = get_bist_price("GARAN.IS")
        result["p_ok"] = p is not None
    except BaseException as e:
        result["s1_err"] = f"{type(e).__name__}: {e}"
    # Step 2: get_bist_info
    try:
        result["s2"] = "get_bist_info"
        inf = get_bist_info("GARAN.IS")
        result["i_ok"] = inf is not None and inf.get("price") is not None
    except BaseException as e:
        result["s2_err"] = f"{type(e).__name__}: {e}"
    # Step 3: get_bist_history
    try:
        result["s3"] = "get_bist_history"
        h = get_bist_history("GARAN.IS", period="6mo")
        result["h_ok"] = h is not None and not h.empty
    except BaseException as e:
        result["s3_err"] = f"{type(e).__name__}: {e}"
    # Step 4: calculate_all_indicators
    try:
        result["s4"] = "calc_indicators"
        h = get_bist_history("GARAN.IS", period="6mo")
        if h is not None and not h.empty:
            ind = calculate_all_indicators(h)
            result["ind_ok"] = "latest" in ind
    except BaseException as e:
        result["s4_err"] = f"{type(e).__name__}: {e}"
    # Step 5: generate_signal
    try:
        result["s5"] = "gen_signal"
        ind = {"latest": {}}
        sig = generate_signal(ind["latest"])
        result["sig_ok"] = "signal" in sig
    except BaseException as e:
        result["s5_err"] = f"{type(e).__name__}: {e}"
    return jsonify(result)


@bist_bp.route("/<path:symbol>")
def instrument_detail(symbol):
    try:
        cache_key = f"bist:detail:{symbol}"
        cached = _get_cached(cache_key)
        if cached:
            return jsonify(cached)
        try:
            info = get_bist_info(symbol) or {}
            df = get_bist_history(symbol, period="6mo")
        except BaseException:
            info = {}
            df = None

        indicators = calculate_all_indicators(df) if df is not None and not df.empty else {"latest": {}}
        signal = generate_signal(indicators["latest"])
        wl = load_bist_watchlist()
        meta = next((i for i in wl if i["symbol"] == symbol), {})
        result = {
            **info,
            "symbol": symbol,
            "name": meta.get("name", info.get("name", symbol)),
            "category": meta.get("category", ""),
            "indicators": indicators,
            "signal": signal,
        }
        _set_cached(cache_key, result)
        return jsonify(result)
    except BaseException:
        return jsonify({"symbol": symbol, "price": None, "error": "exception"}), 500


@bist_bp.route("/<path:symbol>/history")
def instrument_history(symbol):
    try:
        df = get_bist_history(symbol, period="6mo")
    except Exception:
        df = None
    if df is None or df.empty:
        return jsonify({"dates": [], "open": [], "high": [], "low": [], "close": [], "volume": []})
    dates = [str(d.date()) for d in df.index]
    return jsonify({
        "dates": dates,
        "open": [round(float(v), 2) for v in df["Open"]],
        "high": [round(float(v), 2) for v in df["High"]],
        "low": [round(float(v), 2) for v in df["Low"]],
        "close": [round(float(v), 2) for v in df["Close"]],
        "volume": [int(v) for v in df["Volume"]],
    })


@bist_bp.route("/<path:symbol>/signal")
def instrument_signal(symbol):
    try:
        df = get_bist_history(symbol, period="3mo")
    except Exception:
        df = None
    indicators = calculate_all_indicators(df) if df is not None and not df.empty else {"latest": {}}
    signal = generate_signal(indicators["latest"])
    return jsonify(signal)
