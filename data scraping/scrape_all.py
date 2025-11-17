# -*- coding: utf-8 -*-
"""
scrape_all.py
يجمع كل الأنظمة القانونية من موقع هيئة الخبراء
ويحفظ كل نظام في ملف JSON داخل data/boe_laws_json
"""

import os
import time
import json
import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from slugify import slugify
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://laws.boe.gov.sa"
HEADERS = {"User-Agent": "LegalScraper/0.2 (for research use)"}

# مجلد الحفظ
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUT_DIR = os.path.join(BASE_DIR, "data", "boe_laws_json")
os.makedirs(OUT_DIR, exist_ok=True)


def get_soup(url):
    """جلب الصفحة وتحويلها إلى BeautifulSoup"""
    r = requests.get(url, headers=HEADERS, timeout=25, verify=False)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    return BeautifulSoup(r.text, "lxml")


def list_laws_from_folder(folder_id):
    """إرجاع قائمة بروابط كل الأنظمة داخل تصنيف معين"""
    folder_url = f"{BASE_URL}/BoeLaws/Laws/Folders/{folder_id}"
    soup = get_soup(folder_url)
    links = []
    for a in soup.select("a[href*='/BoeLaws/Laws/LawDetails/']"):
        href = a.get("href")
        if href:
            links.append(urljoin(BASE_URL, href))
    return sorted(set(links))


def parse_articles(soup):
    """استخراج نصوص المواد من صفحة النظام"""
    text = soup.get_text("\n", strip=True)
    import re
    parts = re.split(r"(?=المادة\s+\d+|مادة\s+\d+)", text)
    articles = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        m = re.match(r"(?:المادة|مادة)\s+(\d+)", p)
        num = int(m.group(1)) if m else None
        articles.append({
            "number": f"المادة {num}" if num else None,
            "number_norm": num,
            "text": p
        })
    return articles


def scrape_one_law(url):
    """يجمع نظام واحد ويحفظه كملف JSON"""
    soup = get_soup(url)
    h1 = soup.select_one("h1")
    title = h1.get_text(strip=True) if h1 else "بدون عنوان"
    articles = parse_articles(soup)

    data = {
        "title_ar": title,
        "source_url": url,
        "articles": articles,
        "scraped_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

    slug = slugify(title)
    out_path = os.path.join(OUT_DIR, f"{slug}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved: {title} ({len(articles)} articles)")
    return out_path


def main():
    # قائمة تصنيفات الأنظمة في الموقع ()
    folder_ids = [1, 2, 3, 4, 5]
    all_links = set()

    print("🔍 Gathering law links...")
    for fid in folder_ids:
        try:
            urls = list_laws_from_folder(fid)
            print(f"📂 Folder {fid}: {len(urls)} links")
            all_links.update(urls)
            time.sleep(1.5)
        except Exception as e:
            print("⚠️ Error reading folder", fid, e)

    print(f"\n📚 Total unique laws found: {len(all_links)}\n")

    for url in sorted(all_links):
        try:
            scrape_one_law(url)
        except Exception as e:
            print("❌ Error scraping:", url, e)
        time.sleep(2)  # تأخير بسيط لتجنب الضغط على الموقع


if __name__ == "__main__":
    main()
