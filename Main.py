import asyncio
import json
import os
import sys
import random
from datetime import datetime, timezone, timedelta
from telegram import Update, ChatMemberUpdated, ChatMember
from telegram.error import RetryAfter
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler
import logging

# ---------------------------
# YOUR 11 BOT TOKENS (Pre-configured)
# ---------------------------
TOKENS = [
    "8875719610:AAEPZpAFmsLfGpcfq5G6IRqrkRw-oW6wawc",
    "8819644187:AAEfMcd3Y1iUs3a5bswYwuXHMFhe1EdzOEo",
    "8945796268:AAEn4esqIx4JbbNQC5G8LsWD6uALOarqDD0",
    "8896368359:AAHZiQbpOJF-TpL5e-oeXJ4WP-hU2nV6sfQ",
    "8933273450:AAEUY5KkCkdDMKDlmww4-3V6W6ZLUxwZm7M",
    "8907464798:AAHGPbLN37eCgA1qsTbpijqN84eXE0KddzE",
    "8782264249:AAHzdBfPHq8ugHIiSkjNyVIcvnjKnkB8cQ0",
    "8142959042:AAHsO409iZu7S5BTm1NENuiu2UwjJeLK584",
    "8672754851:AAFYrY7xGXywkEtSFmMqO6Mgn1F_K7sd2a4",
    "8666579675:AAGrPDFoJPe8zsuvA6WIP5YqsY2bu7QS9vg",
    "8731707655:AAEhXd7amPipwvx87I1vBEG4eEcgO6IsrkQ"
]

# ---------------------------
# OWNER & SUDO CONFIG (Pre-configured)
# ---------------------------
OWNER_ID = 8680250815
SUDO_FILE = "sudo_users.json"

# Load sudo users
if os.path.exists(SUDO_FILE):
    with open(SUDO_FILE) as f:
        SUDO_USERS = set(json.load(f))
else:
    SUDO_USERS = {OWNER_ID}

def save_sudo():
    with open(SUDO_FILE, "w") as f:
        json.dump(list(SUDO_USERS), f)

# ---------------------------
# GLOBAL STATE
# ---------------------------
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

# ---------------------------
# PERMISSION HELPERS
# ---------------------------
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

