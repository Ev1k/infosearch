import os
from collections import defaultdict

LEMMAS_DIR = "lemmas"
INDEX_FILE = 'inverted_index.txt'

# создает словарь с леммами и названиями документов (лемма:{название_документа1, ...})
def build_index():
    inverted_index = defaultdict(set)
    for filename in os.listdir(LEMMAS_DIR):
        doc_id = filename.replace(".txt", "")
        filepath = os.path.join(LEMMAS_DIR, filename)
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                lemma = line.split()[0]
                inverted_index[lemma].add(doc_id)

    return inverted_index


# сохраняет полученный словарь в файл
def save_index(index):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        for lemma in sorted(index):
            docs = " ".join(sorted(index[lemma]))
            f.write(f"{lemma}: {docs}\n")


index = build_index()
save_index(index)

print("Инвертированный индекс построен")
