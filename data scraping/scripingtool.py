import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

ENTRY_PAGE = "https://laws.boe.gov.sa/BoeLaws/Laws/Folders/1"
BASE_URL = "https://laws.boe.gov.sa"
OUTPUT_JSON_PATH = "laws_dataset.json"

def extract_law_details(url):
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")

    def extract_field(label_text):
        label = soup.find("label", string=lambda s: s and label_text in s)
        if label:
            span = label.find_next("span")
            return span.text.strip() if span else None
        return None

    name = extract_field("الاسم")
    release_date = extract_field("تاريخ الإصدار")
    publish_date = extract_field("تاريخ النشر")

    articles = []
    for article_div in soup.find_all("div", class_="article_item"):
        text = article_div.get_text(separator=" ", strip=True)
        if text:
            articles.append(text)

    return {
        "name": name,
        "release_date": release_date,
        "publish_date": publish_date,
        "articles": articles,
        "url": url
    }

def get_sections():
    res = requests.get(ENTRY_PAGE, verify=False)
    soup = BeautifulSoup(res.text, "html.parser")
    sections = []
    for li in soup.select("section#vertical_tab_nav li a[data-id]"):
        sections.append({
            "id": li["data-id"],
            "name": li.get_text(strip=True)
        })
    return sections

def get_toggle_links(folder_id):
    url = f"{ENTRY_PAGE}?FolderId={folder_id}"
    res = requests.get(url, verify=False)
    soup = BeautifulSoup(res.text, "html.parser")

    toggles = []
    for div in soup.select("div[class^='content-']"):
        title_tag = div.select_one(".link")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        urls = [urljoin(BASE_URL, a["href"]) for a in div.select("a[href^='/BoeLaws/Laws/LawDetails']")]
        toggles.append({"title": title, "urls": urls})
    return toggles

def main():
    print("بدء استخراج البيانات...")
    dataset = []
    counter = 1
    a=1
    sections = get_sections()

    for section in sections:
        toggles = get_toggle_links(section["id"])
        for toggle in toggles:
            for law_url in toggle["urls"]:
                try:
                    law = extract_law_details(law_url)
                    
                    
                    dataset.append({
                        "id": counter,
                        "text_group": section["name"],
                        "category": toggle["title"],
                        "name": law["name"],
                        "release_date": law["release_date"],
                        "publish_date": law["publish_date"],
                        "articles": law["articles"],
                        "url": law["url"]
                    })
                    a +=1
                    print(f"تمت إضافة النظام: {law['name']}")
                    
                except Exception as e:
                    print("خطأ:", e)
            break
        break

    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    

    print(f"تم حفظ الملف: {OUTPUT_JSON_PATH}")

if __name__ == "__main__":
    main()
