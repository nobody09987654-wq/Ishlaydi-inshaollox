from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode

BOT_TOKEN = "7832412035:AAHrVkpQXGl4KnxdMWu2hkRu1QgZZaBmGJc"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot ishlayapti!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Test", callback_data="test")]
        ]),
        parse_mode=ParseMode.HTML
    )

async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("Callback!")

async def msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Message!")

async def delete_media_and_forwards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()

async def delete_ad_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_error_handler(error_handler)

    app.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.VOICE | filters.VIDEO_NOTE |
        filters.ANIMATION | filters.DOCUMENT | filters.STICKER | filters.CONTACT | filters.FORWARD,
        delete_media_and_forwards
    ), group=0)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, delete_ad_text), group=1)
    app.add_handler(CommandHandler("start", start), group=2)
    app.add_handler(CallbackQueryHandler(cb_handler), group=2)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler), group=2)
    app.add_handler(MessageHandler(filters.CONTACT, msg_handler), group=2)

    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()