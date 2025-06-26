# evrit_scraper.py
import re, time, requests
from bs4 import BeautifulSoup
from utils import slugify

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; EvritBot/1.0)"}

class EvritScraper:
    google = "https://www.google.com/search"
    def _search(self, query):
        r = requests.get(self.google, params={"q": query}, headers=HEADERS, timeout=15)
        links = re.findall(r"https://www\.e-vrit\.co\.il/[^\"&]+", r.text)
        return links[0] if links else None

    def _parse_book(self, url):
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")
        title  = soup.select_one("h1.product-title")
        author = soup.select_one(".info-author")
        descr  = soup.select_one(".product-description")
        cover  = soup.select_one("meta[property='og:image']")
        return {
            "title":  title.get_text(strip=True)  if title else None,
            "author": author.get_text(strip=True) if author else None,
            "description": descr.get_text(" ", strip=True) if descr else "",
            "cover_url": cover["content"] if cover else None,
            "book_url": url
        }

    def by_filename(self, filename):
        q = slugify(filename, keep_spaces=True)
        url = self._search(f'site:e-vrit.co.il "{q}"')
        if not url: return {}
        time.sleep(1)  # polite pause
        return self._parse_book(url)