# ---------------------------
# NC EMOJI LISTS
# ---------------------------
DARK_EMOJIS = ["🕳️", "🌑", "👣", "🗝️", "🧬", "🔌", "⬛", "🦾", "📜", "🕯️", "🍷", "🥀", "🖤", "🕸️", "🗡️", "🎱", "🐦‍⬛", "🔮", "🌑", "🪄", "🌝", "🌚", "🌜", "🌛", "🌙", "⭐", "🌟", "✨", "🪐", "🌍", "🌠", "🌌", "☄️", "🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
HAND_EMOJIS = ["👀", "👁️", "👄", "🫦", "👅", "👃🏻", "👂🏻", "🦻🏻", "🦶🏻", "🦵🏻", "🦿", "🦾", "💪🏻", "👏🏻", "👍🏻", "👎🏻", "🫶🏻", "🙌🏻", "👐🏻", "🤲🏻", "🤜🏻", "🤛🏻", "✊🏻", "👊🏻", "🫳🏻", "🫴🏻", "🫱🏻", "🫲🏻", "🫸🏻", "🫷🏻", "👋🏻", "🤚🏻", "🖐🏻", "✋🏻", "🖖🏻", "🤟🏻", "🤘🏻", "✌🏻", "🤞🏻", "🫰🏻", "🤙🏻", "🤌🏻", "🤏🏻", "👌🏻", "🫵🏻", "👉🏻", "👈🏻", "☝🏻", "👆🏻", "👇🏻", "🖕🏻", "✍🏻", "🤳🏻", "🙏🏻", "💅🏻", "🤝🏼", "🌘"]
MARVEL_EMOJIS = ["🛡️", "🇺🇸", "🎖️", "🦾", "🚀", "⚡", "🤖", "⚡", "🔨", "🌩️", "🔱", "🕷️", "🕶️", "🔫", "🥀", "🏹", "🎯", "🦅", "🧪", "☢️", "👊", "🟢", "💎", "🤖", "🟡"]
MAGIC_EMOJIS = ["🧪", "⚗️", "📜", "💎", "🕳️", "🌑", "🧿", "🐦‍⬛", "🌀", "⚡", "🪄", "🧿", "🕯️", "📜", "🏛️", "🖤", "✥", "♱", "⚖︎", "∞", "𖦹"]
NATURE_EMOJIS = ["💐", "🌹", "🥀", "🌺", "🌷", "🪷", "🌸", "💮", "🏵️", "🪻", "🌻", "🌼", "🍂", "🍁", "🍄", "🌾", "🌿", "🌱", "🍃", "☘️", "🍀", "🪴", "🌵", "🌴", "🪾", "🌳", "🌲", "🪵", "🪹", "🪺"]
FOOD_EMOJIS = ["🍧", "🧋", "🧃", "🥛", "🍿", "🧊", "🍵", "☕", "🍻", "🍺", "🧉", "🫖", "🍾", "🍷", "🥃", "🫗", "🍸", "🍹", "🍶", "🥢", "🥂", "🧈", "🧁", "🍭", "🍬", "🍫", "🍨", "🍡", "🍙", "🍥", "🥠", "🥟", "🍛", "🍤", "🍜", "🦪", "🍚", "🥣", "🥫", "🌯"]
FACE_EMOJIS = ["☺️", "😌", "🙂‍↕️", "🙂‍↔️", "😏", "🤤", "😋", "😛", "😝", "😜", "🤪", "😔", "🥺", "😬", "😑", "😐", "😶", "😶‍🌫️", "🫥", "🤐", "🫡", "🤔", "🤫", "🫢", "🤭", "🥱", "🤗", "🫣", "😱", "🤨", "🧐", "😒", "🙄", "😮‍💨", "😤", "😠", "😡", "🤬", "😞", "😓", "😟", "😥", "😢", "☹️", "🙁", "🫤", "😕", "😰", "😨", "😧", "😦", "😮", "😯", "😲", "🤯", "🫨", "😵‍💫", "😵", "😫", "🥴", "🥶", "🥵"]
HOBBY_EMOJIS = ["🃏", "🪄", "🎩", "📷", "🀄", "🎴", "🎰", "📸", "🖼️", "🎨", "🫟", "🖌️", "🖍️", "🪡", "🧵", "🧶", "🎹", "🎷", "🎺", "🎸", "🪕", "🎻", "🪉", "🪘", "🥁", "🪇", "🪈", "🪗", "🎤", "🎧", "🎚️", "🎛️", "🎙️", "📼", "📻", "📺", "📹", "📽️", "🎥", "🎞️", "🎬", "🎭", "🎫", "🎟️"]
TECH_EMOJIS = ["🔋", "🪫", "🖲️", "💽", "💾", "💿", "📀", "🖥️", "💻", "⌨️", "🖨️", "鼠标", "🪙", "💎", "💸", "💵", "💴", "💶", "💷", "💳", "💰", "🧾", "🧮", "⚖️", "🛒", "🛍️", "💡", "🕯️", "🔦", "🏮", "🧱", "🪟", "🪞", "🚪", "🚿", "🛁", "🚽", "🧻", "🪠", "🧸", "🪆", "🧷", "🪢", "🧹", "🧴", "🧽", "🧼", "🪥", "🪒", "🪮", "🧺", "🧦", "🧤", "🧣", "👖"]
ANIMAL_EMOJIS = ["🪼", "🐚", "🦋", "🐞", "🐝", "🐛", "🪱", "🦠", "🐾", "🫧", "🪸", "🦪", "🪼", "🐙", "🦑", "🐡", "🐠", "🐟", "🐳", "🐋", "🐬", "🦈", "🦭", "🐧", "🦃", "🐦‍🔥", "🦚", "🦩", "🪿", "🦆", "🦢", "🦤", "🕊️", "🦜", "🦉", "🦅", "🐥", "🐤", "🐣", "🐓", "🐦", "🪶", "🪽", "t", "🦦", "🦔", "🦡", "🦨", "🐅", "🐆", "🦒", "🦏", "🦣", "🐘", "🦓", "🦘", "🦥", "🦬", "🐃", "🐏", "🐂", "🐄", "🐎", "🐈", "🐩"]

TYPENC_WORDS = [
    "𝗧𝗔𝗧𝗧𝗘", "𝗚𝗨𝗟𝗔𝗠", "𝗠𝗔𝗗𝗔𝗥𝗖𝗛𝗢𝗗", "𝗕𝗛𝗘𝗡𝗞𝗟🇳🇩", "𝗧𝗠𝗞𝗖", "𝗧𝗠𝗞𝗕",
    "𝗥🇳🇩𝗬", "𝗚𝗔𝗥𝗘𝗘𝗕", "𝗠𝗜𝗦𝗧🇮 𝗞🇪 𝗟𝗔𝗗𝗞🇪", "𝗚🇳🇩🇺", "𝗖𝗛𝗔𝗣𝗥🇮", "𝗖𝗛𝗠𝗥",
    "𝗕𝗦🇩𝗞", "𝗞🇪🇪🇩🇪", "𝗖𝗛🇺🇩", "𝗧开𝗞𝗟", "𝗛𝗔𝗥𝗔𝗠𝗞𝗛𝗢𝗥", "𝗥"
]

ALEXA_TEXTS = [
    "𝗔index𝗘𝗫𝗔 🇮𝗦𝗦 𝗠𝗖 𝗞🇮 𝗠𝗔𝗔 𝗞𝗘 🇳🇴𝗧🇪🇸 𝗗🇮𝗞𝗛𝗔官 🙁",
    "𝗔index𝗘𝗫𝗔 🇮𝗦𝗞🇮 𝗕🇭🇪🇳 𝗖🇭🇴𝗗 𝗗🇴 🌙",
    "𝗔index𝗘𝗫𝗔 🇮𝗦𝗞🇪 𝗕🇦‌🇦🇵 𝗞🇮 🇬🇳🇩 𝗠🇮🇪 𝗟🇦𝗧🇭 🇩🇦🇦𝗟 🇩🇴 😆",
    "𝗔index𝗘𝗫𝗔 🇮𝗦𝗞🇦 🇬🇦𝗠🇪 𝗢𝗩🇪🇷 𝗞🇦 𝗩🇮🇩🇪🇴 🇩🇴🇳🇪 𝗞🇷🇴 🥹"
]

ANIMAL_TEXTS = [
    "𝗢𝗬🇪 𝗧🇲𝗞🇨 𝗠🇮🇪 🇬🇴🇷🇮𝗟𝗟𝗔  🦍",
    "𝗢𝗬🇪 𝗧🇪走🇪 𝗕🇭🇪🇳 𝗞🇮 𝗖🇭🇺𝗧 𝗠🇮🇪 🇬🇭🇴🇩🇦 🐎",
    "𝗢𝗬🇪 𝗧🇪走🇪 𝗕🇦🇦🇵 𝗞🇮 🇬体🇩 𝗠🇮🇪 🇨🇦🇳🇬🇦走🇴🇴 🦘",
    "𝗢𝗬🇪 𝗧🇪走🇪 🇬体🇩 𝗠🇮🇪 🇨🇦𝗠🇪𝗟 🐪",
    "𝗢𝗬🇪 𝗧🇺 𝗝🇦🇳𝗪🇦走🇴𝗦 𝗦🇪 𝗖🇭🇺🇩 🇬𝗬🇦 ? 😆"
]

SWIPE_TEXTS = [
    "𝗧🇪走🇮 𝗠𝗞🇨 𝗦🇦🇸𝗧🇮 𝗛🇦🇮 𝗕🇦🇦𝗧 𝗞🇭𝗧🇲 😡",
    "𝗖🇭𝗟 🇬🇺𝗟🇦𝗠🇮 𝗞走 𝗧🇦𝗧𝗧🇪 😆",
    "𝗖🇭🇮施行𝗬🇦 𝗖🇭🇦走🇮 𝗣🇭🇦🇦🇩 𝗣🇪 🇺🇸🇳🇪 🇩🇮𝗬🇦 𝗠🇺𝗧 𝗧🇲𝗞🇨 😆",
    "🇪𝗞 𝗟🇦🇦‌𝗧 𝗠🇮🇪 𝗟🇳🇩 𝗖🇭🇦𝗧𝗧🇦 𝗙🇮走🇪🇬🇦 𝗕🇸施行𝗞 😆"
]

TEXTS_PATTERN = "{text}  𝑶𝒀𝑬 𝑩𝑲𝑳 𝑻𝑬𝑹𝑰 𝑴𝑨𝑨 𝑲𝑨 𝑲𝑯𝑨𝑺𝑨𝑴 𝑯𝑼 𝑨𝑼𝑲𝑨𝑻 𝑴𝑰𝑬 𝑹𝑯 𝑹𝑵加快𝒀 𝑷𝑼𝑻𝑹𝑨 ☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲\\~   "
TEXTS_REPEAT = 10
SHAYARI_PATTERN = "𝙏𝙄𝙆 𝙏𝙄𝙆 𝘾𝙃𝙇𝙏𝘼 𝙂𝙃𝙊𝘿𝘼 {text} 𝙆𝙄 𝘽𝙃𝙀𝙉 𝙆𝘼 𝙇𝙊𝘿𝘼 ╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍☲╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍ "
SHAYARI_REPEAT = 10
SONGY_PATTERN = "{text} 𝗗𝗮狠𝗲!\n𝗕𝗲𝘁𝗮 𝗗𝗮狠𝗲 𝗕𝗲𝗻𝗶 𝗕a𝗮𝗽 𝗧𝗲𝗿𝗮 𝗡𝗮狠𝗮 𝗛𝗮𝗶\n𝗟*🇩𝗮 𝗛𝗼𝗼𝗸𝗮ʜ 𝗠𝗲𝗿𝗮, 𝗠𝗮𝗺𝘁𝗮 𝗠𝗲𝗿𝗶 𝗖𝗵ａ狠𝗮 𝗛𝗮𝗶\n..."
CUSTOM_PATTERN = "{text}  ⩇⩇:⩇⩇ {kaomoji}"
CUSTOM_KAOMOJI = ["(◕‿◕)", "(✿◠‿嫁)", "(◔‿◔)", "(◡‿◡✿)", "(ᵔ◡ᵔ)", "😊", "😄", "😁"]

# Loops for NC, Spam & Sliders
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
            await bot.set_chat_title(chat_id, f"{text} ⭞ ᴛᴍκᴄ ￫ {emoji}")
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
            await bot.set_chat_title(chat_id, f"{text} 𝙏𝘽 Kenny ᯓ {emoji}")
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
            await bot.set_chat_title(chat_id, f"{text} 𝙏𝙀𝙍𝑰 𝙂体🇩 🇲🇮🇪 ≯ {emoji}")
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
            await bot.set_chat_title(chat_id, f"{text} 𝙏𝙀𝙍𝑰 🇲🇦🇦 🇨🇭🇺🇩🇦🇰🇦🇩 ≫ {emoji}")
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
            await bot.set_chat_title(chat_id, f"{text} 转型𝙀𝙀𝘿𝙀 𝘼𝙐𝙆🇦𝙏 𝘽🇳🇦⁀➴♡ {emoji}")
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
            await bot.set_chat_title(chat_id, f"{text} 𝗖🇭🇺🇩 𝗞走 𝗗🇦🇫🇦🇳~{emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

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
            await bot.send_message(chat_id, CUSTOM_PATTERN.format(text=text, kaomoji=kaomoji))
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

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

# ---------------------------
# AUTO HANDLER
# ---------------------------
async def handle_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result: ChatMemberUpdated = update.my_chat_member
    if result.chat.type not in ["group", "supergroup"]: return
    old, new = result.old_chat_member, result.new_chat_member
    if old.status in [ChatMember.LEFT, ChatMember.BANNED] and new.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]:
        await context.bot.send_message(chat_id=result.chat.id, text=GREETING_MESSAGE)
    elif old.status == ChatMember.MEMBER and new.status == ChatMember.ADMINISTRATOR:
        await context.bot.send_message(chat_id=result.chat.id, text=ADMIN_MESSAGE)

# ---------------------------
# COMMAND HANDLERS
# ---------------------------
@sudo_only
async def ncdark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: !ncdark <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(ncdark_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ ncdark started for: {text}")

@sudo_only
async def tmkcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: !tmkcnc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(tmkcnc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ tmkcnc started for: {text}")

@sudo_only
async def evonc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: !evonc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(evonc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ evonc started for: {text}")

@sudo_only
async def marvelnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: !marvelnc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(marvelnc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ marvelnc started for: {text}")

@sudo_only
async def magicnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: !magicnc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(magicnc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ magicnc started for: {text}")

@sudo_only
async def sportnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: !sportnc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(sportnc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ sportnc started for: {text}")

@sudo_only
async def lndnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: !lndnc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(lndnc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ lndnc started for: {text}")

@sudo_only
async def ncspeed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: !ncspeed <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(ncspeed_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ ncspeed started for: {text}")

@sudo_only
async def emognc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: !emognc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(emognc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ emognc started for: {text}")

@sudo_only
async def yournc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: !yournc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(yournc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ yournc started for: {text}")

@sudo_only
async def customnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: !customnc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(customnc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ customnc started for: {text}")

@sudo_only
async def typenc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: !typenc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(typenc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ typenc started for: {text}")

@sudo_only
async def flashnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: !flashnc <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(flashnc_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ flashnc started for: {text}")

@sudo_only
async def foxync(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: !foxync <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(foxync_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ foxync started for: {text}")

@sudo_only
async def texts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: !texts <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in spam_tasks:
        for t in spam_tasks[chat_id]: t.cancel()
    spam_tasks[chat_id] = [asyncio.create_task(texts_spam_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ texts spam started for: {text}")

@sudo_only
async def shayari(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: !shayari <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in spam_tasks:
        for t in spam_tasks[chat_id]: t.cancel()
    spam_tasks[chat_id] = [asyncio.create_task(shayari_spam_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ shayari spam started for: {text}")

@sudo_only
async def songy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: !songy <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in spam_tasks:
        for t in spam_tasks[chat_id]: t.cancel()
    spam_tasks[chat_id] = [asyncio.create_task(songy_spam_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ songy spam started for: {text}")

@sudo_only
async def custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: !custom <text>")
    text, chat_id = " ".join(context.args), update.message.chat_id
    if chat_id in spam_tasks:
        for t in spam_tasks[chat_id]: t.cancel()
    spam_tasks[chat_id] = [asyncio.create_task(custom_spam_loop(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ custom spam started for: {text}")

@sudo_only
async def alexa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("❌ Reply to a message to start alexa!")
    chat_id, target_msg_id = update.message.chat_id, update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for t in slider_tasks[chat_id]: t.cancel()
    slider_tasks[chat_id] = [asyncio.create_task(make_slider_loop(ALEXA_TEXTS, b, chat_id, target_msg_id)) for b in bots]
    await update.message.reply_text("✅ Alexa started on that message.")

@sudo_only
async def animal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("❌ Reply to a message to start animal!")
    chat_id, target_msg_id = update.message.chat_id, update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for t in slider_tasks[chat_id]: t.cancel()
    slider_tasks[chat_id] = [asyncio.create_task(make_slider_loop(ANIMAL_TEXTS, b, chat_id, target_msg_id)) for b in bots]
    await update.message.reply_text("✅ Animal started on that message.")

@sudo_only
async def swipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("❌ Reply to a message to start swipe!")
    chat_id, target_msg_id = update.message.chat_id, update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for t in slider_tasks[chat_id]: t.cancel()
    slider_tasks[chat_id] = [asyncio.create_task(make_slider_loop(SWIPE_TEXTS, b, chat_id, target_msg_id)) for b in bots]
    await update.message.reply_text("✅ Swipe started on that message.")

# Control commands
@sudo_only
async def stopnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
        del nc_tasks[chat_id]
        await update.message.reply_text(STOP_MESSAGE)
    else: await update.message.reply_text("❌ No NC running.")

@sudo_only
async def stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for t in spam_tasks[chat_id]: t.cancel()
        del spam_tasks[chat_id]
        await update.message.reply_text(STOP_MESSAGE)
    else: await update.message.reply_text("❌ No spam running.")

@sudo_only
async def stopslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in slider_tasks:
        for t in slider_tasks[chat_id]: t.cancel()
        del slider_tasks[chat_id]
        await update.message.reply_text(STOP_MESSAGE)
    else: await update.message.reply_text("❌ No slider running.")

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
        return await update.message.reply_text(f"⏱ Current delay: {GLOBAL_DELAY:.3f}s\nUsage: !delay <0.005-0.05>")
    try:
        new_delay = float(context.args[0])
        if 0.005 <= new_delay <= 0.05:
            GLOBAL_DELAY = new_delay
            await update.message.reply_text(f"✅ Delay set to {GLOBAL_DELAY:.3f}s")
        else: await update.message.reply_text("❌ Range must be 0.005 to 0.05")
    except ValueError: await update.message.reply_text("❌ Invalid input.")

# Owner commands
@owner_only
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    p_bot = context.bot
    other_bots = [info for info in bots_info if info['id'] != p_bot.id]
    if not other_bots: return await update.message.reply_text("No other bots.")
    perms = {'can_change_info': True, 'can_post_messages': True, 'can_edit_messages': True, 'can_delete_messages': True, 'can_invite_users': True, 'can_restrict_members': True, 'can_pin_messages': True, 'can_promote_members': True, 'can_manage_video_chats': True, 'can_manage_chat': True}
    count = 0
    for b in other_bots:
        try:
            await p_bot.promote_chat_member(chat_id=chat_id, user_id=b['id'], **perms)
            count += 1
        except Exception: pass
    await update.message.reply_text(f"Promotion completed for {count} bots.")

@owner_only
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("❌ Reply to a message")
    uid = update.message.reply_to_message.from_user.id
    SUDO_USERS.add(uid)
    save_sudo()
    await update.message.reply_text(f"✅ Added sudo: {uid}")

@owner_only
async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("❌ Reply to a message")
    uid = update.message.reply_to_message.from_user.id
    if uid in SUDO_USERS and uid != OWNER_ID:
        SUDO_USERS.remove(uid)
        save_sudo()
        await update.message.reply_text(f"✅ Removed sudo: {uid}")
    else: await update.message.reply_text("❌ Actions failed.")

@owner_only
async def sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = [f"👑 {uid}" for uid in SUDO_USERS]
    await update.message.reply_text(f"**SUDO USERS:**\n" + "\n".join(lines))

@owner_only
async def bye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await update.message.reply_text("👋 Leaving...")
    for b in bots:
        try:
            await b.send_message(chat_id, BYE_MESSAGE)
            await b.leave_chat(chat_id)
        except Exception: pass

HELP_MENU = """
𝐌𝙰𝙳𝙰𝚁𝙰  𝙺𝙴  𝙱𝙰𝙰𝙿  𝙺𝙸  𝚂𝙲𝚁𝙸𝙿𝚃 < 🪐
﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏
──────舊𝐜'𝐬──────
⤹!ncdark
⤹!tmkcnc
⤹!evonc
⤹!marvelnc
⤹!magicnc
⤹!sportnc
⤹!lndnc
⤹!ncspeed
⤹!emognc
⤹!yournc
⤹!customnc
⤹!typenc
⤹!flashnc
⤹!foxync
﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏
──────𝐒𝚙𝐚𝚖───────
⤹!texts
⤹!shayari
⤹!songy
⤹!custom
﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏
──────𝐒𝚕𝚒𝚍𝚎rer──────
⤹!alexa
⤹!animal
⤹!swipe
﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏
──────𝐎𝚠nent───────
⤹!promote
⤹!addsudo 
⤹!delsudo
⤹!sudo
⤹!bye
﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏
──────𝐂𝚘𝚗𝘁𝚛𝚘𝚕──────
⤹!stopnc
⤹!stopspam
⤹!stopslide
⤹!stopall
⤹!delay [0.05 ~ 0.005]
﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏
─────𝐄𝙽𝙹𝙾𝚈 ᥫ᭡.─────
"""

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_owner_or_sudo(update.effective_user.id):
        await update.message.reply_text(HELP_MENU)
    else: await update.message.reply_text("𝐆𝐔𝐋𝐀𝐌𝐈 𝐊𝐑 𝐏𝐇𝐋𝐄 𝐅𝐈𝐑 𝐒𝐔𝐃𝐎 𝐌𝐈𝐋𝐄𝐆𝐀 😂")

# ---------------------------
# BOT APP BUILDER WITH PREFIX CONFIG
# ---------------------------
def build_app(token):
    # Added prefix="!" to map commands cleanly to the help menu layout
    app = Application.builder().token(token).build()
    cmds = [
        ("ncdark", ncdark), ("tmkcnc", tmkcnc), ("evonc", evonc), ("marvelnc", marvelnc),
        ("magicnc", magicnc), ("sportnc", sportnc), ("lndnc", lndnc), ("ncspeed", ncspeed),
        ("emognc", emognc), ("yournc", yournc), ("customnc", customnc), ("typenc", typenc),
        ("flashnc", flashnc), ("foxync", foxync), ("texts", texts), ("shayari", shayari),
        ("songy", songy), ("custom", custom), ("alexa", alexa), ("animal", animal),
        ("swipe", swipe), ("stopnc", stopnc), ("stopspam", stopspam), ("stopslide", stopslide),
        ("stopall", stopall), ("delay", delay), ("promote", promote), ("addsudo", addsudo),
        ("delsudo", delsudo), ("sudo", sudo), ("bye", bye), ("help", help_cmd)
    ]
    for c, fn in cmds:
        app.add_handler(CommandHandler(c, fn, prefix="!"))
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
            print(f"🚀 Bot started: @{me.username}")
        except Exception as e: print(f"❌ Failed to start bot: {e}")
    
    # Simple port routing fake ping server for Railway system uptime
    try:
        port = int(os.environ.get("PORT", 8080))
        server = await asyncio.start_server(lambda r, w: w.close(), '0.0.0.0', port)
        print(f"📡 Fake ping active on port {port} for Railway uptime validation.")
    except Exception as e:
        print(f"⚠️ Port dynamic allocation warning: {e}")

    await asyncio.Event().wait()

if __name__ == "__main__":
    print("\n" + "="*40)
    print("      MADARA KE BAAP KI SCRIPT - RUNNING ON CLOUD")
    print("="*40)
    try:
        asyncio.run(run_all_bots())
    except (KeyboardInterrupt, SystemExit): print("\n🛑 System stopped.")
