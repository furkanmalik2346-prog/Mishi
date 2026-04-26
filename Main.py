import asyncio
import os
import logging
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler, CallbackQueryHandler

# ---------------------------
# FLASK SERVER (For Render 24/7)
# ---------------------------
app = Flask('')
@app.route('/')
def home(): return "FREAKY BOT SYSTEM IS ALIVE"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# ---------------------------
# CONFIGURATION
# ---------------------------
TOKENS = [
    "8615633587:AAE_iSNVgMHHu8oRuKZsdWM1o6AZhKPMnfs", "8115841323:AAFyAg3yJVl3hgbsvsGQlHZsIBNj9hdaX0o",
    "8550488602:AAF7e3hnMy5hZc2cZ3SquzSf-mxUcv7LMOM", "8799799389:AAGiNhvJvopHRfzIkRI4yAh6jgw5__Icmic",
    "7848194644:AAHWp5QnryYlybpIr-AIriJFZFMXjNP1lCk", "8635896580:AAFIR8hjy12CADPgYqCjq4WrqbyGgnoUJmA",
    "8707168681:AAHXnAUVknkW8nKjQyjcg1a9nPCcw8o46lk", "8527582256:AAFAiQjOUn_wiuBjj8X9Fw6cmTgtB4AL9Sc",
    "8586338886:AAECXijuZKVS1qqsOq8E-ch5GIS23E2PMFM", "8633221954:AAEFUIVuIO9UPvQ9PoikmUVH4L7Lr6WqiCM"
]

OWNERS = {8389568613, 8708136512}
GLOBAL_DELAY = 0.05
nc_tasks, spam_tasks, slider_tasks = {}, {}, {}
apps, bots = [], []

logging.basicConfig(level=logging.ERROR)

def is_owner(uid): return uid in OWNERS

# ---------------------------
# AUTO-ADMIN LOGIC
# ---------------------------
async def auto_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    me = await context.bot.get_me()
    status = update.my_chat_member.new_chat_member
    
    if status.status == "administrator" and status.can_promote_members:
        for b_obj in bots:
            if b_obj.id != me.id:
                try:
                    await chat.promote_member(
                        b_obj.id, can_manage_chat=True, can_change_info=True,
                        can_delete_messages=True, can_invite_users=True,
                        can_restrict_members=True, can_pin_messages=True
                    )
                except: pass

# ---------------------------
# SPAM / NC / SWIPE LOGIC
# ---------------------------
async def nc_loop(bot, chat_id, names):
    while True:
        for name in names:
            try:
                await bot.set_chat_title(chat_id, name)
                await asyncio.sleep(GLOBAL_DELAY)
            except Exception: await asyncio.sleep(1)

async def spam_loop(bot, chat_id, text):
    while True:
        try:
            await bot.send_message(chat_id, text)
            await asyncio.sleep(GLOBAL_DELAY)
        except Exception: await asyncio.sleep(1)

# ---------------------------
# COMMANDS
# ---------------------------
async def start_nc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return
    chat_id = update.effective_chat.id
    names = context.args if context.args else ["FREAKY", "ON", "TOP"]
    nc_tasks[chat_id] = []
    for b in bots:
        task = asyncio.create_task(nc_loop(b, chat_id, names))
        nc_tasks[chat_id].append(task)
    await update.message.reply_text("🚀 NC Start Ho Gaya!")

async def start_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return
    chat_id = update.effective_chat.id
    text = " ".join(context.args) if context.args else "FREAKY BRAND 🔥"
    spam_tasks[chat_id] = []
    for b in bots:
        task = asyncio.create_task(spam_loop(b, chat_id, text))
        spam_tasks[chat_id].append(task)
    await update.message.reply_text("🔥 Spamming Start!")

async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return
    chat_id = update.effective_chat.id
    for d in [nc_tasks, spam_tasks, slider_tasks]:
        if chat_id in d:
            for t in d[chat_id]: t.cancel()
            del d[chat_id]
    msg = update.message if update.message else update.callback_query.message
    await msg.reply_text("𝑂𝐾𝐼 𝑌𝐿𝐿 ¡! 🐣")

async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return
    kbd = [[InlineKeyboardButton("🛑 STOP ALL", callback_data='stop_all')],
           [InlineKeyboardButton("📊 STATUS", callback_data='status')]]
    await update.message.reply_text("✨ **FREAKY MENU**", reply_markup=InlineKeyboardMarkup(kbd))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if q.data == 'stop_all': await stopall(update, context)
    await q.answer()

# ---------------------------
# MAIN STARTUP
# ---------------------------
def build_app(token):
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("menu", menu_cmd))
    application.add_handler(CommandHandler("nc", start_nc))
    application.add_handler(CommandHandler("spam", start_spam))
    application.add_handler(CommandHandler("stopall", stopall))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(ChatMemberHandler(auto_admin_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    return application

async def main():
    keep_alive()
    for t in TOKENS:
        try:
            a = build_app(t)
            await a.initialize()
            await a.start()
            await a.updater.start_polling()
            bots.append(a.bot)
        except: pass
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
