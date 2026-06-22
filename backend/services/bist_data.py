import yfinance as yf
import pandas as pd
import requests
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

_YSESSION = requests.Session()
_YSESSION.headers.update({"User-Agent": "Mozilla/5.0"})
_YSESSION.timeout = 10

_BQ_SESSION = requests.Session()
_BQ_BASE = "https://biquote.io"
_BQ_TIMEOUT = 3

_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "bist_cache")
os.makedirs(_CACHE_DIR, exist_ok=True)


def _strip_is(symbol: str) -> str:
    return symbol.replace(".IS", "")


def _cache_path(symbol: str) -> str:
    return os.path.join(_CACHE_DIR, f"{_strip_is(symbol)}.json")


def _read_cache(symbol: str) -> dict | None:
    path = _cache_path(symbol)
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _write_cache(symbol: str, data: dict):
    path = _cache_path(symbol)
    tmp = path + ".tmp"
    try:
        with open(tmp, "w") as f:
            json.dump(data, f)
        os.replace(tmp, path)
    except Exception:
        try:
            os.remove(tmp)
        except Exception:
            pass


def get_bist_price(symbol: str) -> dict | None:
    name = _strip_is(symbol)
    try:
        r = _BQ_SESSION.get(f"{_BQ_BASE}/api/{name}", timeout=_BQ_TIMEOUT)
        if r.status_code == 200:
            d = r.json()
            result = {
                "symbol": symbol,
                "price": d.get("last"),
                "previous_close": d.get("prev", d.get("last")),
                "volume": d.get("volume"),
                "bid": d.get("bid"),
                "ask": d.get("ask"),
                "time": d.get("time"),
                "source": "biquote",
            }
            _write_cache(symbol, {"tick": result, "updated": time.time()})
            return result
    except Exception:
        pass
    cached = _read_cache(symbol)
    if cached and "tick" in cached and isinstance(cached["tick"], dict):
        tick = cached["tick"]
        tick["source"] = "cache"
        return tick
    if cached and "ohlc_bars" in cached and cached["ohlc_bars"]:
        bars = cached["ohlc_bars"]
        last = bars[-1]
        prev = bars[-2]["close"] if len(bars) > 1 else last["close"]
        price = last["close"]
        if price is not None:
            return {
                "symbol": symbol,
                "price": price,
                "previous_close": prev,
                "volume": last.get("tickVolume"),
                "source": "ohlc_cache",
            }
    return None


def get_bist_history(symbol: str, period: str = "3mo", interval: str = "1d") -> pd.DataFrame:
    cached = _read_cache(symbol)
    if cached and "ohlc_bars" in cached and cached["ohlc_bars"]:
        df = _bars_to_df(cached["ohlc_bars"])
        if df is not None and not df.empty:
            return df

    try:
        df = _biquote_ohlc(_strip_is(symbol))
        if df is not None and not df.empty:
            _cache_biquote_ohlc(_strip_is(symbol), df)
            return df
    except Exception:
        pass

    try:
        t = yf.Ticker(symbol, session=_YSESSION)
        df = t.history(period=period, interval=interval)
        if df is not None and not df.empty:
            df.index = df.index.tz_localize(None)
            _cache_biquote_ohlc(_strip_is(symbol), df)
            return df
    except Exception:
        pass

    return pd.DataFrame()


def _biquote_ohlc(name: str) -> pd.DataFrame | None:
    r = _BQ_SESSION.get(f"{_BQ_BASE}/api/{name}/ohlc?interval=1d&limit=200", timeout=10)
    if r.status_code != 200:
        return None
    data = r.json()
    bars = data.get("bars", [])
    if not bars:
        return None
    closed = [b for b in bars if b.get("isOpen") is False]
    if not closed:
        return None
    df = pd.DataFrame(closed)
    df["openTime"] = pd.to_datetime(df["openTime"])
    df = df.set_index("openTime").sort_index()
    df.index.name = None
    return pd.DataFrame({
        "Open": df["open"].astype(float),
        "High": df["high"].astype(float),
        "Low": df["low"].astype(float),
        "Close": df["close"].astype(float),
        "Volume": df["tickVolume"].astype(int),
    })


def _cache_biquote_ohlc(name: str, df: pd.DataFrame):
    try:
        bars = []
        for idx, row in df.iterrows():
            bars.append({
                "openTime": idx.isoformat(),
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
                "tickVolume": int(row.get("Volume", 0)),
                "isOpen": False,
            })
        cached = _read_cache(name + ".IS") or {}
        cached["ohlc_bars"] = bars
        _write_cache(name + ".IS", cached)
    except Exception:
        pass


def _bars_to_df(bars: list) -> pd.DataFrame | None:
    if not bars:
        return None
    df = pd.DataFrame(bars)
    df["openTime"] = pd.to_datetime(df["openTime"])
    df = df.set_index("openTime").sort_index()
    df.index.name = None
    return pd.DataFrame({
        "Open": df["open"].astype(float),
        "High": df["high"].astype(float),
        "Low": df["low"].astype(float),
        "Close": df["close"].astype(float),
        "Volume": df["tickVolume"].astype(int),
    })


def get_bist_prices_batch(symbols: list[str], max_workers: int = 20) -> dict[str, dict | None]:
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        fut_map = {ex.submit(get_bist_price, s): s for s in symbols}
        for f in as_completed(fut_map, timeout=30):
            sym = fut_map[f]
            try:
                r = f.result()
                if r:
                    results[sym] = r
            except Exception:
                pass
    for s in symbols:
        if s not in results:
            c = _read_cache(s)
            if c and "tick" in c:
                results[s] = c["tick"]
    return results


def get_bist_info(symbol: str) -> dict:
    price_data = get_bist_price(symbol)
    if price_data and price_data.get("price") is not None:
        return {
            "symbol": symbol,
            "name": symbol,
            "price": price_data["price"],
            "previous_close": price_data.get("previous_close", price_data["price"]),
            "currency": "TRY",
            "volume": price_data.get("volume"),
            "market_cap": None,
            "52w_high": None,
            "52w_low": None,
            "exchange": "IST",
        }

    try:
        t = yf.Ticker(symbol, session=_YSESSION)
        fi = t.fast_info
        price = getattr(fi, 'last_price', None) or getattr(fi, 'previous_close', None)
        prev = getattr(fi, 'previous_close', None) or price
        return {
            "symbol": symbol, "name": symbol,
            "price": price, "previous_close": prev,
            "currency": "TRY",
            "volume": getattr(fi, 'three_month_average_volume', None),
            "market_cap": getattr(fi, 'market_cap', None),
            "52w_high": getattr(fi, 'year_high', None),
            "52w_low": getattr(fi, 'year_low', None),
            "exchange": getattr(fi, 'exchange', 'IST'),
        }
    except Exception:
        pass

    df = get_bist_history(symbol, period="5d")
    price = float(df["Close"].iloc[-1]) if len(df) > 0 else None
    prev = float(df["Close"].iloc[-2]) if len(df) > 1 else price
    return {
        "symbol": symbol, "name": symbol,
        "price": price, "previous_close": prev,
        "currency": "TRY", "volume": None,
        "market_cap": None, "52w_high": None, "52w_low": None,
        "exchange": "IST",
    }
