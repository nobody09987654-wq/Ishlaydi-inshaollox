# main.py
# ITeach Academy Registration Bot — Clean/Ad-Safe Professional Edition

import logging
import re
import html
from datetime import datetime
from typing import Optional, Dict, Any

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode

# ---------------- CONFIG ----------------
BOT_TOKEN = "7832412035:AAHrVkpQXGl4KnxdMWu2hkRu1QgZZaBmGJc"  # <-- o'zingizning tokeningizni yozing
ADMIN_ID = 6427405038  # faqat bitta admin ID

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("iteach_bot")

# ---------------- DATA ----------------
COURSES = {
    "english": "🇬🇧 Ingliz tili",
    "german": "🇩🇪 Nemis tili",
    "russian": "🇷🇺 Rus tili",
    "arabic": "🇸🇦 Arab tili",
    "math": "🧮 Matematika",
    "uzbek": "🇺🇿 Ona tili",
    "history": "📜 Tarix",
    "biology": "🧬 Biologiya",
    "chemistry": "⚗️ Kimyo",
    "law": "⚖️ Huquq",
}
COURSES_WITH_LEVEL = {"english", "german", "russian"}

LEVELS = {
    "A1": "A1 • Beginner",
    "A2": "A2 • Elementary",
    "B1": "B1 • Intermediate",
    "B2": "B2 • Upper-Intermediate",
    "C1": "C1 • Advanced",
    "C2": "C2 • Proficient",
}
SECTIONS = {
    "kids": "👶 Kids",
    "general": "📘 General",
    "certificate": "🏅 Certificate",
    "ielts": "🎓 IELTS",   # faqat ingliz tili uchun
}

PHONE_REGEX = re.compile(r"^\+998\d{9}$")

# ---------------- VALIDATION ----------------
def valid_full_name(s: str) -> bool:
    s = s.strip()
    parts = s.split()
    if len(parts) < 2:
        return False
    return all(len(p) >= 2 for p in parts)

def valid_age(s: str) -> bool:
    return s.isdigit() and 3 <= int(s) <= 100

def normalize_phone(s: str) -> Optional[str]:
    t = re.sub(r"[^\d+]", "", s.strip())
    if t.startswith("998") and len(t) == 12:
        t = "+" + t
    if t.startswith("+998") and len(t) == 13:
        return t
    return None

# ---------------- HELPERS ----------------
def esc(s: Any) -> str:
    return html.escape(str(s) if s else "")

def build_admin_text(d: Dict[str, Any], u) -> str:
    txt = [
        "🔔 <b>Yangi o‘quvchi ro‘yxatdan o‘tdi</b>",
        f"👤 <b>Ism:</b> {esc(d.get('full_name'))}",
        f"🎂 <b>Yosh:</b> {esc(d.get('age'))}",
        f"📱 <b>Telefon:</b> {esc(d.get('phone'))}",
        f"📚 <b>Kurs:</b> {esc(COURSES.get(d.get('course'), d.get('course')))}",
    ]
    if d.get("course") not in {"law"}:
        txt.append(f"🗂 <b>Bo‘lim:</b> {esc(SECTIONS.get(d.get('section'), d.get('section')))}")
    if d.get("course") in COURSES_WITH_LEVEL:
        txt.append(f"📊 <b>Daraja:</b> {esc(LEVELS.get(d.get('level'), d.get('level')))}")
    txt += [
        f"🆔 <b>Telegram ID:</b> {u.id}",
        f"👤 <b>Username:</b> @{u.username}" if u.username else "👤 <b>Username:</b> Yo‘q",
        f"📅 <b>Sana:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    ]
    return "\n".join(txt)

def nav_buttons(step: str) -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton("❌ Bekor qilish", callback_data="reg:cancel")]
    ]
    if step != "course":
        kb.insert(0, [InlineKeyboardButton("⬅️ Ortga", callback_data=f"back:{step}")])
    return InlineKeyboardMarkup(kb)

# ---------------- SAFETY: AD/MEDIA FILTERS ----------------
AD_KEYWORDS = [
    "awin", "bet", "casino", "1xbet", "melbet", "mostbet", "parimatch", "bcgame",
    "bonus", "promo", "promokod", "promo code", "aktsiya", "aksiya",
    "click here", "подпишись", "заработай", "выиграй", "ставк", "букмек",
    "lottery", "lotereya", "bukmeker", "affiliate", "реферал", "referral",
    "kredit", "qarz", "loan", "pul ishlang",
    "tezkor pul", "klik", "klik qiling", "подписка", "подписывайся"
]
AD_DOMAINS = [
    "http://", "https://", "www.", "t.me/joinchat", "t.me/+",
    ".bet", ".casino", ".porn", ".sex", ".xxx", ".cfd", ".binomo", "binance", "okx",
]

AD_REGEX = re.compile(
    r"(" + r"|".join([re.escape(k) for k in AD_KEYWORDS + AD_DOMAINS]) + r")",
    flags=re.IGNORECASE
)

def looks_like_ad(text: str) -> bool:
    if not text:
        return False
    if AD_REGEX.search(text):
        return True
    if re.search(r"(?:https?://|t\.me/|[A-Za-z0-9\-]+\.[A-Za-z]{2,})", text, flags=re.I):
        return True
    return False

# ---------------- HANDLERS ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👋 Assalomu alaykum!\n\n"
        "<b>ITeach Academy</b> ga xush kelibsiz 🎓\n\n"
        "Bizning jamoamizga qo'shilish va roʻyxatdan o'tish uchun pastdagi tugmadan foydalaning 👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Ro‘yxatdan o‘tish", callback_data="reg:start")]
        ]),
        parse_mode=ParseMode.HTML,
    )

# Test uchun oddiy handlerlar (o‘rniga o‘z funksiyangizni qo‘ying)
async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("Callback!")

async def msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Message!")

async def delete_media_and_forwards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()

async def delete_ad_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if looks_like_ad(update.message.text):
        await update.message.delete()

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

# ---------------- RUN ----------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_error_handler(error_handler)

    app.add_handler(MessageHandler(
        filters.PHOTO
        | filters.VIDEO
        | filters.AUDIO
        | filters.VOICE
        | filters.VIDEO_NOTE
        | filters.ANIMATION
        | filters.DOCUMENT
        | filters.STICKER
        | filters.CONTACT
        | filters.FORWARD,  # Faqat yangi versiyada FORWARD, eski versiyada FORWARDED bo‘ladi
        delete_media_and_forwards
    ), group=0)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, delete_ad_text), group=1)

    app.add_handler(CommandHandler("start", start), group=2)
    app.add_handler(CallbackQueryHandler(cb_handler), group=2)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler), group=2)
    app.add_handler(MessageHandler(filters.CONTACT, msg_handler), group=2)

    logger.info("Bot is running with hardened ad/media filters...")
    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()