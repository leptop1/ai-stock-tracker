# Kurulum Rehberi

## Gereksinimler
- Python 3.11+
- Node.js 18+
- Ollama (AI sohbet için, ücretsiz)

## 1. Ollama Kurulumu

### Linux:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1
```

### macOS:
```bash
brew install ollama
ollama pull llama3.1
```

### Windows:
https://ollama.ai adresinden indirin, kurun ve:
```powershell
ollama pull llama3.1
```

## 2. Backend Kurulumu

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
cp .env.example .env
python app.py
# → http://localhost:5001
```

## 3. Frontend Kurulumu

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

## Kullanım

1. Ollama'yı arka planda çalıştırın: `ollama serve`
2. Backend'i başlatın: `python app.py`
3. Frontend'i başlatın: `npm run dev`
4. Tarayıcıda `http://localhost:5173` adresini açın

## AI Sağlayıcı Değiştirme

Varsayılan: **Ollama** (ücretsiz, yerel)

Anthropic Claude kullanmak için `.env` dosyasını düzenleyin:
```
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

## Telegram Botu

```bash
cd backend
TELEGRAM_BOT_TOKEN=xxx python telegram_agent.py
```
