# -*- coding: utf-8 -*-
"""
scrape_one.py
سكريبت بسيط يسحب صفحة نظام من بوابة القوانين ويخرج JSON يحتوي على المواد.

"""

import re
import json
import datetime
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from slugify import slugify
import urllib3

# تعطيل تحذيرات InsecureRequestWarning مؤقتًا
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# مخرجات
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUT_DIR = os.path.join(BASE_DIR, "data", "boe_laws_json")
os.makedirs(OUT_DIR, exist_ok=True)


HEADERS = {"User-Agent": "LegalScraper/0.1 (for research; contact: you@example.com)"}

# رابط تجريبي:ا
TEST_URL = "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/16b97fcb-4833-4f66-8531-a9a700f161b6/1"

def textnorm(s):
    """تنظيف فراغات"""
    return re.sub(r"\s+", " ", (s or "")).strip()

def get_soup(url):
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # نطلب الصفحة بدون تحقق SSL
    r = requests.get(
        url,
        headers=HEADERS,
        timeout=25,
        verify=False     # ← تعطيل التحقق نهائياً
    )
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    return BeautifulSoup(r.text, "lxml")


def parse_articles(text):
    """
    يقسم النص إلى مقاطع اعتمادًا على نمط "المادة N" أو "مادة N".
    يعيد قائمة مقالات مع رقم المادة والنص.
    """
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
    # ترتيب حسب رقم الماده د
    articles.sort(key=lambda x: (x["number_norm"] is None, x["number_norm"] or 0))
    return articles

def scrape_one(url):
    """يجمع صفحة نظام ويحفظ ملف JSON في مجلد OUT_DIR (يتخطى الأنظمة المحفوظة مسبقًا)"""
    # استخراج معرف النظام من الرابط لتكوين اسم الملف
    import re
    law_id = re.findall(r"/LawDetails/([^/]+)/", url)
    law_id = law_id[0] if law_id else slugify(url)

    out_path = os.path.join(OUT_DIR, f"{law_id}.json")

    # لو الملف موجود بالفعل، نتخطاه
    if os.path.exists(out_path):
        print(f"⏩ Skipped (already saved): {url}")
        return out_path

    # محاولة تحميل الصفحة
    try:
        soup = get_soup(url)
    except Exception as e:
        print("ERROR: failed to fetch URL:", url)
        print(type(e).__name__, str(e))
        return None

    # استخراج العنوان
    h1 = soup.select_one("h1")
    title = textnorm(h1.get_text(strip=True)) if h1 else textnorm(soup.title.get_text() if soup.title else "بدون عنوان")

    # النص الكامل للصفحة
    main = soup.select_one("main") or soup
    full_text = textnorm(main.get_text("\n", strip=True))
    articles = parse_articles(full_text)

    # استخراج معرف النظام (GUID) والإصدار
    guid = None
    version = None
    try:
        parts = [p for p in urlparse(url).path.split("/") if p]
        if len(parts) >= 2 and parts[-2]:
            guid = parts[-2]
        if parts and parts[-1].isdigit():
            version = int(parts[-1])
    except Exception:
        pass

    # البحث عن المرفقات (PDF)
    atts = []
    for a in soup.select("a[href*='/Files/Download/?attId=']"):
        href = a.get("href")
        if href:
            atts.append({
                "label": textnorm(a.get_text(strip=True) or "ملف"),
                "url": href
            })

    # البيانات النهائية
    data = {
        "law_id": guid,
        "title_ar": title,
        "title_en": None,
        "category": None,
        "issuance_hijri": None,
        "issuance_gregorian": None,
        "last_update_hijri": None,
        "last_update_gregorian": None,
        "version": version,
        "source_url": url,
        "articles": articles,
        "attachments": atts,
        "metadata": {
            "publisher": "هيئة الخبراء بمجلس الوزراء",
            "language": "ar",
            "scraped_at": datetime.datetime.utcnow().isoformat() + "Z"
        }
    }

    # الحفظ
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved: {title} ({len(articles)} articles)")
    return out_path


if __name__ == "__main__":
    scrape_one(TEST_URL)
