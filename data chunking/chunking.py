import os

def read_files_from_data_folder():
    texts = []
    folder = "data"

    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if filename.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                texts.append((filename, f.read()))
    return texts

def clean_text(text):
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    return text

def chunk_text(text, chunk_size=300, overlap=50):
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap

    return chunks

texts = read_files_from_data_folder()

for filename, content in texts:
    clean = clean_text(content)
    chunks = chunk_text(clean)

    print(f"ملف: {filename}")
    print(f"عدد القطع = {len(chunks)}")
    print("-" * 40)

    for i, c in enumerate(chunks):
        with open(f"chunks_{filename}_{i}.txt", "w", encoding="utf-8") as f:
            f.write(c)