# runBot.py
import os, asyncio, mimetypes, tempfile
from pyrogram import Client, filters
from utils import smart_merge, slugify, download_file
from evrit_scraper import EvritScraper
from ebooklib import epub
from PyPDF2 import PdfReader
from pyrogram.errors import FloodWait

API_ID    = int(os.environ["TG_API_ID"])
API_HASH  = os.environ["TG_API_HASH"]
BOT_TOKEN = os.environ["TG_BOT_TOKEN"]

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
scraper = EvritScraper()

def read_epub(path):
    book = epub.read_epub(path)
    meta = {"title": None, "author": None, "pages": None}
    if book.get_metadata("DC", "title"):
        meta["title"]  = book.get_metadata("DC", "title")[0][0]
    if book.get_metadata("DC", "creator"):
        meta["author"] = book.get_metadata("DC", "creator")[0][0]
    return meta

def read_pdf(path):
    pdf  = PdfReader(path)
    info = pdf.metadata
    meta = {"title": getattr(info, "title", None),
            "author": getattr(info, "author", None),
            "pages": len(pdf.pages)}
    return meta

def extract_metadata(path):
    kind = mimetypes.guess_type(path)[0]
    raw  = read_epub(path) if kind and "epub" in kind else read_pdf(path)
    if not raw["title"] or not raw["author"]:
        ev = scraper.by_filename(os.path.basename(path))
        raw = smart_merge(raw, ev)
    return raw

@app.on_message(filters.document)
async def handle_doc(client, msg):
    doc_path = await client.download_media(msg.document)
    meta = extract_metadata(doc_path)

    title  = meta.get("title")  or "Unknown"
    author = meta.get("author") or "Unknown"
    new_name = f"{slugify(title)} - {slugify(author)}{os.path.splitext(doc_path)[1]}"
    os.rename(doc_path, new_name)

    caption = f"**{title}**\n_{author}_\n\n{meta.get('description','')}"
    cover = meta.get("cover_url")

    try:
        if cover:
            await client.send_photo(msg.chat.id, cover, caption=caption)
        await client.send_document(msg.chat.id, new_name, caption=caption)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await client.send_document(msg.chat.id, new_name, caption=caption)
    finally:
        os.remove(new_name)

if __name__ == "__main__":
    app.run()
