import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# Mengambil token & API key dari environment variables di Render
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Inisialisasi Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

# Logging untuk memantau status bot
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

user_chats = {}

def get_or_create_chat(user_id: int):
    if user_id not in user_chats:
        user_chats[user_id] = client.chats.create(
            model="gemini-2.5-flash",
            config={
                "system_instruction": (
                    "Kamu adalah OpenClaw Agent, asisten AI yang terhubung ke Telegram. "
                    "Jawablah dengan cerdas, ramah, dan solutif."
                ),
            }
        )
    return user_chats[user_id]

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    get_or_create_chat(user_id)
    await update.message.reply_text("🤖 **OpenClaw Agent Aktif!**\nAda yang bisa saya bantu?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        chat = get_or_create_chat(user_id)
        response = chat.send_message(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Terjadi masalah saat memproses pesan.")

if __name__ == '__main__':
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        print("❌ Error: TELEGRAM_BOT_TOKEN atau GEMINI_API_KEY belum diatur!")
        exit(1)

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 OpenClaw Agent berjalan...")
    app.run_polling()
