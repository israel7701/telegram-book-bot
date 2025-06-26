# utils.py
import re, requests, shutil
from difflib import SequenceMatcher
from pathlib import Path

def slugify(txt, keep_spaces=False):
    txt = re.sub(r"[^\w\s\-]", "", txt).strip()
    return txt if keep_spaces else txt.replace(" ", "_")

def smart_merge(local: dict, remote: dict) -> dict:
    out = local.copy()
    for k, v in remote.items():
        if not out.get(k) and v:
            out[k] = v
    return out

def download_file(url, dest):
    with requests.get(url, stream=True, timeout=20) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            shutil.copyfileobj(r.raw, f)

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()
