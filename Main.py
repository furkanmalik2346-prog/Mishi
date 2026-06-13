# main.py - Complete Script Configured for Render/Railway Deployment
import asyncio
import json
import os
import sys
import random
import logging
from threading import Thread
from flask import Flask
from datetime import datetime, timezone, timedelta
from telegram import Update, ChatMemberUpdated, ChatMember
from telegram.error import RetryAfter
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler

# ---------------------------
# BACKGROUND WEB SERVER CONFIG
# ---------------------------
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "🚀 FREAKY BOT V4 IS RUNNING LIVE 24/7! 🪐"

def run_flask():
    # Render externally passes the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

# ---------------------------
# YOUR 10 BOT TOKENS
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

OWNER_ID = 8389568613
SUDO_FILE = "sudo_users.json"

if os.path.exists(SUDO_FILE):
    with open(SUDO_FILE) as f:
        SUDO_USERS = set(json.load(f))
else:
    SUDO_USERS = {OWNER_ID}

def save_sudo():
    with open(SUDO_FILE, "w") as f:
        json.dump(list(SUDO_USERS), f)

apps = []
bots = []
bots_info = []
nc_tasks = {}
spam_tasks = {}
slider_tasks = {}
GLOBAL_DELAY = 0.05

STOP_MESSAGE = "𝑂𝐾𝐼 𝑌𝐿𝐿 ¡! 🐣"
ADMIN_MESSAGE = "ꪖᦔꪑ꠸ꪀ ꫝꫀ᥅ꫀ ~ 🪽"
BYE_MESSAGE = "𝐆𝐀𝐌𝐄 𝐎𝐕𝐄𝐑 !! 📌"
GREETING_MESSAGE = "ꪑ꠸ꫀ ꪖᧁꪗꪖ 🫣"

logging.basicConfig(level=logging.INFO)

def is_owner_or_sudo(uid):
    return uid == OWNER_ID or uid in SUDO_USERS

def owner_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id == OWNER_ID:
            return await func(update, context)
        await update.message.reply_text("❌ Only owner can use this command!")
    return wrapper

def sudo_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if is_owner_or_sudo(update.effective_user.id):
            return await func(update, context)
        await update.message.reply_text("𝐆𝐔𝐋𝐀𝐌𝐈 𝐊𝐑 𝐏𝐇𝐋𝐄 𝐅𝐈𝐑 𝐒𝐔𝐃𝐎 𝐌𝐈𝐋𝐄𝐆𝐀 😂")
    return wrapper

