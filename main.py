from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

BOT_TOKEN = "7832412035:AAHrVkpQXGl4KnxdMWu2hkRu1QgZZaBmGJc"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Assalomu alaykum!\n\n"
        "<b>ITeach Academy</b> ga xush kelibsiz 🎓\n\n"
        "Bot ishlayapti!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Ro‘yxatdan o‘tish", callback_data="reg:start")]
        ]),
        parse_mode=ParseMode.HTML,
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()