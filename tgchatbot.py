import openai
import asyncio
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters


openai.api_key = "chatgpt_api"

TELEGRAM_BOT_TOKEN = "telegram_api" 

CHARACTER_PROMPTS = {
    "Character prompt write"
}

messages = [{"role": "system", "content": CHARACTER_PROMPTS}]

async def reply_in_parts(reply: str, update: Update):
    parts = re.split(r'(?<=[.?!])\s+', reply)
    for part in parts:
        part = part.strip()
        if part:
            await update.message.reply_text(part)
            await asyncio.sleep(1)

async def set_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_character, messages
    args = context.args
    if not args or args[0] not in CHARACTER_PROMPTS:
        keys = ", ".join(CHARACTER_PROMPTS.keys())
        await update.message.reply_text(f"Karakter seçimi: /karakter <{keys}> örn: /karakter serkan")
        return
    current_character = args[0]
    messages = [{"role": "system", "content": CHARACTER_PROMPTS[current_character]}]
    await update.message.reply_text(f"Karakter '{current_character}' olarak ayarlandı.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_name = user.first_name or "Anonim"
    user_message = update.message.text.strip()
    if not user_message:
        return
    print(f"{user_name}: {user_message}")
    messages.append({"role": "user", "content": user_message})
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.8,
            max_tokens=150
        )
        reply = response.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": reply})
        print(f"Bot: {reply}")
        await reply_in_parts(reply, update)
    except Exception as e:
        print("[Hata]:", e)
        await update.message.reply_text("Bir hata oluştu: " + str(e))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Merhaba! Sohbete hazırım. Karakteri değiştirmek için /karakter serkan gibi kullan.")

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("karakter", set_character))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot çalışıyor...")
app.run_polling()