# Emoji & Word Lists
DARK_EMOJIS = ["🕳️", "🌑", "👣", "🗝️", "🧬", "🔌", "⬛", "🦾", "📜", "🕯️", "🍷", "🥀", "🖤", "🕸️", "🗡️", "🎱", "🐦‍⬛", "🔮", "🌑", "🪄", "🌝", "🌚", "🌜", "🌛", "🌙", "⭐", "🌟", "✨", "🪐", "🌍", "🌠", "🌌", "☄️", "🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
HAND_EMOJIS = ["👀", "👁️", "👄", "🫦", "👅", "👃🏻", "👂🏻", "🦻🏻", "🦶🏻", "🦵🏻", "🦿", "🦾", "💪🏻", "👏🏻", "👍🏻", "👎🏻", "🫶🏻", "🙌🏻", "👐🏻", "🤲🏻", "🤜🏻", "🤛🏻", "✊🏻", "👊🏻", "🫳🏻", "🫴🏻", "🫱🏻", "🫲🏻", "🫸🏻", "🫷🏻", "👋🏻", "🤚🏻", "🖐🏻", "✋🏻", "🖖🏻", "🤟🏻", "🤘🏻", "✌🏻", "🤞🏻", "🫰🏻", "🤙🏻", "🤌🏻", "🤏🏻", "👌🏻", "🫵🏻", "👉🏻", "👈🏻", "☝🏻", "👆🏻", "👇🏻", "🖕🏻", "✍🏻", "🤳🏻", "🙏🏻", "💅🏻", "🤝🏼", "🌘"]
MARVEL_EMOJIS = ["🛡️", "🇺🇸", "🎖️", "🦾", "🚀", "⚡", "🤖", "⚡", "🔨", "🌩️", "🔱", "🕷️", "🕶️", "🔫", "🥀", "🏹", "🎯", "🦅", "🧪", "☢️", "👊", "🟢", "💎", "🤖", "🟡"]
MAGIC_EMOJIS = ["🧪", "⚗️", "📜", "💎", "🕳️", "🌑", "🧿", "🐦‍⬛", "🌀", "⚡", "🪄", "🧿", "🕯️", "📜", "🏛️", "🖤", "✥", "♱", "⚖︎", "∞", "𖦹"]
NATURE_EMOJIS = ["💐", "🌹", "🥀", "🌺", "🌷", "🪷", "🌸", "💮", "🏵️", "🪻", "🌻", "🌼", "🍂", "🍁", "🍄", "🌾", "🌿", "🌱", "🍃", "☘️", "🍀", "🪴", "🌵", "🌴", "🪾", "🌳", "🌲", "🪵", "🪹", "🪺"]
FOOD_EMOJIS = ["🍧", "🧋", "🧃", "🥛", "🍿", "🧊", "🍵", "☕", "🍻", "🍺", "🧉", "🫖", "🍾", "🍷", "🥃", "🫗", "🍸", "🍹", "🍶", "🥢", "🥂", "🧈", "🧁", "🍭", "🍬", "🍫", "🍨", "🍡", "🍙", "🍥", "🥠", "🥟", "🍛", "🍤", "🍜", "🦪", "🍚", "🥣", "🥫", "🌯"]
FACE_EMOJIS = ["☺️", "😌", "🙂‍↕️", "🙂‍↔️", "😏", "🤤", "😋", "😛", "😝", "😜", "🤪", "😔", "🥺", "😬", "😑", "😐", "😶", "😶‍🌫️", "🫥", "🤐", "🫡", "🤔", "🤫", "🫢", "🤭", "🥱", "🤗", "🫣", "😱", "🤨", "🧐", "😒", "🙄", "😮‍💨", "😤", "😠", "😡", "🤬", "😞", "😓", "😟", "😥", "😢", "☹️", "🙁", "🫤", "😕", "😰", "😨", "😧", "😦", "😮", "😯", "😲", "🤯", "🫨", "😵‍💫", "😵", "😫", "🥴", "🥶", "🥵"]
HOBBY_EMOJIS = ["🃏", "🪄", "🎩", "📷", "🀄", "🎴", "🎰", "📸", "🖼️", "🎨", "🫟", "🖌️", "🖍️", "🪡", "🧵", "🧶", "🎹", "🎷", "🎺", "🎸", "🪕", "🎻", "🪉", "🪘", "🥁", "🪇", "🪈", "🪗", "🎤", "🎧", "🎚️", "🎛️", "🎙️", "📼", "📻", "📺", "📹", "📽️", "🎥", "🎞️", "🎬", "🎭", "🎫", "🎟️"]
TECH_EMOJIS = ["🔋", "🪫", "🖲️", "💽", "💾", "💿", "📀", "🖥️", "💻", "⌨️", "🖨️", "🖱️", "🪙", "💎", "💸", "💵", "💴", "💶", "💷", "💳", "💰", "🧾", "🧮", "⚖️", "🛒", "🛍️", "💡", "🕯️", "🔦", "🏮", "🧱", "🪟", "🪞", "🚪", "🚿", "🛁", "🚽", "🧻", "🪠", "🧸", "🪆", "🧷", "🪢", "🧹", "🧴", "🧽", "🧼", "🪥", "🪒", "🪮", "🧺", "🧦", "🧤", "🧣", "👖"]
ANIMAL_EMOJIS = ["🪼", "🐚", "🦋", "🐞", "🐝", "🐛", "🪱", "🦠", "🐾", "🫧", "🪸", "🦪", "🪼", "🐙", "🦑", "🐡", "🐠", "🐟", "🐳", "🐋", "🐬", "🦈", "🦭", "🐧", "🦃", "🐦‍🔥", "🦚", "🦩", "🪿", "🦆", "🦢", "🦤", "🕊️", "🦜", "🦉", "🦅", "🐥", "🐤", "🐣", "🐓", "🐦", "🪶", "🪽", "🦇", "🦦", "🦔", "🦡", "🦨", "🐅", "🐆", "🦒", "🦏", "🦣", "🐘", "🦓", "🦘", "🦥", "🦬", "🐃", "🐏", "🐂", "🐄", "🐎", "🐈", "🐩"]

TYPENC_WORDS = ["𝗧𝗔𝗧𝗧𝗘", "𝗚🇺𝗟𝗔𝗠", "𝗠𝗔𝗗𝗔𝗥🇨🇭🇴🇩", "𝗕𝗛🇪🇳𝗞🇱🇳🇩", "𝗧𝗠𝗞🇨", "𝗧𝗠𝗞𝗕", "狠𝗡🇩𝗬", "𝗚𝗔𝗥🇪🇪𝗕", "𝗠🇮𝗦𝗧🇮 𝗞🇪 🇱𝗔🇩𝗞🇪", "🇬🇳🇩🇺", "🇨🇭🇦🇵🇷🇮", "🇨🇭🇲🇷", "𝗕𝗦🇩𝗞", "𝗞🇪🇪🇩🇪", "🇨🇭🇺🇩", "𝗧🇧𝗞🇱", "𝗛🇦🇷🇦𝗠𝗞🇭🇴𝗥", "𝗥🇷 𝗠🇹 𝗞🇷"]
ALEXA_TEXTS = ["𝗔𝗟🇪𝗫𝗔 🇮𝗦𝗦 𝗠🇨 𝗞🇮 𝗠🇦🇦 𝗞🇪 🇳🇴🇹🇪🇸 🇩🇮𝗞🇭🇦🇴 🙁", "𝗔index🇪𝗫𝗔 🇮𝗦𝗞🇮 🇧🇭🇪🇳 🇨🇭🇴🇩 🇩🇴 🌙", "𝗔index🇪𝗫𝗔 🇮𝗦(𝗞🇪) 🇧🇦‌🇦🇵 𝗞🇮 🇬🇳🇩 𝗠🇮🇪 奠🇦🇹🇭 🇩🇦‌🇦🇱 🇩🇴 😆", "𝗔index🇪𝗫𝗔 🇮𝗦𝗞🇦 🇬🇦𝗠🇪 🇴🇻🇪🇷 𝗞🇦 🇻🇮🇩🇪🇴 🇩🇴🇳🇪 𝗞🇷🇴 🥹"]
ANIMAL_TEXTS = ["𝗢𝗬🇪 𝗧🇲🇰🇨 𝗠🇮🇪 🇬🇴𝗥🇮🇱🇱🇦  🦍", "𝗢𝗬🇪 𝗧🇪🇷🇮 🇧🇭🇪🇳 𝗞🇮 🇨🇭🇺🇹 𝗠🇮🇪 🇬🇭🇴🇩🇦 🐎", "𝗢𝗬🇪 𝗧🇪🇷🇪 🇧🇦🇦🇵 𝗞🇮 🇬🇳🇩 𝗠🇮🇪 𝗞🇦🇳🇬🇦🇷🇴🇴 🦘", "𝗢𝗬🇪 𝗧🇪🇷🇮 🇬🇳🇩 𝗠🇮🇪 🇨🇦🇲🇪🇱 🐪", "𝗢𝗬🇪 𝗧🇺 𝗝🇦🇳𝗪🇦🇷🇴 𝗦🇪 🇨🇭🇺🇩 🇬𝗬🇦 ? 😆"]
SWIPE_TEXTS = ["𝗧🇪🇷🇮 𝗠🇰🇨 𝗦🇦🇸𝗧🇮 𝗛🇦🇮 🇧🇦🇦𝗧 𝗞🇭🇹🇲 😡", "🇨🇭𝗟 🇬🇺🇱🇦🇲🇮 𝗞🇷 𝗧🇦𝗧𝗧🇪 😆", "🇨🇭🇮🇩🇮𝗬🇦 🇨🇭🇦🇩🇮 🇵🇭🇦🇦‌🇩 🇵🇪 🇺🇸🇳🇪 🇩🇮archive 𝗠🇺🇹 𝗧🇲𝗞🇨 😆", "🇪𝗞 裝🇦🇦‌🇹 𝗠🇮🇪 奠🇳🇩 🇨🇭🇦𝗧𝗧🇦 🇫🇮🇷🇪🇬🇦 🇧🇸🇩𝗞 😆"]

TEXTS_PATTERN = "{text}  𝑶𝒀𝑬 𝑩𝑲🇱 𝑻𝑬𝑹𝑰 𝑴𝑨𝑨 𝑲𝑨 𝑲𝑯𝑨𝑺𝑨𝑴 𝑯𝑼 𝑨𝑼𝑲𝑨🇹 𝑴𝑰𝑬 𝑹𝑯 𝑹𝑵𝑫𝒀 𝑷𝑼𝑻𝑹𝑨 ☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲\\~   "
TEXTS_REPEAT = 10
SHAYARI_PATTERN = "𝙏𝙄𝙆 𝙏𝙄𝙆 𝘾𝙃𝙇𝙏𝘼 𝙂𝙃𝙊𝘿𝘼 {text} 𝙆𝙄 𝘽𝙃𝙀𝙉 𝙆𝘼 𝙇𝙊𝘿𝘼 ╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍ "
SHAYARI_REPEAT = 10
SONGY_PATTERN = "{text} 𝗗𝗮𝗹𝗹𝗲!\n𝗕𝗲𝘁𝗮 𝗗𝗮𝗹𝗹𝗲 𝗕𝗲𝗻𝗶 𝗕𝗮𝗮𝗽 𝗧𝗲𝗿𝗮 𝗡𝗮𝗹𝗹𝗮 𝗛𝗮𝗶\n𝗟*🇩🇦 𝗛𝗼𝗼𝗸auto 𝗠𝗲𝗿𝗮, 𝗠𝗮𝗺𝘁𝗮 𝗠𝗲𝗿𝗶 🇨🇭𝗮𝗹𝗹𝗮 𝗛𝗮𝗶..."
CUSTOM_PATTERN = "{text}  ⩇⩇:⩇⩇ {kaomoji}"
CUSTOM_KAOMOJI = ["(◕‿◕)", "(✿◠‿◠)", "(◔‿◔)", "(◡‿◡✿)"]

# NC Loops Functions
async def ncdark_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = DARK_EMOJIS[i % len(DARK_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} ＴＭＫＣ ＲＮＤＹＫＥ⪩ {emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def tmkcnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = HAND_EMOJIS[i % len(HAND_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} ⭞ ᴛᴍᴋᴄ ￫ {emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def evonc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = HAND_EMOJIS[i % len(HAND_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} 𝙂𝙐𝙇𝘼𝙈﹏{emoji}﹏")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def marvelnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = MARVEL_EMOJIS[i % len(MARVEL_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} 𝙏𝘽𝙆𝘾 ᯓ {emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def magicnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = MAGIC_EMOJIS[i % len(MAGIC_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} 𝙍𝙉𝘿𝙔 𝘽𝘼𝙇𝘼𝙆⁀➴༯ {emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def sportnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = MARVEL_EMOJIS[i % len(MARVEL_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} 𝙏𝙀𝙍🇮 𝙂𝙉🇩 𝙈🇮🇪 ≯ {emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def lndnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = NATURE_EMOJIS[i % len(NATURE_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} 𝘾𝙃𝙐𝘿 𓀐𓂺 {emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def ncspeed_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = FOOD_EMOJIS[i % len(FOOD_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} 𝙏🇪🇷🇮 𝙈🇦🇦 🇨🇭🇺🇩🇦𝙆🇦🇩 ≫ {emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def emognc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = FACE_EMOJIS[i % len(FACE_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} 𝙆𝙀🇪🇩🇪 𝘼🇺𝙆🇦𝗧 𝘽🇳🇦⁀➴♡ {emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def yournc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = HOBBY_EMOJIS[i % len(HOBBY_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} 𓆩 {emoji} 𓆪")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def customnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = FACE_EMOJIS[i % len(FACE_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} જ⁀➴ {emoji} ִֶָ𓂃 ࣪ ִֶָ🦢་༘࿐")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def typenc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            word = TYPENC_WORDS[i % len(TYPENC_WORDS)]
            await bot.set_chat_title(chat_id, f"{text} {word} ִֶָ࣪𓏲ᥫ᭡ ₊ ⊹ ˑ ִ ֶ 𓂃")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def flashnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = TECH_EMOJIS[i % len(TECH_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} ═══ {emoji} ═══")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def foxync_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = ANIMAL_EMOJIS[i % len(ANIMAL_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} 🇨🇭🇺🇩 𝗞🇷 𝗗🇦𝗙🇦🇳~{emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

# Spam Loops
async def texts_spam_loop(bot, chat_id, text):
    message = (TEXTS_PATTERN.format(text=text) + "\n") * TEXTS_REPEAT
    while True:
        try:
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def shayari_spam_loop(bot, chat_id, text):
    message = (SHAYARI_PATTERN.format(text=text) + "\n") * SHAYARI_REPEAT
    while True:
        try:
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def songy_spam_loop(bot, chat_id, text):
    message = SONGY_PATTERN.format(text=text)
    while True:
        try:
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def custom_spam_loop(bot, chat_id, text):
    while True:
        try:
            kaomoji = random.choice(CUSTOM_KAOMOJI)
            message = CUSTOM_PATTERN.format(text=text, kaomoji=kaomoji)
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

# Slider Loops
async def make_slider_loop(texts, bot, chat_id, target_msg_id):
    i = 0
    while True:
        try:
            await bot.send_message(chat_id=chat_id, text=texts[i % len(texts)], reply_to_message_id=target_msg_id)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

# Member Handler
async def handle_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result: ChatMemberUpdated = update.my_chat_member
    if result.chat.type not in ["group", "supergroup"]: return
    old = result.old_chat_member
    new = result.new_chat_member
    if old.status in [ChatMember.LEFT, ChatMember.BANNED] and new.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]:
        await context.bot.send_message(chat_id=result.chat.id, text=GREETING_MESSAGE)
    elif old.status == ChatMember.MEMBER and new.status == ChatMember.ADMINISTRATOR:
        await context.bot.send_message(chat_id=result.chat.id, text=ADMIN_MESSAGE)

# Command Definitions
@sudo_only
async def ncdark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /ncdark <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(ncdark_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ ncdark started for: {text}")

@sudo_only
async def tmkcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /tmkcnc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(tmkcnc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ tmkcnc started for: {text}")

@sudo_only
async def evonc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /evonc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(evonc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ evonc started for: {text}")

@sudo_only
async def marvelnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /marvelnc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(marvelnc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ marvelnc started for: {text}")

@sudo_only
async def magicnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /magicnc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(magicnc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ magicnc started for: {text}")

@sudo_only
async def sportnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /sportnc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(sportnc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ sportnc started for: {text}")

@sudo_only
async def lndnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /lndnc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(lndnc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ lndnc started for: {text}")

@sudo_only
async def ncspeed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /ncspeed <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(ncspeed_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ ncspeed started for: {text}")

@sudo_only
async def emognc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /emognc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(emognc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ emognc started for: {text}")

@sudo_only
async def yournc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /yournc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(yournc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ yournc started for: {text}")

@sudo_only
async def customnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /customnc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(customnc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ customnc started for: {text}")

@sudo_only
async def typenc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /typenc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(typenc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ typenc started for: {text}")

@sudo_only
async def flashnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /flashnc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(flashnc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ flashnc started for: {text}")

@sudo_only
async def foxync(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /foxync <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(foxync_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ foxync started for: {text}")

# Spam Commands
@sudo_only
async def texts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /texts <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in spam_tasks:
        for t in spam_tasks[chat_id]: t.cancel()
    spam_tasks[chat_id] = [asyncio.create_task(texts_spam_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ texts spam started")

@sudo_only
async def shayari(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /shayari <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in spam_tasks:
        for t in spam_tasks[chat_id]: t.cancel()
    spam_tasks[chat_id] = [asyncio.create_task(shayari_spam_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ shayari spam started")

@sudo_only
async def songy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /songy <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in spam_tasks:
        for t in spam_tasks[chat_id]: t.cancel()
    spam_tasks[chat_id] = [asyncio.create_task(songy_spam_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ songy spam started")

@sudo_only
async def custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /custom <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in spam_tasks:
        for t in spam_tasks[chat_id]: t.cancel()
    spam_tasks[chat_id] = [asyncio.create_task(custom_spam_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ custom spam started")

# Sliders Commands
@sudo_only
async def alexa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("❌ Reply to a message!")
    chat_id, target_msg_id = update.message.chat_id, update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for t in slider_tasks[chat_id]: t.cancel()
    slider_tasks[chat_id] = [asyncio.create_task(make_slider_loop(ALEXA_TEXTS, b, chat_id, target_msg_id)) for b in bots]
    await update.message.reply_text("✅ Alexa started.")

@sudo_only
async def animal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("❌ Reply to a message!")
    chat_id, target_msg_id = update.message.chat_id, update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for t in slider_tasks[chat_id]: t.cancel()
    slider_tasks[chat_id] = [asyncio.create_task(make_slider_loop(ANIMAL_TEXTS, b, chat_id, target_msg_id)) for b in bots]
    await update.message.reply_text("✅ Animal started.")

@sudo_only
async def swipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("❌ Reply to a message!")
    chat_id, target_msg_id = update.message.chat_id, update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for t in slider_tasks[chat_id]: t.cancel()
    slider_tasks[chat_id] = [asyncio.create_task(make_slider_loop(SWIPE_TEXTS, b, chat_id, target_msg_id)) for b in bots]
    await update.message.reply_text("✅ Swipe started.")

# Control & Stops
@sudo_only
async def stopnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
        del nc_tasks[chat_id]
    await update.message.reply_text(STOP_MESSAGE)

@sudo_only
async def stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for t in spam_tasks[chat_id]: t.cancel()
        del spam_tasks[chat_id]
    await update.message.reply_text(STOP_MESSAGE)

@sudo_only
async def stopslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in slider_tasks:
        for t in slider_tasks[chat_id]: t.cancel()
        del slider_tasks[chat_id]
    await update.message.reply_text(STOP_MESSAGE)

@sudo_only
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    for d in [nc_tasks, spam_tasks, slider_tasks]:
        if chat_id in d:
            for t in d[chat_id]: t.cancel()
            del d[chat_id]
    await update.message.reply_text(STOP_MESSAGE)

@sudo_only
async def delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_DELAY
    if not context.args:
        return await update.message.reply_text(f"⏱ Current delay: {GLOBAL_DELAY:.3f}s")
    try:
        val = float(context.args[0])
        if 0.005 <= val <= 0.05:
            GLOBAL_DELAY = val
            await update.message.reply_text(f"✅ Delay set to {val:.3f}s")
        else:
            await update.message.reply_text("❌ Limit: 0.005 to 0.05")
    except: pass

# Owner Operations
@owner_only
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    p_bot = context.bot
    perms = {'can_change_info': True, 'can_post_messages': True, 'can_edit_messages': True, 'can_delete_messages': True, 'can_invite_users': True, 'can_restrict_members': True, 'can_pin_messages': True, 'can_promote_members': True, 'can_manage_video_chats': True, 'can_manage_chat': True}
    count = 0
    for b_info in bots_info:
        if b_info['id'] != p_bot.id:
            try:
                await p_bot.promote_chat_member(chat_id=chat_id, user_id=b_info['id'], **perms)
                count += 1
            except: pass
    await update.message.reply_text(f"Promotion completed. {count} bots promoted.")

@owner_only
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return
    uid = update.message.reply_to_message.from_user.id
    SUDO_USERS.add(uid)
    save_sudo()
    await update.message.reply_text(f"✅ Added sudo: {uid}")

@owner_only
async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return
    uid = update.message.reply_to_message.from_user.id
    if uid in SUDO_USERS and uid != OWNER_ID:
        SUDO_USERS.remove(uid)
        save_sudo()
        await update.message.reply_text(f"✅ Removed sudo: {uid}")

@owner_only
async def sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"**SUDO USERS:**\n" + "\n".join([f"👑 {u}" for u in SUDO_USERS]))

@owner_only
async def bye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    for b in bots:
        try:
            await b.send_message(chat_id, BYE_MESSAGE)
            await b.leave_chat(chat_id)
        except: pass

HELP_MENU = """
𝐓𝙷𝙴  𝐅𝚁𝙴𝙰𝙺𝚈  𝐌𝚄𝚂𝙴 < 🪐
──────做𝚌'𝚜──────
⤹/ncdark | /tmkcnc | /evonc | /marvelnc | /magicnc | /sportnc | /lndnc | /ncspeed | /emognc | /yournc | /customnc | /typenc | /flashnc | /foxync
──────𝐒𝐩𝐚𝐦───────
⤹/texts | /shayari | /songy | /custom
──────𝐒complete──────
⤹/alexa | /animal | /swipe
──────𝐎𝚠..."""

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_owner_or_sudo(update.effective_user.id): await update.message.reply_text(HELP_MENU)

def build_app(token):
    app = Application.builder().token(token).build()
    cmds = ["ncdark","tmkcnc","evonc","marvelnc","magicnc","sportnc","lndnc","ncspeed","emognc","yournc","customnc","typenc","flashnc","foxync","texts","shayari","songy","custom","alexa","animal","swipe","stopnc","stopspam","stopslide","stopall","delay","promote","addsudo","delsudo","sudo","bye"]
    for c in cmds:
        app.add_handler(CommandHandler(c, globals()[c]))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(ChatMemberHandler(handle_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
    return app

async def run_all_bots():
    global bots_info
    for token in TOKENS:
        try:
            app = build_app(token)
            await app.initialize()
            me = await app.bot.get_me()
            bots_info.append({'id': me.id, 'username': me.username, 'bot': app.bot})
            apps.append(app)
            bots.append(app.bot)
            await app.start()
            await app.updater.start_polling()
            print(f"🚀 Started: @{me.username}")
        except Exception as e: print(f"❌ Error starting token: {e}")

async def main():
    # Run the background HTTP Flask server
    server_thread = Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()
    
    # Fire up the Telegram Client loops
    await run_all_bots()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
