import asyncio
import os
import random
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.error import RetryAfter
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler

# ---------------------------
# RENDER HOSTING (PORT BIND)
# ---------------------------
app = Flask('')
@app.route('/')
def home(): return "SYSTEM ONLINE"
def run(): app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# ---------------------------
# CONFIG (TERI ORIGINAL IDS)
# ---------------------------
TOKENS = [
    "8615633587:AAE_iSNVgMHHu8oRuKZsdWM1o6AZhKPMnfs", "8115841323:AAFyAg3yJVl3hgbsvsGQlHZsIBNj9hdaX0o",
    "8550488602:AAF7e3hnMy5hZc2cZ3SquzSf-mxUcv7LMOM", "8799799389:AAGiNhvJvopHRfzIkRI4yAh6jgw5__Icmic",
    "7848194644:AAHWp5QnryYlybpIr-AIriJFZFMXjNP1lCk", "8635896580:AAFIR8hjy12CADPgYqCjq4WrqbyGgnoUJmA",
    "8707168681:AAHXnAUVknkW8nKjQyjcg1a9nPCcw8o46lk", "8527582256:AAFAiQjOUn_wiuBjj8X9Fw6cmTgtB4AL9Sc",
    "8586338886:AAECXijuZKVS1qqsOq8E-ch5GIS23E2PMFM", "8633221954:AAEFUIVuIO9UPvQ9PoikmUVH4L7Lr6WqiCM"
]

OWNERS = {8389568613, 8708136512}
GLOBAL_DELAY = 0.1 # 🔥 0.1 Per Second Speed
running_tasks = {} # Isse stop command kaam karega
bots = []

# --- TERI SCRIPT KE ORIGINAL PATTERNS ---
DARK_EMOJIS = ["🕳️", "🌑", "👣", "🗝️", "🧬", "🔌", "⬛", "🦾", "📜", "🕯️", "🍷", "🥀", "🖤", "🕸️", "🗡️", "🎱", "🐦‍⬛", "🔮", "🌑", "🪄", "🌝", "🌚", "🌜", "🌛", "🌙", "⭐", "🌟", "✨", "🪐", "🌍", "🌠", "🌌", "☄️", "🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
SWIPE_TEXTS = ["𝗧𝗘𝗥𝗜 𝗠𝗞𝗖 𝗦𝗔𝗦𝗧𝗜 𝗛𝗔𝗜 😡", "𝗖𝗛𝗟 𝗚𝗨𝗟𝗔𝗠𝗜 𝗞𝗥 𝗧𝗔𝗧𝗧𝗘 😆", "𝗘𝗞 𝗟𝗔𝗔‌𝗧 𝗠𝗜𝗘 𝗟𝗡𝗗 𝗖𝗛𝗔𝗧𝗧𝗔 𝗙𝗜𝗥𝗘𝗚𝗔 😆"]

# ---------------------------
# LOOPS (NON-STOP 0.1s)
# ---------------------------
async def nc_loop(bot, chat_id, text):
    i = 0
    while running_tasks.get(chat_id):
        try:
            emo = DARK_EMOJIS[i % len(DARK_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} {emo}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except: await asyncio.sleep(0.5)

async def spam_loop(bot, chat_id, msg):
    while running_tasks.get(chat_id):
        try:
            await bot.send_message(chat_id, msg)
            await asyncio.sleep(GLOBAL_DELAY)
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except: await asyncio.sleep(0.5)

async def swipe_loop(bot, chat_id, target_id):
    i = 0
    while running_tasks.get(chat_id):
        try:
            msg = SWIPE_TEXTS[i % len(SWIPE_TEXTS)]
            await bot.send_message(chat_id, msg, reply_to_message_id=target_id)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except: await asyncio.sleep(0.5)

# ---------------------------
# COMMANDS (ORIGINAL NAMES)
# ---------------------------
async def ncdark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNERS: return
    cid = update.effective_chat.id
    txt = " ".join(context.args) or "FREAKY"
    running_tasks[cid] = True
    for b in bots: asyncio.create_task(nc_loop(b, cid, txt))
    await update.message.reply_text("🚀 NC DARK STARTED @ 0.1s")

async def texts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNERS: return
    cid = update.effective_chat.id
    txt = " ".join(context.args) or "FREAKY ON TOP 🔥"
    running_tasks[cid] = True
    for b in bots: asyncio.create_task(spam_loop(b, cid, txt))
    await update.message.reply_text("🔥 SPAM STARTED @ 0.1s")

async def swipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNERS or not update.message.reply_to_message:
        return await update.message.reply_text("Kisi message pe reply karke maar bkl!")
    cid = update.effective_chat.id
    mid = update.message.reply_to_message.message_id
    running_tasks[cid] = True
    for b in bots: asyncio.create_task(swipe_loop(b, cid, mid))
    await update.message.reply_text("🌊 SWIPE STARTED @ 0.1s")

async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNERS: return
    running_tasks[update.effective_chat.id] = False
    await update.message.reply_text("𝑂𝐾𝐼 𝑌𝐿𝐿 ¡! 🐣")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in OWNERS:
        from main_menu import HELP_TEXT # Agar help text badi hai
        await update.message.reply_text("𝐓𝙷𝙴  𝐅𝚁𝙴𝙰𝙺𝚈  𝐌𝚄𝐒𝙴...\n/ncdark\n/texts\n/swipe\n/stopall")

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
# MAIN
# ---------------------------
async def main():
    keep_alive()
    for token in TOKENS:
        try:
            app = Application.builder().token(token).build()
            app.add_handler(CommandHandler("ncdark", ncdark))
            app.add_handler(CommandHandler("texts", texts))
            app.add_handler(CommandHandler("swipe", swipe))
            app.add_handler(CommandHandler("stopall", stopall))
            app.add_handler(CommandHandler("help", help_cmd))
            app.add_handler(ChatMemberHandler(auto_admin, ChatMemberHandler.MY_CHAT_MEMBER))
            
            await app.initialize()
            await app.start()
            await app.updater.start_polling(drop_pending_updates=True)
            bots.append(app.bot)
        except Exception as e: print(f"Error: {e}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
