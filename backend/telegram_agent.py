"""
Telegram Agent — Biscuit hisse analiz botu.

Kullanım:
    TELEGRAM_BOT_TOKEN=<token> python telegram_agent.py

Ortam değişkenleri:
    TELEGRAM_BOT_TOKEN   — Telegram BotFather'dan alınan token (zorunlu)
    AI_PROVIDER          — "ollama" (varsayılan, ücretsiz) veya "anthropic"
    OLLAMA_BASE_URL      — Ollama sunucu adresi (varsayılan: http://localhost:11434)
    OLLAMA_MODEL         — Ollama model adı (varsayılan: llama3.1)
    ANTHROPIC_API_KEY    — Anthropic API anahtarı (AI_PROVIDER=anthropic ise)
"""

import asyncio
import json
import logging
import os
import sys

# Dosya konumuna göre backend dizinini Python path'e ekle
sys.path.insert(0, os.path.dirname(__file__))

try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(_env_path)
except ImportError:
    pass

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ChatAction

from biscuit_agent import BiscuitAgent

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Sabitler — ConversationHandler durumları
# ---------------------------------------------------------------------------
MENU_WATCHLIST  = "MENU_WATCHLIST"   # inline menü beklenirken
AWAITING_ADD    = "AWAITING_ADD"     # eklenecek ticker bekleniyor
AWAITING_REMOVE = "AWAITING_REMOVE"  # çıkarılacak ticker bekleniyor

# ---------------------------------------------------------------------------
# Uygulama durumu
# ---------------------------------------------------------------------------
_user_sessions: dict[int, list[dict]] = {}
_agent = BiscuitAgent()


def _get_history(user_id: int) -> list[dict]:
    return _user_sessions.setdefault(user_id, [])


def _clear_history(user_id: int) -> None:
    _user_sessions[user_id] = []


# ---------------------------------------------------------------------------
# Watchlist yazma yardımcısı
# ---------------------------------------------------------------------------
_WATCHLIST_FILE = os.path.join(os.path.dirname(__file__), "watchlist.json")
_DEFAULT_FILE   = os.path.join(os.path.dirname(__file__), "data", "default_watchlist.json")


def _save_watchlist(tickers: list[dict]) -> None:
    with open(_WATCHLIST_FILE, "w") as f:
        json.dump({"tickers": tickers}, f, indent=2, ensure_ascii=False)


def _load_watchlist_raw() -> list[dict]:
    path = _WATCHLIST_FILE if os.path.exists(_WATCHLIST_FILE) else _DEFAULT_FILE
    with open(path, "r") as f:
        return json.load(f).get("tickers", [])


# ---------------------------------------------------------------------------
# Watchlist yönetim menüsü
# ---------------------------------------------------------------------------

def _watchlist_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Hisse Ekle",   callback_data="wl_add"),
            InlineKeyboardButton("➖ Hisse Çıkar",  callback_data="wl_remove"),
        ],
        [
            InlineKeyboardButton("📋 Listeyi Göster", callback_data="wl_list"),
            InlineKeyboardButton("❌ Kapat",           callback_data="wl_close"),
        ],
    ])


