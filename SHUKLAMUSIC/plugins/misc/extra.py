# Ported from elsen_music (originally Nunum/AylinRobot) and adapted to
# Shakura's own plugin conventions, including the multi-language string
# system (strings/langs/*.yml -> extra_1, extra_2, extra_3). Music/download
# functionality is NOT touched by this file - it only adds the extra
# fun/social commands that Shakura didn't already have.

import os
import random

from pyrogram import filters

from SHUKLAMUSIC import app
from SHUKLAMUSIC.utils.database import get_lang
from SHUKLAMUSIC.utils.extra_data import ANIME_PHOTOS, BIO_QUOTES, PP_PHOTOS, SEVGI_QUOTES
from strings import get_string

SEHID_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "utils", "data", "sehid.txt")


async def _lang(chat_id):
    try:
        return get_string(await get_lang(chat_id))
    except Exception:
        return get_string("en")


@app.on_message(filters.command(["sevgi"]))
async def sevgi_cmd(_, message):
    await message.reply_text(random.choice(SEVGI_QUOTES), quote=True)


@app.on_message(filters.command(["bio"]))
async def bio_cmd(_, message):
    await message.reply_text(random.choice(BIO_QUOTES), quote=True)


@app.on_message(filters.command(["anime"]))
async def anime_cmd(_, message):
    lang = await _lang(message.chat.id)
    photo = random.choice(ANIME_PHOTOS)
    await message.reply_photo(photo=photo, caption=lang["extra_1"].format(app.mention))


@app.on_message(filters.command(["pp"]))
async def pp_cmd(_, message):
    lang = await _lang(message.chat.id)
    photo = random.choice(PP_PHOTOS)
    await message.reply_photo(photo=photo, caption=lang["extra_2"].format(app.mention))


def _random_line(fname: str) -> str:
    with open(fname, "r", encoding="utf-8") as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip()]
    return random.choice(lines)


@app.on_message(filters.command(["sehid"]))
async def sehid_cmd(_, message):
    lang = await _lang(message.chat.id)
    try:
        line = _random_line(SEHID_FILE)
    except FileNotFoundError:
        return await message.reply_text(lang["extra_3"])
    await message.reply_text(f"🕯 {line}", quote=True)

# NOTE: /github was intentionally NOT ported here - Shakura already has an
# identical GitHub profile lookup command (see plugins/tools/gitinfo.py and
# plugins/tools/shivop.py), so adding it again would only duplicate it.
