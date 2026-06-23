import json
import os
import time
from flask import Blueprint, jsonify, request
from services.bist_data import get_bist_info, get_bist_price, get_bist_prices_batch, get_cached_ohlc_data
from services.signals import generate_signal
from services.indicators_np import compute_all_indicators

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
        change_pct = None
        if p and p.get("price") is not None and p.get("previous_close") is not None and p["previous_close"]:
            change_pct = round((p["price"] - p["previous_close"]) / p["previous_close"] * 100, 2)
        rsi_val = None
        avg_vol_10 = None
        sma_20_val = None
        ohlc = get_cached_ohlc_data(i["symbol"])
        if ohlc and len(ohlc.get("close", [])) > 14:
            closes = ohlc["close"]
            gains, losses = 0.0, 0.0
            n = min(15, len(closes))
            for j in range(len(closes) - n, len(closes) - 1):
                diff = closes[j + 1] - closes[j]
                if diff > 0:
                    gains += diff
                else:
                    losses -= diff
            if losses > 0:
                rs = (gains / (n - 1)) / (losses / (n - 1))
                rsi_val = round(100 - (100 / (1 + rs)), 1)
            else:
                rsi_val = round(100.0 if gains > 0 else 50.0, 1)
            vols = ohlc.get("volume", [])
            if len(vols) >= 10:
                avg_vol_10 = int(sum(vols[-10:]) / 10)
            if len(closes) >= 20:
                sma_20_val = round(sum(closes[-20:]) / 20, 2)
        out.append({
            "symbol": i["symbol"],
            "name": i.get("name", i["symbol"]),
            "category": i.get("category", ""),
            "price": p.get("price") if p else None,
            "change_pct": change_pct,
            "volume": p.get("volume") if p else None,
            "signal": "N/A", "score": 0, "confidence": "LOW",
            "rsi": rsi_val, "sma_20": sma_20_val, "avg_volume_10": avg_vol_10,
        })
    return jsonify(out)


@bist_bp.route("/_ping")
def ping():
    return jsonify({"ok": True, "engine": "flask", "time": time.time()})


@bist_bp.route("/_dt")
def diag_endpoint():
    return jsonify({"ok": True, "dt": "clean"})

@bist_bp.route("/<path:symbol>")
def instrument_detail(symbol):
    try:
        cache_key = f"bist:detail:{symbol}"
        cached = _get_cached(cache_key)
        if cached:
            return jsonify(cached)
        info = get_bist_info(symbol) or {}
        ohlc = get_cached_ohlc_data(symbol)
        indicators = {"latest": {}}
        if ohlc and len(ohlc.get("close", [])) > 10:
            try:
                indicators = compute_all_indicators(
                    ohlc.get("dates", []),
                    ohlc.get("open", []),
                    ohlc.get("high", ohlc.get("close", [])),
                    ohlc.get("low", ohlc.get("close", [])),
                    ohlc["close"],
                    ohlc.get("volume", [0] * len(ohlc["close"])),
                )
            except BaseException:
                indicators = {"latest": {}}
        signal = generate_signal(indicators.get("latest", {}))
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
        data = get_cached_ohlc_data(symbol)
        if data:
            return jsonify({"dates": data["dates"], "open": data["open"],
                            "high": data["high"], "low": data["low"],
                            "close": data["close"], "volume": data["volume"]})
    except Exception:
        pass
    return jsonify({"dates": [], "open": [], "high": [], "low": [], "close": [], "volume": []})


@bist_bp.route("/<path:symbol>/signal")
def instrument_signal(symbol):
    ohlc = get_cached_ohlc_data(symbol)
    latest = {}
    if ohlc and len(ohlc.get("close", [])) > 10:
        try:
            ind = compute_all_indicators(
                ohlc.get("dates", []),
                ohlc.get("open", []),
                ohlc.get("high", ohlc.get("close", [])),
                ohlc.get("low", ohlc.get("close", [])),
                ohlc["close"],
                ohlc.get("volume", [0] * len(ohlc["close"])),
            )
            latest = ind.get("latest", {})
        except BaseException:
            latest = {}
    signal = generate_signal(latest)
    return jsonify(signal)
