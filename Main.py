import asyncio
import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import RetryAfter
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler

# ---------------------------
# RENDER HOSTING (KEEP ALIVE)
# ---------------------------
app = Flask('')
@app.route('/')
def home(): return "FREAKY BOT IS RUNNING NON-STOP"
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
SPEED = 0.1  # 0.1 per sec
tasks = {"nc": {}, "spam": {}, "swipe": {}}
bots = []

def is_owner(uid): return uid in OWNERS

# ---------------------------
# AUTO-ADMIN (EK KO POWER, SAB ADMIN)
# ---------------------------
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
# NON-STOP LOOPS (0.1s SPEED)
# ---------------------------
async def nc_loop(bot, chat_id, text, emojis):
    i = 0
    while True:
        try:
            await bot.set_chat_title(chat_id, f"{text} {emojis[i % len(emojis)]}")
            i += 1
            await asyncio.sleep(SPEED)
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except: await asyncio.sleep(0.5)

async def spam_loop(bot, chat_id, msg):
    while True:
        try:
            await bot.send_message(chat_id, msg)
            await asyncio.sleep(SPEED)
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except: await asyncio.sleep(0.5)

async def swipe_loop(bot, chat_id, mid, texts):
    i = 0
    while True:
        try:
            await bot.send_message(chat_id, texts[i % len(texts)], reply_to_message_id=mid)
            i += 1
            await asyncio.sleep(SPEED)
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except: await asyncio.sleep(0.5)

# ---------------------------
# COMMAND HANDLERS
# ---------------------------
async def ncdark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return
    txt = " ".join(context.args) if context.args else "FREAKY"
    cid = update.effective_chat.id
    tasks["nc"][cid] = [asyncio.create_task(nc_loop(b, cid, txt, ["🔥","🌑","⚡"])) for b in bots]
    await update.message.reply_text(f"🚀 NC Ultra Speed (0.1s) On!")

async def texts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return
    txt = " ".join(context.args) if context.args else "FREAKY ON TOP 🔥"
    cid = update.effective_chat.id
    tasks["spam"][cid] = [asyncio.create_task(spam_loop(b, cid, txt)) for b in bots]
    await update.message.reply_text(f"🔥 Spam Ultra Speed (0.1s) On!")

async def swipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id) or not update.message.reply_to_message: return
    cid = update.effective_chat.id
    mid = update.message.reply_to_message.message_id
    tasks["swipe"][cid] = [asyncio.create_task(swipe_loop(b, cid, mid, ["BKL","CHUD GYA","GULAMI KR"])) for b in bots]
    await update.message.reply_text(f"🌊 Swipe Ultra Speed (0.1s) On!")

async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return
    cid = update.effective_chat.id
    for cat in tasks:
        if cid in tasks[cat]:
            for t in tasks[cat][cid]: t.cancel()
            del tasks[cat][cid]
    await update.message.reply_text("𝑂𝐾𝐼 𝑌𝐿𝐿 ¡! 🐣")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return
    menu = "𝐓𝙷𝙴  𝐅𝚁𝙴𝙰𝙺𝚈  𝐌𝚄𝐒𝙴\n\n/ncdark - 0.1s NC\n/texts - 0.1s Spam\n/swipe - 0.1s Swipe\n/stopall - Stop"
    await update.message.reply_text(menu)

# ---------------------------
# MAIN STARTUP
# ---------------------------
def build_app(token):
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ncdark", ncdark))
    app.add_handler(CommandHandler("texts", texts))
    app.add_handler(CommandHandler("swipe", swipe))
    app.add_handler(CommandHandler("stopall", stopall))
    app.add_handler(ChatMemberHandler(auto_admin, ChatMemberHandler.MY_CHAT_MEMBER))
    return app

async def main():
    keep_alive()
    for t in TOKENS:
        try:
            a = build_app(t)
            await a.initialize(); await a.start(); await a.updater.start_polling()
            bots.append(a.bot)
        except: pass
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
