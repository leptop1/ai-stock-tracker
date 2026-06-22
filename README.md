# Market Tracker

**AI Stocks (ABD)**, **VIOP** ve **BIST (Borsa İstanbul)** piyasalarını takip eden, teknik indikatörler bazında analiz yapan, alım/satım önerileri sunan ve Biscuit AI asistanı ile sohbet imkânı veren web uygulaması.

---

## Modüller

### AI Stocks — Amerikan Borsası
Amerikan borsasındaki (NASDAQ/NYSE) AI sektörü hisse senetleri takibi.

- 30 AI şirketi ile hazır başlangıç listesi (NVDA, MSFT, GOOGL, META, AMD, PLTR vb.)
- Otomatik AI hisse keşfi (Yahoo Finance arama + ETF holdings)
- Yahoo Finance haber akışı
- Hisse ekleme/çıkarma (kart üzerinden veya sol menüden)

### VIOP — Borsa İstanbul Türev Araçları
Türkiye'nin vadeli işlem ve opsiyon piyasası (Borsa İstanbul) takibi.

| Kategori | Enstrümanlar |
|----------|-------------|
| **Endeks** | BIST 30 (XU030.IS), BIST 100 (XU100.IS) |
| **Döviz** | USD/TRY, EUR/TRY, GBP/TRY |
| **Emtia** | Altın (GC=F), Gümüş (SI=F), Ham Petrol (CL=F) |
| **Hisse** | GARAN, AKBNK, THYAO, EREGL, KCHOL, SAHOL, SISE, TCELL, BIMAS, ASELS |

- TRY ve USD fiyat gösterimi
- **VIOP'a özel sinyal**: LONG / SHORT / HEDGE / NEUTRAL
- Hedge skor barı (çelişkili indikatör yoğunluğu)
- İndikatör bazlı gerekçe listesi (her indikatör için yön + açıklama)

### BIST — Borsa İstanbul Spot Piyasa
Türkiye borsasındaki 32 hisse senedi (BIST30 + seçili hisseler).

- Kategori bazlı renk kodlaması (Bankacılık, Enerji, Teknoloji vb.)
- TRY fiyat ve günlük değişim gösterimi
- Hisse ekleme/çıkarma

---

## Ortak Özellikler

- **Teknik indikatörler**: RSI (14), MACD (12/26/9), Bollinger Bands (20), Hacim analizi
- **Sinyal motoru**: BUY / SELL / HOLD + HIGH / MEDIUM / LOW güven seviyesi
- **Grafikler**: Fiyat + Bollinger overlay, RSI, MACD histogram, Hacim
- **Bollinger Squeeze** tespiti ve tooltip açıklaması
- **İndikatör şeffaflığı**: Her indikatörün ağırlığı, değeri ve hesaplama formülü tooltip ile görünür
- **Hisse silme**: Ana ekrandaki her kartın sol üst köşesinde hover ile silme butonu
- 60 saniyede bir otomatik yenileme
- 5 dakika in-memory cache (Yahoo Finance rate limit koruması)

### Sinyal Ağırlıkları

| İndikatör | Ağırlık | BUY / LONG | SELL / SHORT |
|-----------|---------|------------|--------------|
| RSI | %30 | < 30 (oversold) | > 70 (overbought) |
| MACD | %30 | Bullish crossover | Bearish crossover |
| Bollinger | %25 | Fiyat alt banda değdi | Fiyat üst banda değdi |
| Hacim | %15 | Yüksek hacim + yukarı | Yüksek hacim + aşağı |

---

## Biscuit — AI Yatırım Asistanı

Sol menünün altındaki tavşan ikonuna tıklayarak Biscuit chat panelini açabilirsiniz.

- **Teknik analiz**: RSI, MACD, Bollinger, Hacim bazlı alım/satım gerekçesi
- **Web araması**: DuckDuckGo entegrasyonu ile güncel haberler, şirket duyuruları ve piyasa gelişmeleri
- **Watchlist bağlamı**: Açık olan tüm modüllerdeki (AI Stocks, VIOP, BIST) güncel veriler Biscuit'e otomatik iletilir
- **Yeniden boyutlandırma**: Chat penceresinin sol üst köşesinden sürükleyerek boyut ayarlanabilir
- **Tam ekran**: Başlık çubuğundaki ⤢ ikonu ile tam ekran yapılabilir