async def cmd_manage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """/yonet komutu — watchlist yönetim menüsünü aç."""
    await update.message.reply_text(
        "📂 *Watchlist Yönetimi*\n\nNe yapmak istersiniz?",
        parse_mode="Markdown",
        reply_markup=_watchlist_menu_keyboard(),
    )
    return MENU_WATCHLIST


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Inline buton tıklamalarını işle."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "wl_list":
        items = _load_watchlist_raw()
        if not items:
            text = "📋 İzleme listesi boş."
        else:
            lines = ["📋 *İzleme Listesi*\n"]
            for item in items:
                lines.append(f"  • `{item['ticker']}` — {item.get('name', item['ticker'])}")
            text = "\n".join(lines)
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=_watchlist_menu_keyboard(),
        )
        return MENU_WATCHLIST

    if data == "wl_add":
        await query.edit_message_text(
            "➕ *Eklenecek hissenin sembolünü yazın.*\n\n"
            "Örnek: `AAPL` veya `THYAO.IS`\n\n"
            "İptal için /iptal",
            parse_mode="Markdown",
        )
        return AWAITING_ADD

    if data == "wl_remove":
        items = _load_watchlist_raw()
        if not items:
            await query.edit_message_text(
                "📋 İzleme listesi zaten boş.",
                reply_markup=_watchlist_menu_keyboard(),
            )
            return MENU_WATCHLIST
        # Hisse başına "Çıkar" butonu
        buttons = [
            [InlineKeyboardButton(
                f"🗑 {item['ticker']} — {item.get('name', '')}",
                callback_data=f"rm_{item['ticker']}",
            )]
            for item in items
        ]
        buttons.append([InlineKeyboardButton("« Geri", callback_data="wl_back")])
        await query.edit_message_text(
            "➖ *Çıkarmak istediğiniz hisseyi seçin:*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return AWAITING_REMOVE

    if data == "wl_close":
        await query.edit_message_text("✅ Menü kapatıldı.")
        return ConversationHandler.END

    if data == "wl_back":
        await query.edit_message_text(
            "📂 *Watchlist Yönetimi*\n\nNe yapmak istersiniz?",
            parse_mode="Markdown",
            reply_markup=_watchlist_menu_keyboard(),
        )
        return MENU_WATCHLIST

    # rm_TICKER — watchlist'ten çıkar
    if data.startswith("rm_"):
        ticker = data[3:]
        items = _load_watchlist_raw()
        new_items = [i for i in items if i["ticker"] != ticker]
        if len(new_items) == len(items):
            await query.edit_message_text(
                f"⚠️ `{ticker}` listede bulunamadı.",
                parse_mode="Markdown",
                reply_markup=_watchlist_menu_keyboard(),
            )
        else:
            _save_watchlist(new_items)
            await query.edit_message_text(
                f"✅ `{ticker}` izleme listesinden çıkarıldı. ({len(new_items)} hisse kaldı)",
                parse_mode="Markdown",
                reply_markup=_watchlist_menu_keyboard(),
            )
        return MENU_WATCHLIST

    return MENU_WATCHLIST


async def receive_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Kullanıcının yazdığı ticker'ı watchlist'e ekle."""
    ticker = update.message.text.strip().upper()
    items = _load_watchlist_raw()

    if any(i["ticker"] == ticker for i in items):
        await update.message.reply_text(
            f"⚠️ `{ticker}` zaten listede.",
            parse_mode="Markdown",
            reply_markup=_watchlist_menu_keyboard(),
        )
        return MENU_WATCHLIST

    # Yahoo Finance'dan isim almayı dene
    name = ticker
    try:
        from services.yahoo_finance import get_stock_info
        info = get_stock_info(ticker)
        name = info.get("name") or info.get("longName") or ticker
    except Exception:
        pass

    items.append({"ticker": ticker, "name": name, "category": ""})
    _save_watchlist(items)

    await update.message.reply_text(
        f"✅ `{ticker}` — _{name}_ izleme listesine eklendi. (Toplam: {len(items)} hisse)",
        parse_mode="Markdown",
        reply_markup=_watchlist_menu_keyboard(),
    )
    return MENU_WATCHLIST


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """/iptal komutu — konuşma akışını sonlandır."""
    await update.message.reply_text("❌ İşlem iptal edildi.")
    return ConversationHandler.END


# ---------------------------------------------------------------------------
# Mevcut komutlar
# ---------------------------------------------------------------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Merhaba! Ben *Biscuit* — hisse senedi analiz uzmanınızım.\n\n"
        "Bana herhangi bir hisse senedi sembolü veya soru yazabilirsiniz.\n"
        "Örnek: _GARAN analiz et_ veya _BIST'te bugün ne var?_\n\n"
        "📌 Komutlar:\n"
        "  /start — Bu mesajı göster\n"
        "  /yardim — Kullanım kılavuzu\n"
        "  /temizle — Sohbet geçmişini sıfırla\n"
        "  /watchlist — İzleme listesini göster\n"
        "  /ozet — Tüm watchlist özetini al\n"
        "  /yonet — Watchlist'e hisse ekle / çıkar",
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📖 *Biscuit Kullanım Kılavuzu*\n\n"
        "*Hisse Analizi*\n"
        "  `GARAN analiz et`\n"
        "  `THYAO için ne düşünüyorsun?`\n"
        "  `BIMAS teknik analiz`\n\n"
        "*Piyasa Haberleri*\n"
        "  `Bugün borsada ne oldu?`\n"
        "  `GARAN son haberler`\n\n"
        "*Watchlist*\n"
        "  /watchlist — Tüm hisseleri listele\n"
        "  /ozet — Tüm hisselerin sinyal özetini al\n"
        "  /yonet — Hisse ekle / çıkar (butonlu menü)\n\n"
        "*Sohbet*\n"
        "  /temizle — Konuşma geçmişini sıfırla\n\n"
        "_Biscuit teknik indikatörler (RSI, MACD, Bollinger) ve güncel "
        "haber arama ile analiz yapar._",
        parse_mode="Markdown",
    )


async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _clear_history(update.effective_user.id)
    await update.message.reply_text("🗑️ Sohbet geçmişi temizlendi.")


async def cmd_watchlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        items = _agent.get_watchlist()
        if not items:
            await update.message.reply_text("📋 İzleme listesi boş.")
            return
        lines = ["📋 *İzleme Listesi*\n"]
        for item in items:
            lines.append(f"  • `{item['ticker']}` — {item.get('name', item['ticker'])}")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        logger.exception("watchlist hatası")
        await update.message.reply_text(f"❌ Watchlist alınamadı: {e}")


async def cmd_ozet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.chat.send_action(ChatAction.TYPING)
    try:
        summary = _agent.get_watchlist_summary()
        if not summary:
            await update.message.reply_text("📊 Veri bulunamadı.")
            return
        lines = ["📊 *Watchlist Özeti*\n"]
        for s in summary:
            signal_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(s.get("signal", ""), "⚪")
            price_str = f"{s['price']:.2f}" if s.get("price") else "N/A"
            change_str = f"{s['change_pct']:+.2f}%" if s.get("change_pct") is not None else ""
            rsi_str = f"RSI:{s['rsi']:.1f}" if s.get("rsi") else ""
            parts = [p for p in [price_str, change_str, rsi_str] if p]
            lines.append(
                f"{signal_emoji} `{s['ticker']}` {s.get('name', '')} — "
                f"{s.get('signal', 'N/A')} | {' | '.join(parts)}"
            )
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        logger.exception("ozet hatası")
        await update.message.reply_text(f"❌ Özet alınamadı: {e}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_text = update.message.text.strip()

    if not user_text:
        return

    await update.message.chat.send_action(ChatAction.TYPING)

    history = _get_history(user_id)
    history.append({"role": "user", "content": user_text})

    try:
        reply = await asyncio.to_thread(
            _agent.chat,
            messages=history,
            context=_agent.build_context_string(),
        )
        history.append({"role": "assistant", "content": reply})
        for chunk in _split_message(reply):
            await update.message.reply_text(chunk, parse_mode="Markdown")
    except Exception as e:
        logger.exception("agent hatası")
        await update.message.reply_text(f"❌ Bir hata oluştu: {e}")


def _split_message(text: str, limit: int = 4000) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks = []
    while text:
        chunks.append(text[:limit])
        text = text[limit:]
    return chunks


# ---------------------------------------------------------------------------
# Ana fonksiyon
# ---------------------------------------------------------------------------

def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN ortam değişkeni tanımlanmamış.")
        sys.exit(1)

    app = ApplicationBuilder().token(token).build()

    # Watchlist yönetim konuşma akışı
    wl_conv = ConversationHandler(
        entry_points=[CommandHandler("yonet", cmd_manage)],
        states={
            MENU_WATCHLIST: [
                CallbackQueryHandler(menu_callback),
            ],
            AWAITING_ADD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_add),
                CallbackQueryHandler(menu_callback),
            ],
            AWAITING_REMOVE: [
                CallbackQueryHandler(menu_callback),
            ],
        },
        fallbacks=[CommandHandler("iptal", cmd_cancel)],
    )

    app.add_handler(wl_conv)
    app.add_handler(CommandHandler("start",     cmd_start))
    app.add_handler(CommandHandler("yardim",    cmd_help))
    app.add_handler(CommandHandler("temizle",   cmd_clear))
    app.add_handler(CommandHandler("watchlist", cmd_watchlist))
    app.add_handler(CommandHandler("ozet",      cmd_ozet))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Biscuit Telegram agent başlatıldı.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
