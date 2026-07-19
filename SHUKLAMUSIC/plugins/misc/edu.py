# Ported from elsen_music (originally eduaze-bot) and adapted to Shakura's
# own plugin conventions, including the multi-language string system
# (strings/langs/*.yml -> edu_1..edu_8). /ask is intentionally NOT ported
# here since Shakura already has AI Q&A via SHUKLAMUSIC/plugins/tools/Gpt.py
# - this file only adds what was missing: image/video search and a small
# file catalog.

import json
import os
import time

import aiohttp
from pyrogram import filters
from pyrogram.types import InputMediaPhoto

import config
from SHUKLAMUSIC import app
from SHUKLAMUSIC.misc import SUDOERS
from SHUKLAMUSIC.utils.database import get_lang
from strings import get_string

PEXELS_IMAGE_URL = "https://api.pexels.com/v1/search"
PEXELS_VIDEO_URL = "https://api.pexels.com/videos/search"


async def _lang(chat_id):
    try:
        return get_string(await get_lang(chat_id))
    except Exception:
        return get_string("en")


def _load_catalog() -> list:
    try:
        with open(config.CATALOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_catalog(items: list) -> None:
    os.makedirs(os.path.dirname(config.CATALOG_PATH) or ".", exist_ok=True)
    with open(config.CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


async def _pexels_get(endpoint: str, query: str, per_page: int):
    if not config.PEXELS_API_KEY:
        return None
    headers = {"Authorization": config.PEXELS_API_KEY}
    params = {"query": query, "per_page": per_page}
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            return await resp.json()


@app.on_message(filters.command(["img"]))
async def pexels_image_cmd(_, message):
    lang = await _lang(message.chat.id)
    if not config.PEXELS_API_KEY:
        return await message.reply_text(lang["edu_1"])
    if len(message.command) < 2:
        return await message.reply_text(lang["edu_2"])

    query = message.text.split(None, 1)[1]
    data = await _pexels_get(PEXELS_IMAGE_URL, query, 5)
    photos = (data or {}).get("photos", [])
    if not photos:
        return await message.reply_text(lang["edu_3"])

    urls = [p["src"]["large"] for p in photos]
    media = [InputMediaPhoto(u) for u in urls]
    await message.reply_media_group(media)


@app.on_message(filters.command(["vid"]))
async def pexels_video_cmd(_, message):
    lang = await _lang(message.chat.id)
    if not config.PEXELS_API_KEY:
        return await message.reply_text(lang["edu_1"])
    if len(message.command) < 2:
        return await message.reply_text(lang["edu_4"])

    query = message.text.split(None, 1)[1]
    data = await _pexels_get(PEXELS_VIDEO_URL, query, 3)
    videos = (data or {}).get("videos", [])
    if not videos:
        return await message.reply_text(lang["edu_3"])

    best = videos[0]["video_files"][-1]["link"]
    await message.reply_video(best)


@app.on_message(filters.command(["catalog"]))
async def catalog_cmd(_, message):
    lang = await _lang(message.chat.id)
    items = _load_catalog()
    if len(message.command) > 1:
        needle = message.text.split(None, 1)[1].lower()
        items = [
            i for i in items
            if needle in i.get("title", "").lower() or needle in i.get("keywords", "").lower()
        ]

    if not items:
        return await message.reply_text(lang["edu_5"])

    for item in items[:10]:
        try:
            await message.reply_document(
                item["file_id"],
                caption=f"<b>{item['title']}</b>\n{item.get('category', '-')}",
            )
        except Exception:
            continue


@app.on_message(filters.command(["addfile"]) & filters.reply)
async def addfile_cmd(_, message):
    lang = await _lang(message.chat.id)
    if message.from_user.id not in SUDOERS:
        return await message.reply_text(lang["edu_6"])

    doc = message.reply_to_message.document
    if not doc or len(message.command) < 3:
        return await message.reply_text(lang["edu_7"])

    category = message.command[1]
    rest = message.text.split(None, 2)[2]
    title, _sep, keywords = rest.partition("|")

    items = _load_catalog()
    items.append(
        {
            "id": str(int(time.time() * 1000)),
            "title": title.strip(),
            "keywords": keywords.strip(),
            "file_id": doc.file_id,
            "category": category,
            "added_by": message.from_user.id,
            "added_at": int(time.time()),
        }
    )
    _save_catalog(items)
    await message.reply_text(lang["edu_8"].format(title.strip()))
