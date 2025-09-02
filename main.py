# main.py
# ITeach Academy Registration Bot — Perfect Version

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
BOT_TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = 6427405038  # faqat bitta admin

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
    "math": "🧮 Matematika",
    "uzbek": "🇺🇿 Ona tili",
    "history": "📜 Tarix",
    "biology": "🧬 Biologiya",
    "chemistry": "⚗️ Kimyo",
}

COURSES_WITH_LEVEL = {"english", "german"}

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
        f"🗂 <b>Bo‘lim:</b> {esc(SECTIONS.get(d.get('section'), d.get('section')))}",
    ]
    if d.get("course") in COURSES_WITH_LEVEL:
        txt.append(f"📊 <b>Daraja:</b> {esc(LEVELS.get(d.get('level'), d.get('level')))}")
    txt += [
        f"🆔 <b>Telegram ID:</b> {u.id}",
        f"👤 <b>Username:</b> @{u.username}" if u.username else "👤 <b>Username:</b> Yo‘q",
        f"📅 <b>Sana:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    ]
    return "\n".join(txt)

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

async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    await q.answer()

    # START
    if data == "reg:start":
        kb = [[InlineKeyboardButton(v, callback_data=f"course:{k}")] for k, v in COURSES.items()]
        await q.edit_message_text("📚 Qaysi kursga yozilmoqchisiz?", reply_markup=InlineKeyboardMarkup(kb))
        return

    # COURSE SELECT
    if data.startswith("course:"):
        course = data.split(":")[1]
        context.user_data["course"] = course

        # 🔹 Bo‘limlarni kursga qarab chiqaramiz
        if course == "english":
            sections = {
                "kids": SECTIONS["kids"],
                "general": SECTIONS["general"],
                "certificate": SECTIONS["certificate"],
                "ielts": SECTIONS["ielts"],
            }
        elif course == "german":
            sections = {
                "kids": SECTIONS["kids"],
                "general": SECTIONS["general"],
                "certificate": SECTIONS["certificate"],
            }
        else:
            sections = {
                "kids": SECTIONS["kids"],
                "general": SECTIONS["general"],
                "certificate": SECTIONS["certificate"],
            }

        kb = [[InlineKeyboardButton(v, callback_data=f"section:{k}")] for k, v in sections.items()]
        await q.edit_message_text("🗂 Bo‘limni tanlang:", reply_markup=InlineKeyboardMarkup(kb))
        return

    # SECTION SELECT
    if data.startswith("section:"):
        section = data.split(":")[1]
        context.user_data["section"] = section
        course = context.user_data.get("course")

        if course in COURSES_WITH_LEVEL:
            kb = [[InlineKeyboardButton(v, callback_data=f"level:{k}")] for k, v in LEVELS.items()]
            await q.edit_message_text("📊 Darajangizni tanlang:", reply_markup=InlineKeyboardMarkup(kb))
        else:
            await q.edit_message_text("👤 Ismingizni kiriting (Masalan: Akmal Valiyev):")
            context.user_data["step"] = "full_name"
        return

    # LEVEL SELECT
    if data.startswith("level:"):
        level = data.split(":")[1]
        context.user_data["level"] = level
        await q.edit_message_text("👤 Ismingizni kiriting (Masalan: Akmal Valiyev):")
        context.user_data["step"] = "full_name"
        return

    # CONFIRM
    if data == "reg:confirm":
        txt = build_admin_text(context.user_data, update.effective_user)
        await q.edit_message_text("🎉 Tabriklaymiz! Ro‘yxatdan o‘tdingiz. Tez orada siz bilan bog‘lanamiz.")
        await context.bot.send_message(ADMIN_ID, txt, parse_mode=ParseMode.HTML)
        context.user_data.clear()
        return

    if data == "reg:cancel":
        context.user_data.clear()
        await q.edit_message_text("❌ Ro‘yxatdan o‘tish bekor qilindi.")
        return

# ---------------- MESSAGE HANDLER ----------------
async def msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    text = update.message.text.strip() if update.message.text else ""

    # FULL NAME
    if step == "full_name":
        if not valid_full_name(text):
            await update.message.reply_text("❌ Iltimos, to‘liq ism kiriting. Masalan: <b>Akmal Valiyev</b>", parse_mode=ParseMode.HTML)
            return
        context.user_data["full_name"] = text
        context.user_data["step"] = "age"
        await update.message.reply_text("🎂 Yoshingizni kiriting (Masalan: 18):")
        return

    # AGE
    if step == "age":
        if not valid_age(text):
            await update.message.reply_text("❌ Iltimos, yoshingizni to‘g‘ri kiriting (3-100).")
            return
        context.user_data["age"] = text
        context.user_data["step"] = "phone"

        # 🔹 Telefon raqamni qo‘lda yoki share contact bilan olish
        kb = ReplyKeyboardMarkup(
            [[KeyboardButton("📱 Raqamni ulashish", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await update.message.reply_text(
            "📱 Telefon raqamingizni kiriting (masalan: +998901234567) yoki pastdagi tugma orqali yuboring:",
            reply_markup=kb
        )
        return

    # PHONE (manual yozsa)
    if step == "phone" and text:
        phone = normalize_phone(text)
        if not phone:
            await update.message.reply_text("❌ Telefon raqam noto‘g‘ri. Masalan: +998901234567")
            return
        context.user_data["phone"] = phone

    # PHONE (agar contact yuborsa)
    if update.message.contact and step == "phone":
        phone = normalize_phone(update.message.contact.phone_number)
        if not phone:
            await update.message.reply_text("❌ Telefon raqam noto‘g‘ri. Masalan: +998901234567")
            return
        context.user_data["phone"] = phone

    if "phone" in context.user_data:
        # Show confirmation
        txt = build_admin_text(context.user_data, update.effective_user)
        kb = [
            [InlineKeyboardButton("✅ Tasdiqlash", callback_data="reg:confirm")],
            [InlineKeyboardButton("❌ Bekor qilish", callback_data="reg:cancel")],
        ]
        await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
        context.user_data.pop("step", None)  # stepni tozalash
        return

# ---------------- RUN ----------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(cb_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))
    app.add_handler(MessageHandler(filters.CONTACT, msg_handler))
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
