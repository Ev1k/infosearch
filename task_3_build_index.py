import os
from collections import defaultdict

LEMMAS_DIR = "lemmas"


# создает словарь с леммами и названиями документов (лемма:{название_документа1, ...})
def build_index():
    inverted_index = defaultdict(set)
    print(inverted_index)
    for filename in os.listdir(LEMMAS_DIR):
        doc_id = filename.replace(".txt", "")
        filepath = os.path.join(LEMMAS_DIR, filename)
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                lemma = line.split()[0]
                inverted_index[lemma].add(doc_id)

    return inverted_index

print(build_index())
