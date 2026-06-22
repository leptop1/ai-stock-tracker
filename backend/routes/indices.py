from flask import Blueprint, jsonify
import yfinance as yf
import pandas as pd
import numpy as np
import time

indices_bp = Blueprint("indices", __name__)

INDICES = [
    {"symbol": "XU100.IS", "name": "BIST 100", "exchange": "Türkiye"},
    {"symbol": "XU030.IS", "name": "BIST 30", "exchange": "Türkiye"},
    {"symbol": "XBANK.IS", "name": "BIST Bankacılık", "exchange": "Türkiye"},
    {"symbol": "XUSIN.IS", "name": "BIST Sınai", "exchange": "Türkiye"},
    {"symbol": "XUTEK.IS", "name": "BIST Teknoloji", "exchange": "Türkiye"},
    {"symbol": "XGIDA.IS", "name": "BIST Gıda", "exchange": "Türkiye"},
    {"symbol": "XTEKS.IS", "name": "BIST Tekstil", "exchange": "Türkiye"},
    {"symbol": "XKMYA.IS", "name": "BIST Kimya", "exchange": "Türkiye"},
    {"symbol": "XINSA.IS", "name": "BIST İnşaat", "exchange": "Türkiye"},
    {"symbol": "XMADN.IS", "name": "BIST Madencilik", "exchange": "Türkiye"},
    {"symbol": "XHOLD.IS", "name": "BIST Holding", "exchange": "Türkiye"},
    {"symbol": "XTRZM.IS", "name": "BIST Turizm", "exchange": "Türkiye"},
    {"symbol": "XULAS.IS", "name": "BIST Ulaştırma", "exchange": "Türkiye"},
    {"symbol": "XSPOR.IS", "name": "BIST Spor", "exchange": "Türkiye"},
    {"symbol": "XSGRT.IS", "name": "BIST Sigorta", "exchange": "Türkiye"},
    {"symbol": "XGMYO.IS", "name": "BIST GYO", "exchange": "Türkiye"},
    {"symbol": "XILTM.IS", "name": "BIST İletişim", "exchange": "Türkiye"},
    {"symbol": "XTAST.IS", "name": "BIST Taş Toprak", "exchange": "Türkiye"},
    {"symbol": "XTCRT.IS", "name": "BIST Ticaret", "exchange": "Türkiye"},
    {"symbol": "XELKT.IS", "name": "BIST Elektrik", "exchange": "Türkiye"},
    {"symbol": "^GSPC", "name": "S&P 500", "exchange": "ABD"},
    {"symbol": "^IXIC", "name": "Nasdaq 100", "exchange": "ABD"},
    {"symbol": "^DJI", "name": "Dow Jones", "exchange": "ABD"},
    {"symbol": "^GDAXI", "name": "DAX", "exchange": "Almanya"},
    {"symbol": "^FTSE", "name": "FTSE 100", "exchange": "İngiltere"},
    {"symbol": "^N225", "name": "Nikkei 225", "exchange": "Japonya"},
    {"symbol": "^HSI", "name": "Hang Seng", "exchange": "Hong Kong"},
    {"symbol": "GC=F", "name": "Altın (Ons)", "exchange": "Emtia"},
    {"symbol": "BTC-USD", "name": "Bitcoin", "exchange": "Kripto"},
    {"symbol": "EURUSD=X", "name": "EUR/USD", "exchange": "Döviz"},
]

_cache = {}
_cache_ts = {}
CACHE_TTL = 600

def _get_cached(key):
    if key in _cache and time.time() - _cache_ts.get(key, 0) < CACHE_TTL:
        return _cache[key]
    return None

def _set_cached(key, value):
    _cache[key] = value
    _cache_ts[key] = time.time()

@indices_bp.route("")
def get_indices():
    cached = _get_cached("indices")
    if cached:
        return jsonify(cached)

    results = []
    symbols_to_fetch = []
    for idx_def in INDICES:
        cached_sym = _get_cached(f"idx:{idx_def['symbol']}")
        if cached_sym:
            results.append(cached_sym)
        else:
            symbols_to_fetch.append(idx_def)

    consec_fail = 0
    for idx_def in symbols_to_fetch:
        if consec_fail >= 10:
            break
        sym = idx_def["symbol"]
        try:
            t = yf.Ticker(sym)
            df = t.history(period="1mo")
            if df is None or df.empty:
                consec_fail += 1
                continue
            if hasattr(df.index, 'tz_localize'):
                df.index = df.index.tz_localize(None)

            close = df["Close"]
            price = float(close.iloc[-1])
            prev = float(close.iloc[-2]) if len(df) >= 2 else None
            change_pct = round((price - prev) / prev * 100, 2) if prev and prev != 0 else None

            sma_20 = round(float(close.rolling(20).mean().iloc[-1]), 2) if len(df) >= 20 else None
            rsi_val = None
            if len(df) >= 15:
                delta = close.diff()
                gain = delta.where(delta > 0, 0.0).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
                rs = gain / loss.replace(0, np.nan)
                rsi_series = 100 - (100 / (1 + rs))
                rsi_val = round(float(rsi_series.iloc[-1]), 2) if not rsi_series.empty else None

            volume = int(df["Volume"].iloc[-1]) if "Volume" in df.columns and df["Volume"].iloc[-1] > 0 else None
            avg_volume_10 = None
            if volume is not None and len(df) >= 10:
                avg_volume_10 = round(float(df["Volume"].tail(10).mean()), 1)

            closes = [round(float(c), 2) for c in close.tail(24).tolist()]

            entry = {
                "symbol": sym,
                "name": idx_def["name"],
                "exchange": idx_def["exchange"],
                "price": round(price, 2),
                "change_pct": change_pct,
                "sma_20": sma_20,
                "rsi": rsi_val,
                "volume": volume,
                "avg_volume_10": avg_volume_10,
                "sparkline": closes,
            }
            _set_cached(f"idx:{sym}", entry)
            results.append(entry)
            consec_fail = 0
        except Exception:
            consec_fail += 1
            continue

    _set_cached("indices", results)
    return jsonify(results)
