import yfinance as yf
import pandas as pd


def get_stock_history(ticker: str, period: str = "3mo", interval: str = "1d") -> pd.DataFrame:
    t = yf.Ticker(ticker)
    df = t.history(period=period, interval=interval)
    df.index = df.index.tz_localize(None)
    return df


def get_stock_info(ticker: str) -> dict:
    """Get stock info using fast_info + history to avoid rate limits."""
    t = yf.Ticker(ticker)
    try:
        fi = t.fast_info
        price = getattr(fi, 'last_price', None) or getattr(fi, 'previous_close', None)
        prev = getattr(fi, 'previous_close', None) or price
        name = ticker
        try:
            name = t.info.get("longName") or t.info.get("shortName") or ticker
        except Exception:
            pass
        return {
            "ticker": ticker,
            "name": name,
            "sector": "",
            "industry": "",
            "exchange": getattr(fi, 'exchange', ''),
            "market_cap": getattr(fi, 'market_cap', None),
            "price": price,
            "previous_close": prev,
            "volume": getattr(fi, 'three_month_average_volume', None),
            "avg_volume": getattr(fi, 'three_month_average_volume', None),
            "52w_high": getattr(fi, 'year_high', None),
            "52w_low": getattr(fi, 'year_low', None),
            "pe_ratio": None,
            "description": "",
        }
    except Exception:
        # Fallback: derive from history
        df = get_stock_history(ticker, period="5d")
        price = float(df["Close"].iloc[-1]) if len(df) > 0 else None
        prev = float(df["Close"].iloc[-2]) if len(df) > 1 else price
        return {
            "ticker": ticker,
            "name": ticker,
            "sector": "", "industry": "", "exchange": "",
            "market_cap": None,
            "price": price,
            "previous_close": prev,
            "volume": int(df["Volume"].iloc[-1]) if len(df) > 0 else None,
            "avg_volume": None,
            "52w_high": None, "52w_low": None,
            "pe_ratio": None, "description": "",
        }


def get_batch_quotes(tickers: list) -> dict:
    """Batch fetch using yf.download — single request, no rate limit issues."""
    if not tickers:
        return {}
    results = {}
    try:
        # Download last 5 days for all tickers at once
        raw = yf.download(
            tickers,
            period="5d",
            interval="1d",
            group_by="ticker",
            auto_adjust=True,
            progress=False,
            threads=True,
        )
        for ticker in tickers:
            try:
                if len(tickers) == 1:
                    df = raw
                else:
                    df = raw[ticker]
                df = df.dropna(subset=["Close"])
                if len(df) == 0:
                    raise ValueError("no data")
                price = float(df["Close"].iloc[-1])
                prev = float(df["Close"].iloc[-2]) if len(df) > 1 else price
                change_pct = ((price - prev) / prev * 100) if prev else 0
                volume = int(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0
                results[ticker] = {
                    "ticker": ticker,
                    "name": ticker,
                    "price": round(price, 2),
                    "previous_close": round(prev, 2),
                    "change_pct": round(change_pct, 2),
                    "volume": volume,
                }
            except Exception:
                results[ticker] = {"ticker": ticker, "price": None, "change_pct": None, "error": True}
    except Exception:
        for ticker in tickers:
            results[ticker] = {"ticker": ticker, "price": None, "change_pct": None, "error": True}
    return results


def get_news(ticker: str) -> list:
    t = yf.Ticker(ticker)
    try:
        news = t.news or []
    except Exception:
        return []
    result = []
    for item in news[:10]:
        # New yfinance structure: data is nested under item['content']
        content = item.get('content') or item
        title = content.get('title')
        summary = content.get('summary', '')
        url = (
            (content.get('canonicalUrl') or {}).get('url')
            or (content.get('clickThroughUrl') or {}).get('url')
            or content.get('link')
            or item.get('link')
        )
        publisher = (content.get('provider') or {}).get('displayName') or content.get('publisher')
        pub_date = content.get('pubDate') or content.get('providerPublishTime') or item.get('providerPublishTime')
        # Normalize to Unix timestamp
        if pub_date and isinstance(pub_date, str):
            try:
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                pub_date = int(dt.timestamp())
            except Exception:
                pub_date = None
        thumbnail = None
        thumb = content.get('thumbnail') or item.get('thumbnail')
        if thumb and thumb.get('resolutions'):
            thumbnail = thumb['resolutions'][0].get('url')
        if not title:
            continue
        result.append({
            "title": title,
            "summary": summary,
            "link": url,
            "publisher": publisher,
            "published_at": pub_date,
            "thumbnail": thumbnail,
        })
    return result
