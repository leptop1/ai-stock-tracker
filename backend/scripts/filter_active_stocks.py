import json, sys, time
import yfinance as yf

DATA_FILE = "/home/yasin/ai-stock-tracker/backend/data/default_bist.json"
WATCHLIST_FILE = "/home/yasin/ai-stock-tracker/backend/bist_watchlist.json"

with open(DATA_FILE) as f:
    data = json.load(f)

all_instruments = data["instruments"]
total = len(all_instruments)
active = []
delisted = []
start = time.time()

for i, item in enumerate(all_instruments):
    symbol = item["symbol"]
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2mo")
        latest_close = hist["Close"].iloc[-1] if not hist.empty else None
        if latest_close is not None:
            active.append(item)
            status = "OK"
        else:
            delisted.append(symbol)
            status = "NO DATA"
    except Exception:
        delisted.append(symbol)
        status = "ERROR"

    elapsed = time.time() - start
    pct = (i + 1) / total * 100
    eta = (elapsed / (i + 1)) * (total - i - 1)
    print(f"[{i+1}/{total}] {pct:.0f}% {symbol} -> {status}  ({elapsed:.0f}s geçti, ~{eta:.0f}s kaldı)")

watchlist = {"instruments": active}
with open(WATCHLIST_FILE, "w") as f:
    json.dump(watchlist, f, ensure_ascii=False, indent=2)

dur = time.time() - start
print(f"\nToplam: {total} -> {len(active)} aktif, {len(delisted)} delist/hatalı")
print(f"Süre: {dur:.0f}sn ({dur/60:.1f}dk)")
print(f"Hatalı: {', '.join(delisted[:20])}{'...' if len(delisted) > 20 else ''}")
