import asyncio
import os
import random
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.error import RetryAfter
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler

# ---------------------------
# RENDER HOSTING LOGIC
# ---------------------------
app = Flask('')
@app.route('/')
def home(): return "FREAKY SYSTEM IS STABLE"
def run(): app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
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
SPEED = 0.1
# Is flag se stop command kaam karega
running_chats = {} 

bots = []

# ---------------------------
# NON-STOP SPEED LOOPS WITH STOP CHECK
# ---------------------------
async def nc_loop(bot, chat_id, text):
    while running_chats.get(chat_id):
        try:
            emo = random.choice(["🔥", "🌑", "⚡", "😈", "✨", "🪐"])
            await bot.set_chat_title(chat_id, f"{text} {emo}")
            await asyncio.sleep(SPEED)
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(0.5)

async def spam_loop(bot, chat_id, msg):
    while running_chats.get(chat_id):
        try:
            await bot.send_message(chat_id, msg)
            await asyncio.sleep(SPEED)
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(0.5)

# ---------------------------
# COMMAND HANDLERS
# ---------------------------
async def ncdark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNERS: return
    cid = update.effective_chat.id
    txt = " ".join(context.args) or "FREAKY"
    running_chats[cid] = True
    for b in bots: asyncio.create_task(nc_loop(b, cid, txt))
    await update.message.reply_text("🚀 NC Non-stop Started (0.1s)!")

async def texts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNERS: return
    cid = update.effective_chat.id
    txt = " ".join(context.args) or "FREAKY ON TOP"
    running_chats[cid] = True
    for b in bots: asyncio.create_task(spam_loop(b, cid, txt))
    await update.message.reply_text("🔥 Spam Non-stop Started (0.1s)!")

async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNERS: return
    cid = update.effective_chat.id
    running_chats[cid] = False # Flag off karte hi loop ruk jayega
    await update.message.reply_text("𝑂𝐾𝐼 𝑌𝐿𝐿 ¡! 🐣 (Stopped everything)")

async def auto_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    me = await context.bot.get_me()
    status = update.my_chat_member.new_chat_member
    if status.status == "administrator" and status.can_promote_members:
        for b in bots:
            if b.id != me.id:
                try:
                    await chat.promote_member(b.id, can_manage_chat=True, can_change_info=True, can_delete_messages=True, can_invite_users=True, can_restrict_members=True, can_pin_messages=True, can_promote_members=True)
                except: pass

# ---------------------------
# MAIN STARTUP
# ---------------------------
async def main():
    keep_alive()
    for token in TOKENS:
        try:
            app = Application.builder().token(token).build()
            app.add_handler(CommandHandler("ncdark", ncdark))
            app.add_handler(CommandHandler("texts", texts))
            app.add_handler(CommandHandler("stopall", stopall))
            app.add_handler(ChatMemberHandler(auto_admin, ChatMemberHandler.MY_CHAT_MEMBER))
            
            await app.initialize()
            await app.start()
            await app.updater.start_polling(drop_pending_updates=True)
            bots.append(app.bot)
        except Exception as e: print(f"Error: {e}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
