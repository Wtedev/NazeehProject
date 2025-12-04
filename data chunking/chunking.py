import os
import json
import re

# أين توجد ملفات JSON؟
DATA_FOLDER = "data/boe_laws_json"

# أين نحفظ القطع الناتجة؟
CHUNKS_FOLDER = "chunks"

# إعدادات التقطيع
CHUNK_SIZE = 250
OVERLAP = 50


# ------------------------------------------
# 1) دالة تنظيف النص القانوني
# ------------------------------------------
def clean_text(text):
    # إزالة نصوص الموقع غير المهمة
    bad_phrases = [
        "البحث في الوثائق النظامية",
        "تسجيل الدخول",
        "حجم الخط",
        "تصفية النتائج",
        "مسح النتائج",
        "أدوات إصدار النظام",
        "نبذة عن النظام",
        "عدد مرات التصفح",
        "طلب اشعار",
        "الإصدارات",
        "اللغات",
        "EN",
        "أصل الوثيقة",
        "الملاحظات والتعليقات",
        "سياسة الخصوصية",
        "جميع الحقوق محفوظة",
        "©",
        "المستخدم مسؤول",
        "إشعار إخلاء مسؤولية"
    ]

    for phrase in bad_phrases:
        text = text.replace(phrase, " ")

    # إزالة تكرار المسافات
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ------------------------------------------
# 2) تقسيم النص حسب كلمة "المادة"
# ------------------------------------------
def split_by_articles(text):
    # نستخدم regex لتحديد بداية كل مادة
    parts = re.split(r"(المادة\s+\S+)", text)

    articles = []
    current_title = None
    current_body = ""

    for part in parts:
        if part.startswith("المادة"):
            # إذا فيه مادة سابقة نخزنها
            if current_title and current_body.strip():
                articles.append((current_title, current_body.strip()))
            current_title = part
            current_body = ""
        else:
            current_body += " " + part

    # آخر مادة
    if current_title and current_body.strip():
        articles.append((current_title, current_body.strip()))

    return articles


# ------------------------------------------
# 3) تقطيع المادة الطويلة إلى أجزاء صغيرة
# ------------------------------------------
def chunk_text(text, size=CHUNK_SIZE, overlap=OVERLAP):
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        start = end - overlap

    return chunks


# ------------------------------------------
# 4) البرنامج الرئيسي
# ------------------------------------------
def main():
    os.makedirs(CHUNKS_FOLDER, exist_ok=True)

    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".json"):
            file_path = os.path.join(DATA_FOLDER, filename)

            # نقرأ JSON
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # نسحب النص من داخل articles
            text = ""
            if "articles" in data and len(data["articles"]) > 0:
                text = data["articles"][0].get("text", "")

            # تنظيف النص
            clean = clean_text(text)

            # تقسيم حسب المواد
            articles = split_by_articles(clean)

            print(f"\n📌 الملف: {filename}")
            print(f"عدد المواد: {len(articles)}")

            # معالجة كل مادة
            for i, (title, body) in enumerate(articles):
                # إذا المادة قصيرة → نخزنها مباشرة
                if len(body.split()) < CHUNK_SIZE:
                    chunk_filename = f"{filename}_article_{i}.txt"
                    with open(os.path.join(CHUNKS_FOLDER, chunk_filename), "w", encoding="utf-8") as f:
                        f.write(title + "\n" + body)
                else:
                    # تقطيع المادة الطويلة
                    small_chunks = chunk_text(body)
                    for j, piece in enumerate(small_chunks):
                        chunk_filename = f"{filename}_article_{i}_chunk_{j}.txt"
                        with open(os.path.join(CHUNKS_FOLDER, chunk_filename), "w", encoding="utf-8") as f:
                            f.write(title + "\n" + piece)

    print("\n✨ التقطيع اكتمل! تمت كتابة جميع الملفات داخل مجلد chunks")


# تشغيل البرنامج
if __name__ == "__main__":
    main()