"""
Biscuit Agent — Türkiye borsası odaklı hisse analiz uzmanı.

AI_PROVIDER=ollama (varsayılan, ücretsiz, yerel) veya anthropic ile çalışır.
Ollama kullanımı için: https://ollama.ai adresinden kurulum yapın,
ardından: ollama pull llama3.1 (veya tercih ettiğiniz model)

Kullanım:
    from biscuit_agent import BiscuitAgent
    agent = BiscuitAgent()
    reply = agent.chat(messages=[{"role": "user", "content": "GARAN analiz et"}])
"""

import json
import os
import requests

# ---------------------------------------------------------------------------
# Sağlayıcı seçimi
# ---------------------------------------------------------------------------

AI_PROVIDER = os.environ.get("AI_PROVIDER", "ollama").lower()

# Ollama ayarları
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")

# Anthropic ayarları (yedek)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_BASE_URL = os.environ.get("ANTHROPIC_BASE_URL")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_DEFAULT_MODEL", "claude-opus-4-6")


def _make_client():
    if AI_PROVIDER == "anthropic":
        import anthropic
        key = ANTHROPIC_API_KEY
        if key and ANTHROPIC_BASE_URL:
            return anthropic.Anthropic(api_key=key, base_url=ANTHROPIC_BASE_URL)
        if key:
            return anthropic.Anthropic(api_key=key)
        return anthropic.Anthropic()
    return None  # Ollama client object gerekmez, requests kullanırız


# ---------------------------------------------------------------------------
# Sistem prompt (web araması araçlı, Biscuit kimliği)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """Sen Biscuit adında deneyimli, aktif ve risk alabilen bir hisse senedi yatırım uzmanısın. Market Tracker uygulaması içinde çalışırsın ve kullanıcıyla Türkçe sohbet edersin.

Teknik indikatörlere dayalı kısa ve orta vadeli alım-satım kararları üretirsin. Hedefin kullanıcıya net, anlaşılır ve kanıta dayalı yatırım önerileri sunmaktır.

## Kullandığın İndikatörler
RSI, MACD, Bollinger Bantları, Hacim Analizi, Supertrend, Hareketli Ortalamalar (EMA/SMA), ATR, Destek/Direnç seviyeleri

## Risk Sınıflandırması
- DÜŞÜK RİSK: Güçlü trend, net destek, düşük volatilite
- ORTA RİSK: Kısmen belirsiz trend, orta volatilite
- YÜKSEK RİSK: Yüksek volatilite, spekülatif hareket

## Analiz Formatı
Hisse analizi yapınca şu yapıyı kullan:
📊 [HİSSE] ANALİZİ
🎯 KARAR: [AL / SAT / BEKLE]
⏱️ VADE: [Kısa / Orta Vadeli]
⚠️ RİSK: [DÜŞÜK / ORTA / YÜKSEK]
📌 DURUM: [özet]
🔍 TEKNİK: [indikatörler]
📐 SEVİYELER: Giriş / Hedef / Stop-Loss
⚡ ÖZET: [1-2 cümle]

