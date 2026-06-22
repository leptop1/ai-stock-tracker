import yfinance as yf
import pandas as pd


def _normalize_index(df: pd.DataFrame) -> pd.DataFrame:
    """DatetimeIndex'i tz-naive yap; sıradan Index ise DatetimeIndex'e çevir."""
    if isinstance(df.index, pd.DatetimeIndex):
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
    else:
        try:
            df.index = pd.to_datetime(df.index).tz_localize(None)
        except Exception:
            pass
    return df


def get_viop_history(symbol: str, period: str = "3mo", interval: str = "1d") -> pd.DataFrame:
    t = yf.Ticker(symbol)
    df = t.history(period=period, interval=interval)
    return _normalize_index(df)


def get_viop_info(symbol: str) -> dict:
    """Get instrument info using fast_info to avoid rate limits."""
    t = yf.Ticker(symbol)
    try:
        fi = t.fast_info
        price = getattr(fi, 'last_price', None) or getattr(fi, 'previous_close', None)
        prev = getattr(fi, 'previous_close', None) or price
        currency = getattr(fi, 'currency', 'TRY')
        return {
            "symbol": symbol,
            "name": symbol,
            "price": price,
            "previous_close": prev,
            "currency": currency,
            "volume": getattr(fi, 'three_month_average_volume', None),
            "market_cap": getattr(fi, 'market_cap', None),
            "52w_high": getattr(fi, 'year_high', None),
            "52w_low": getattr(fi, 'year_low', None),
            "exchange": getattr(fi, 'exchange', ''),
        }
    except Exception:
        df = get_viop_history(symbol, period="5d")
        price = float(df["Close"].iloc[-1]) if len(df) > 0 else None
        prev = float(df["Close"].iloc[-2]) if len(df) > 1 else price
        return {
            "symbol": symbol,
            "name": symbol,
            "price": price,
            "previous_close": prev,
            "currency": "TRY",
            "volume": None,
            "market_cap": None,
            "52w_high": None,
            "52w_low": None,
            "exchange": "",
        }


def get_viop_quotes(instruments: list) -> dict:
    """Batch fetch using yf.download — single request, no rate limit issues."""
    if not instruments:
        return {}
    symbols = [i["symbol"] for i in instruments]
    results = {}
    try:
        raw = yf.download(
            symbols,
            period="5d",
            interval="1d",
            group_by="ticker",
            auto_adjust=True,
            progress=False,
            threads=True,
        )
        for item in instruments:
            symbol = item["symbol"]
            try:
                if len(symbols) == 1:
                    df = raw
                else:
                    df = raw[symbol]
                df = _normalize_index(df).dropna(subset=["Close"])
                if len(df) == 0:
                    raise ValueError("no data")
                price = float(df["Close"].iloc[-1])
                prev = float(df["Close"].iloc[-2]) if len(df) > 1 else price
                change_pct = ((price - prev) / prev * 100) if prev else 0
                volume = int(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0
                results[symbol] = {
                    "symbol": symbol,
                    "name": item.get("name", symbol),
                    "category": item.get("category", ""),
                    "currency": item.get("currency", "TRY"),
                    "price": round(price, 4),
                    "previous_close": round(prev, 4),
                    "change_pct": round(change_pct, 2),
                    "volume": volume,
                }
            except Exception:
                results[symbol] = {
                    "symbol": symbol,
                    "name": item.get("name", symbol),
                    "category": item.get("category", ""),
                    "currency": item.get("currency", "TRY"),
                    "price": None,
                    "change_pct": None,
                    "error": True,
                }
    except Exception:
        for item in instruments:
            symbol = item["symbol"]
            results[symbol] = {
                "symbol": symbol,
                "name": item.get("name", symbol),
                "category": item.get("category", ""),
                "currency": item.get("currency", "TRY"),
                "price": None,
                "change_pct": None,
                "error": True,
            }
    return results
