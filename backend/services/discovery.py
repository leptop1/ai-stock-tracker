import time
import requests

AI_ETFS = ["BOTZ", "AIQ", "ARKQ", "IRBO"]
AI_KEYWORDS = [
    "artificial intelligence", "machine learning", "AI", "neural network",
    "deep learning", "computer vision", "natural language", "autonomous",
    "robotics", "semiconductor", "data center", "cloud computing"
]

_discovery_cache = {"data": None, "ts": 0}
DISCOVERY_CACHE_TTL = 86400  # 24 hours


def search_stocks(query: str) -> list:
    url = f"https://query1.finance.yahoo.com/v1/finance/search"
    params = {"q": query, "quotesCount": 10, "newsCount": 0, "enableFuzzyQuery": False}
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("quotes", []):
            if item.get("quoteType") != "EQUITY":
                continue
            exchange = item.get("exchange", "")
            if exchange not in ("NMS", "NYQ", "NGM", "NCM", "PCX", "ASE"):
                continue
            results.append({
                "ticker": item.get("symbol"),
                "name": item.get("longname") or item.get("shortname", ""),
                "exchange": exchange,
                "sector": item.get("sector", ""),
            })
        return results
    except Exception:
        return []


def discover_ai_stocks() -> list:
    now = time.time()
    if _discovery_cache["data"] and now - _discovery_cache["ts"] < DISCOVERY_CACHE_TTL:
        return _discovery_cache["data"]

    found = {}

    # Search by AI keywords
    for keyword in AI_KEYWORDS[:6]:  # limit to avoid rate limiting
        results = search_stocks(keyword)
        for r in results:
            ticker = r.get("ticker")
            if ticker and ticker not in found:
                found[ticker] = r
        time.sleep(0.5)

    _discovery_cache["data"] = list(found.values())
    _discovery_cache["ts"] = now
    return _discovery_cache["data"]
