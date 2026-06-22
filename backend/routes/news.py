from flask import Blueprint, jsonify
from services.yahoo_finance import get_news
from routes.watchlist import load_watchlist
import time

news_bp = Blueprint("news", __name__)

_summary_cache = {}
_summary_cache_ts = {}
CACHE_TTL = 300


def _get_cached(key):
    if key in _summary_cache and time.time() - _summary_cache_ts.get(key, 0) < CACHE_TTL:
        return _summary_cache[key]
    return None


def _set_cached(key, value):
    _summary_cache[key] = value
    _summary_cache_ts[key] = time.time()


@news_bp.route("/")
def all_news():
    watchlist = load_watchlist()
    tickers = [w["ticker"] for w in watchlist[:10]]
    all_items = []
    for ticker in tickers:
        try:
            items = get_news(ticker)
            for item in items:
                item["ticker"] = ticker
            all_items.extend(items)
        except Exception:
            pass
    all_items.sort(key=lambda x: x.get("published_at") or 0, reverse=True)
    return jsonify(all_items[:50])


@news_bp.route("/<ticker>")
def ticker_news(ticker):
    ticker = ticker.upper()
    try:
        items = get_news(ticker)
        for item in items:
            item["ticker"] = ticker
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@news_bp.route("/<ticker>/summary")
def ticker_news_summary(ticker):
    ticker = ticker.upper()
    cache_key = f"summary:{ticker}"
    cached = _get_cached(cache_key)
    if cached:
        return jsonify(cached)

    try:
        items = get_news(ticker)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if not items:
        return jsonify({"summary": None, "articles": []})

    top5 = items[:5]
    articles = [
        {"title": a["title"], "summary": a.get("summary", ""), "publisher": a.get("publisher", ""), "link": a.get("link", "")}
        for a in top5
    ]

    news_text = ""
    for i, a in enumerate(articles, 1):
        news_text += f"{i}. {a['title']}"
        if a["summary"]:
            news_text += f"\n   {a['summary']}"
        if a["publisher"]:
            news_text += f"\n   Kaynak: {a['publisher']}"
        news_text += "\n\n"

    try:
        import anthropic
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=400,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"{ticker} hissesiyle ilgili aşağıdaki son 5 haberi Türkçe olarak tek bir akıcı paragrafta özetle. "
                        "Yatırımcı perspektifinden en önemli bilgileri vurgula. "
                        "Özet 2-3 cümle olsun.\n\n"
                        + news_text
                    ),
                }
            ],
        )
        ai_summary = message.content[0].text
    except Exception as e:
        ai_summary = None

    result = {"summary": ai_summary, "articles": articles}
    _set_cached(cache_key, result)
    return jsonify(result)
