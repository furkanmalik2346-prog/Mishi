import asyncio
import json
import os
import sys
import random
import logging
from flask import Flask
from threading import Thread
from telegram import Update, ChatMemberUpdated, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import RetryAfter
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler, CallbackQueryHandler

# ---------------------------
# FLASK SERVER (Render 24/7 ke liye)
# ---------------------------
app = Flask('')

@app.route('/')
def home():
    return "FREAKY BOT IS ALIVE!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# ---------------------------
# CONFIGURATION
# ---------------------------
TOKENS = [
    "8615633587:AAE_iSNVgMHHu8oRuKZsdWM1o6AZhKPMnfs",
    "8115841323:AAFyAg3yJVl3hgbsvsGQlHZsIBNj9hdaX0o",
    "8550488602:AAF7e3hnMy5hZc2cZ3SquzSf-mxUcv7LMOM",
    "8799799389:AAGiNhvJvopHRfzIkRI4yAh6jgw5__Icmic",
    "7848194644:AAHWp5QnryYlybpIr-AIriJFZFMXjNP1lCk",
    "8635896580:AAFIR8hjy12CADPgYqCjq4WrqbyGgnoUJmA",
    "8707168681:AAHXnAUVknkW8nKjQyjcg1a9nPCcw8o46lk",
    "8527582256:AAFAiQjOUn_wiuBjj8X9Fw6cmTgtB4AL9Sc",
    "8586338886:AAECXijuZKVS1qqsOq8E-ch5GIS23E2PMFM",
    "8633221954:AAEFUIVuIO9UPvQ9PoikmUVH4L7Lr6WqiCM",
]

# Dono Owners ki IDs yahan hain
OWNERS = {8389568613, 8708136512} 
SUDO_FILE = "sudo_users.json"
GLOBAL_DELAY = 0.05

# State management
apps = []
bots = []
nc_tasks = {}
spam_tasks = {}
slider_tasks = {}

logging.basicConfig(level=logging.INFO)

# ---------------------------
# PERMISSION HELPERS
# ---------------------------
if os.path.exists(SUDO_FILE):
    with open(SUDO_FILE) as f:
        SUDO_USERS = set(json.load(f))
else:
    SUDO_USERS = set()

# Owners humesha sudo list mein rahenge
SUDO_USERS.update(OWNERS)

def is_owner_or_sudo(uid):
    return uid in OWNERS or uid in SUDO_USERS

def sudo_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if is_owner_or_sudo(update.effective_user.id):
            return await func(update, context)
        await update.message.reply_text("𝐆𝐔𝐋𝐀𝐌𝐈 𝐊𝐑 𝐏𝐇𝐋𝐄 𝐅𝐈𝐑 𝐒𝐔𝐃𝐎 𝐌𝐈𝐋𝐄𝐆𝐀 😂")
    return wrapper

# ---------------------------
# MENU & CALLBACKS
# ---------------------------
@sudo_only
async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛑 STOP ALL", callback_data='stop_all')],
        [
            InlineKeyboardButton("🚫 STOP SPAM", callback_data='stop_spam'),
            InlineKeyboardButton("🚫 STOP NC", callback_data='stop_nc')
        ],
        [InlineKeyboardButton("📊 STATUS", callback_data='status'), InlineKeyboardButton("🗑️ CLOSE", callback_data='close')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✨ **FREAKY BOT CONTROL PANEL** ✨", reply_markup=reply_markup, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_owner_or_sudo(query.from_user.id):
        await query.answer("Aukat mein reh!", show_alert=True)
        return
    
    await query.answer()
    if query.data == 'stop_all':
        await stopall(update, context)
    elif query.data == 'close':
        await query.message.delete()
    # Baki buttons ke logic yahan add karein...

# ---------------------------
# STOP LOGIC
# ---------------------------
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    for storage in [nc_tasks, spam_tasks, slider_tasks]:
        if chat_id in storage:
            for task in storage[chat_id]:
                task.cancel()
            del storage[chat_id]
    
    msg_obj = update.message if update.message else update.callback_query.message
    await msg_obj.reply_text("𝑂𝐾𝐼 𝑌𝐿𝐿 ¡! 🐣")

# ---------------------------
# MAIN STARTUP
# ---------------------------
def build_app(token):
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("menu", menu_cmd))
    app.add_handler(CommandHandler("start", menu_cmd))
    app.add_handler(CommandHandler("stopall", stopall))
    app.add_handler(CallbackQueryHandler(button_callback))
    # [Aapke baki saare ncdark, texts, etc. handlers yahan aayenge]
    return app

async def main():
    keep_alive() # Start Flask server
    for token in TOKENS:
        try:
            app = build_app(token)
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            bots.append(app.bot)
            apps.append(app)
            print(f"🚀 Bot Ready")
        except Exception as e:
            print(f"❌ Error: {e}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