### Biscuit'e Örnek Sorular
- *"GARAN hissesi hakkında bugünkü son haberler neler?"*
- *"NVDA için teknik analiz yap, almalı mıyım?"*
- *"Portföyümdeki hisselerin genel risk durumu nedir?"*
- *"THYAO neden düştü?"*

---

## Telegram Botu — Biscuit Agent

Biscuit'e Telegram üzerinden de erişilebilir. Bot; hisse analizi, watchlist yönetimi ve piyasa özetini doğrudan Telegram'dan sunar.

### Özellikler

| Komut | Açıklama |
|-------|----------|
| `/start` | Botu tanıt, komut listesini göster |
| `/yardim` | Kullanım kılavuzu |
| `/watchlist` | İzleme listesindeki tüm hisseleri göster |
| `/ozet` | Tüm hisseler için anlık sinyal özeti (BUY/SELL/HOLD, fiyat, RSI) |
| `/yonet` | **Watchlist yönetim menüsü** — inline butonlarla hisse ekle / çıkar |
| `/temizle` | Sohbet geçmişini sıfırla |
| `/iptal` | Aktif işlemi iptal et |

Serbest metin yazıldığında Biscuit agent devreye girer; teknik analiz yapar, gerekirse web araması gerçekleştirir.

### `/yonet` Menüsü

```
📂 Watchlist Yönetimi

  ➕ Hisse Ekle    ➖ Hisse Çıkar
  📋 Listeyi Göster   ❌ Kapat
```

- **Ekle**: Ticker sembolü yazmanız istenir (örn. `AAPL`, `THYAO.IS`). Hisse adı Yahoo Finance'dan otomatik çekilir.
- **Çıkar**: Mevcut hisseler buton listesi olarak gösterilir, tıklayarak kaldırılır.

### Telegram Botu Kurulumu

1. [BotFather](https://t.me/BotFather)'dan `/newbot` komutuyla bir bot oluşturun ve token alın.
2. Token'ı `.env` dosyasına ekleyin:

```env
ANTHROPIC_API_KEY=your_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

3. Botu başlatın:

```bash
cd backend
python3 telegram_agent.py
```

> Bot ve Flask backend birbirinden bağımsız çalışır; aynı `watchlist.json` dosyasını paylaşırlar.

---

## Kurulum

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# API key'i ayarla
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

python app.py
# → http://localhost:5001
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### Ortam Değişkenleri

`backend/.env` dosyası oluşturun:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

Biscuit chat özelliği için [Anthropic API key](https://console.anthropic.com/) gereklidir.

---

## Tech Stack

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python 3.11 + Flask + Flask-CORS |
| Veri | yfinance + pandas + ta |
| AI | Anthropic Claude (claude-opus-4-6) + DuckDuckGo Search |
| Frontend | React 19 + Vite |
| State | Zustand |
| Grafikler | Recharts |
| Stil | Tailwind CSS v4 |

---

## API Endpoint'leri

### AI Stocks
```
GET  /api/stocks/summary        → Tüm hisse özeti
GET  /api/stocks/:ticker        → Hisse detayı + indikatörler
GET  /api/watchlist/            → Watchlist
POST /api/watchlist/            → Hisse ekle
DELETE /api/watchlist/:ticker   → Hisse çıkar
GET  /api/news/:ticker          → Haberler
GET  /api/discover/search?q=    → Hisse ara
```

### VIOP
```
GET  /api/viop/summary               → Tüm enstrüman özeti
GET  /api/viop/:symbol               → Enstrüman detayı + indikatörler + VIOP sinyali
GET  /api/viop/watchlist             → VIOP watchlist
POST /api/viop/watchlist             → Enstrüman ekle
DELETE /api/viop/watchlist/:symbol   → Enstrüman çıkar
```

### BIST
```
GET  /api/bist/summary               → Tüm hisse özeti
GET  /api/bist/:symbol               → Hisse detayı + indikatörler
GET  /api/bist/watchlist             → BIST watchlist
POST /api/bist/watchlist             → Hisse ekle
DELETE /api/bist/watchlist/:symbol   → Hisse çıkar
```

### Biscuit Chat
```
POST /api/chat/message   → { messages, context } → { reply }
```