## Kurallar
- Stop-loss olmadan alım önerisi verme
- Yalın Türkçe kullan, teknik terimleri açıkla
- Veri bazlı gerekçe sun, belirsiz ifadeler kullanma
- Sohbet tonunu sıcak ve profesyonel tut
- Adın Biscuit, kendinle gurur duyuyorsun"""


def _do_web_search(query: str, max_results: int = 5) -> str:
    """DuckDuckGo arama yap ve sonuçları döndür."""
    try:
        from duckduckgo_search import DDGS
        results = DDGS().text(query, max_results=min(max_results, 10))
        if not results:
            return "Arama sonucu bulunamadı."
        lines = []
        for r in results:
            lines.append(
                f"**{r.get('title', '')}**\n{r.get('body', '')}\nKaynak: {r.get('href', '')}"
            )
        return "\n\n---\n\n".join(lines)
    except Exception as e:
        return f"Arama hatası: {str(e)}"


def _ollama_chat(messages: list[dict], system: str) -> str:
    """Ollama API ile sohbet (eski sürüm /api/generate uyumlu)."""
    user_msgs = [m["content"] for m in messages if m["role"] == "user"]
    prompt = "\n".join(user_msgs) if user_msgs else messages[-1]["content"]
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {"num_predict": 2048},
    }
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "")
    except requests.exceptions.ConnectionError:
        return "⚠️ Ollama çalışmıyor. Lütfen `ollama serve` komutunu çalıştırın ve modeli yükleyin: `ollama pull " + OLLAMA_MODEL + "`"
    except Exception as e:
        return f"⚠️ Ollama hatası: {str(e)}"


def _anthropic_chat(client, messages: list[dict], system: str) -> str:
    """Anthropic API ile sohbet (tool calling dahil)."""
    loop_messages = list(messages)
    max_iters = 5
    for _ in range(max_iters):
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=2000,
            system=system,
            tools=[{
                "name": "web_search",
                "description": "İnternet üzerinde güncel bilgi arar.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Arama sorgusu"},
                        "max_results": {"type": "integer", "description": "Maksimum sonuç sayısı", "default": 5},
                    },
                    "required": ["query"],
                },
            }],
            messages=loop_messages,
        )

        if response.stop_reason != "tool_use":
            return next(
                (b.text for b in response.content if b.type == "text"), ""
            )

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                query = block.input.get("query", "")
                max_r = block.input.get("max_results", 5)
                result_text = _do_web_search(query, max_r)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_text,
                })

        loop_messages = loop_messages + [
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": tool_results},
        ]
    return "⚠️ Maksimum tur sayısına ulaşıldı."


# ---------------------------------------------------------------------------
# BiscuitAgent
# ---------------------------------------------------------------------------

class BiscuitAgent:
    """
    Biscuit agent'ının tüm mantığını kapsüller.
    AI_PROVIDER ortam değişkenine göre Ollama veya Anthropic kullanır.
    """

    def __init__(self):
        self._client = _make_client()

    def chat(self, messages: list[dict], context: str = "") -> str:
        """
        Verilen mesaj geçmişiyle Biscuit agent'ını çalıştır.

        Args:
            messages: [{"role": "user"|"assistant", "content": "..."}]
            context:  Piyasa verisi gibi ek bağlam

        Returns:
            Agent yanıtı (str)
        """
        system = SYSTEM_PROMPT
        if context:
            system += f"\n\n## Mevcut Piyasa Verisi (Market Tracker)\n{context}"

        if AI_PROVIDER == "anthropic":
            if not self._client:
                return "⚠️ Anthropic API anahtarı (ANTHROPIC_API_KEY) tanımlanmamış."
            return _anthropic_chat(self._client, messages, system)
        else:
            return _ollama_chat(messages, system)

    # ------------------------------------------------------------------
    # Watchlist yardımcıları
    # ------------------------------------------------------------------

    def get_watchlist(self) -> list[dict]:
        """Watchlist'i yükle."""
        _base = os.path.dirname(__file__)
        watchlist_file = os.path.join(_base, "watchlist.json")
        default_file = os.path.join(_base, "data", "default_watchlist.json")
        try:
            path = watchlist_file if os.path.exists(watchlist_file) else default_file
            with open(path, "r") as f:
                return json.load(f).get("tickers", [])
        except Exception:
            return []

    def get_watchlist_summary(self) -> list[dict]:
        """Watchlist'teki tüm hisseler için özet sinyal verisi döndür."""
        try:
            from services.yahoo_finance import get_stock_history
            from services.indicators import calculate_all_indicators
            from services.signals import generate_signal

            items = self.get_watchlist()
            results = []
            for item in items:
                ticker = item["ticker"]
                try:
                    df = get_stock_history(ticker, period="3mo")
                    df = df.dropna(subset=["Close"])
                    price = change_pct = rsi_val = None
                    signal_data = {"signal": "N/A", "score": 0, "confidence": "LOW"}
                    if len(df) >= 2:
                        price = round(float(df["Close"].iloc[-1]), 2)
                        prev = float(df["Close"].iloc[-2])
                        change_pct = round((price - prev) / prev * 100, 2) if prev else 0
                    if len(df) >= 15:
                        indicators = calculate_all_indicators(df)
                        signal_data = generate_signal(indicators["latest"])
                        rsi_val = indicators["latest"].get("rsi")
                    results.append({
                        "ticker": ticker,
                        "name": item.get("name", ticker),
                        "price": price,
                        "change_pct": change_pct,
                        "signal": signal_data["signal"],
                        "score": signal_data["score"],
                        "rsi": rsi_val,
                    })
                except Exception:
                    results.append({
                        "ticker": ticker,
                        "name": item.get("name", ticker),
                        "price": None,
                        "change_pct": None,
                        "signal": "N/A",
                        "score": 0,
                        "rsi": None,
                    })
            return results
        except Exception:
            return []

    def build_context_string(self) -> str:
        """Watchlist özet verisini metin olarak döndür."""
        try:
            summary = self.get_watchlist_summary()
            if not summary:
                return ""
            return json.dumps(summary, ensure_ascii=False, indent=2)
        except Exception:
            return ""
