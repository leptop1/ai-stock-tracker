import os
import json
import anthropic

# ANTHROPIC_AUTH_TOKEN veya ANTHROPIC_API_KEY destekle
_api_key = os.environ.get("ANTHROPIC_API_KEY")
_auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")
_base_url = os.environ.get("ANTHROPIC_BASE_URL")

if _api_key:
    client = anthropic.Anthropic(api_key=_api_key, base_url=_base_url) if _base_url else anthropic.Anthropic(api_key=_api_key)
elif _auth_token:
    client = anthropic.Anthropic(api_key=_auth_token, base_url=_base_url) if _base_url else anthropic.Anthropic(api_key=_auth_token)
else:
    client = anthropic.Anthropic()  # SDK kendi ortam değişkenlerini arar

_model = os.environ.get("ANTHROPIC_DEFAULT_HAIKU_MODEL", "claude-haiku-4-5-20251001")

TURKEY_CONTEXT_SYMBOLS = [
    {"symbol": "USDTRY=X", "name": "USD/TRY"},
    {"symbol": "EURTRY=X", "name": "EUR/TRY"},
    {"symbol": "GBPTRY=X", "name": "GBP/TRY"},
    {"symbol": "GC=F",     "name": "Altın"},
    {"symbol": "SI=F",     "name": "Gümüş"},
    {"symbol": "CL=F",     "name": "Ham Petrol"},
]


def _fetch_context_data() -> list:
    """Türkiye döviz ve emtia verilerini çek."""
    from services.viop_data import get_viop_history
    from services.indicators import calculate_all_indicators

    context = []
    for item in TURKEY_CONTEXT_SYMBOLS:
        try:
            df = get_viop_history(item["symbol"], period="1mo")
            df = df.dropna(subset=["Close"])
            if len(df) < 2:
                continue
            price = round(float(df["Close"].iloc[-1]), 4)
            prev  = round(float(df["Close"].iloc[-2]), 4)
            change_pct = round((price - prev) / prev * 100, 2) if prev else 0
            week_change = None
            if len(df) >= 6:
                week_ago = float(df["Close"].iloc[-6])
                week_change = round((price - week_ago) / week_ago * 100, 2) if week_ago else None
            month_change = None
            if len(df) >= 22:
                month_ago = float(df["Close"].iloc[-22])
                month_change = round((price - month_ago) / month_ago * 100, 2) if month_ago else None
            rsi = None
            trend = None
            if len(df) >= 15:
                ind = calculate_all_indicators(df)
                rsi = ind["latest"].get("rsi")
                closes = df["Close"]
                if len(closes) >= 20:
                    sma5  = float(closes.iloc[-5:].mean())
                    sma20 = float(closes.iloc[-20:].mean())
                    trend = "YUKARI" if sma5 > sma20 else "ASAGI"
            context.append({
                "name": item["name"],
                "symbol": item["symbol"],
                "price": price,
                "change_pct_daily": change_pct,
                "change_pct_weekly": week_change,
                "change_pct_monthly": month_change,
                "rsi": round(rsi, 1) if rsi is not None else None,
                "trend": trend,
            })
        except Exception:
            pass
    return context


SYSTEM_PROMPT = """Sen Türkiye borsasında uzmanlaşmış bir türev araçlar analistisin.
Görevin: Verilen VİOP enstrümanı için PUT opsiyon ile hedge alınıp alınmaması gerektiğini analiz et.

Analiz yaparken şunları dikkate al:
1. Döviz kurları (USD/TRY, EUR/TRY, GBP/TRY) — TL değer kaybı portföyü eritir
2. Emtia fiyatları (Altın, Gümüş, Petrol) — enflasyon ve risk iştahı göstergesi
3. Teknik indikatörler (RSI, trend) — aşırı alım/satım bölgeleri
4. Enstrümanın kategorisi ve fiyat hareketi

Karar kriterleri:
- HEDGE AL: Yüksek risk sinyali var (TL zayıflıyor + emtia yükseliyor + RSI aşırı alımda + düşüş trendi)
- HEDGE ALMA: Düşük risk, yükseliş trendi güçlü, hedge maliyeti avantajı azaltır
- NÖTR: Karma sinyaller, belirsizlik yüksek

Cevabını SADECE şu JSON formatında ver, başka hiçbir şey yazma:
{
  "hedge_signal": "HEDGE_AL" | "HEDGE_ALMA" | "NÖTR",
  "confidence": "YÜKSEK" | "ORTA" | "DÜŞÜK",
  "score": <-1.0 ile 1.0 arasında float, pozitif = hedge al>,
  "reasoning": "<2-3 cümle Türkçe açıklama>",
  "key_factors": ["<faktör 1>", "<faktör 2>", "<faktör 3>"]
}"""


def analyze_hedge(
    symbol,
    name,
    category,
    price,
    change_pct,
    rsi,
    signal,
    score,
):
    """
    Uzman agent ile opsiyon hedge analizi yap.
    Döndürür: {hedge_signal, confidence, score, reasoning, key_factors}
    """
    context_data = _fetch_context_data()
    context_str = json.dumps(context_data, ensure_ascii=False, indent=2)

    user_message = f"""## Analiz edilecek VİOP enstrümanı
- Sembol: {symbol}
- İsim: {name}
- Kategori: {category}
- Güncel fiyat: {price}
- Günlük değişim: {change_pct}%
- RSI: {rsi}
- Teknik sinyal: {signal} (skor: {score})

## Türkiye piyasası anlık verileri
{context_str}

Yukarıdaki verilere dayanarak bu enstrüman için PUT opsiyon hedge analizi yap."""

    try:
        response = client.messages.create(
            model=_model,
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        raw = response.content[0].text.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
        for field in ("hedge_signal", "confidence", "score", "reasoning", "key_factors"):
            if field not in result:
                raise ValueError(f"Missing field: {field}")
        return result
    except Exception as e:
        return {
            "hedge_signal": "NÖTR",
            "confidence": "DÜŞÜK",
            "score": 0.0,
            "reasoning": f"Analiz yapılamadı: {str(e)}",
            "key_factors": [],
        }
