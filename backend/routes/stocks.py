from flask import Blueprint, jsonify
from services.yahoo_finance import get_stock_history as yf_history, get_stock_info as yf_info, get_batch_quotes
from services.bist_data import get_bist_history, get_bist_info, get_bist_price
from services.indicators import calculate_all_indicators
from services.signals import generate_signal
from routes.watchlist import load_watchlist
import time

stocks_bp = Blueprint("stocks", __name__)

_cache = {}
_cache_ts = {}
CACHE_TTL = 300  # 5 minutes


def _get_cached(key):
    if key in _cache and time.time() - _cache_ts.get(key, 0) < CACHE_TTL:
        return _cache[key]
    return None


def _set_cached(key, value):
    _cache[key] = value
    _cache_ts[key] = time.time()


def _is_bist(ticker: str) -> bool:
    return ticker.upper().endswith(".IS")


@stocks_bp.route("/summary")
def summary():
    watchlist = load_watchlist()
    tickers = [w["ticker"] for w in watchlist]
    cache_key = "summary:" + ",".join(sorted(tickers))
    cached = _get_cached(cache_key)
    if cached:
        return jsonify(cached)

    ticker_map = {w["ticker"]: w for w in watchlist}
    bist_tickers = [t for t in tickers if _is_bist(t)]
    non_bist = [t for t in tickers if not _is_bist(t)]
    bist_prices = get_bist_prices_batch(bist_tickers) if len(bist_tickers) <= 50 else {}

    results = []
    for ticker in tickers:
        item = ticker_map[ticker]
        price = change_pct = volume = rsi_val = None
        signal_data = {"signal": "N/A", "score": 0, "confidence": "LOW", "breakdown": {}}

        if _is_bist(ticker):
            pd_ = bist_prices.get(ticker)
            if pd_ and pd_.get("price") is not None:
                price = pd_["price"]
                volume = pd_.get("volume")
        else:
            try:
                df = yf_history(ticker, period="3mo")
                df = df.dropna(subset=["Close"])
                if len(df) >= 2:
                    price = round(float(df["Close"].iloc[-1]), 2)
                    prev = round(float(df["Close"].iloc[-2]), 2)
                    change_pct = round((price - prev) / prev * 100, 2) if prev else 0
                    volume = int(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0
                if len(df) >= 15:
                    indicators = calculate_all_indicators(df)
                    signal_data = generate_signal(indicators["latest"])
                    rsi_val = indicators["latest"].get("rsi")
            except Exception:
                pass

        results.append({
            "ticker": ticker,
            "name": item.get("name", ticker),
            "category": item.get("category", ""),
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


@stocks_bp.route("/<ticker>")
def stock_detail(ticker):
    ticker = ticker.upper()
    cache_key = f"detail:{ticker}"
    cached = _get_cached(cache_key)
    if cached:
        return jsonify(cached)
    try:
        if _is_bist(ticker):
            info = get_bist_info(ticker) or {}
            df = get_bist_history(ticker, period="6mo")
        else:
            info = yf_info(ticker)
            df = yf_history(ticker, period="6mo")
    except Exception:
        info = {}
        df = None

    indicators = calculate_all_indicators(df) if df is not None and not df.empty else {"latest": {}}
    signal = generate_signal(indicators["latest"])
    result = {**info, "indicators": indicators, "signal": signal}
    _set_cached(cache_key, result)
    return jsonify(result)


@stocks_bp.route("/<ticker>/history")
def stock_history(ticker):
    ticker = ticker.upper()
    try:
        df = get_bist_history(ticker, period="6mo") if _is_bist(ticker) else yf_history(ticker, period="6mo")
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


@stocks_bp.route("/<ticker>/signal")
def stock_signal(ticker):
    ticker = ticker.upper()
    try:
        df = get_bist_history(ticker, period="3mo") if _is_bist(ticker) else yf_history(ticker, period="3mo")
    except Exception:
        df = None
    indicators = calculate_all_indicators(df) if df is not None and not df.empty else {"latest": {}}
    signal = generate_signal(indicators["latest"])
    return jsonify(signal)
