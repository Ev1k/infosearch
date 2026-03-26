import math
import os
import re

import pymorphy3


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEMMAS_TFIDF_DIR = os.path.join(BASE_DIR, "lemmas_tfidf")
INDEX_FILE = os.path.join(BASE_DIR, "index.txt")

DOC_FILENAME_PATTERN = re.compile(r"^(\d+)\.txt$")

morph = pymorphy3.MorphAnalyzer()

# достаёт id документа из имени файла
def extract_doc_id(filename):
    match = DOC_FILENAME_PATTERN.fullmatch(filename)
    if not match:
        return None
    return int(match.group(1))


# создает словарь с парами doc_id:"url"
def load_index():
    doc_urls = {}

    with open(INDEX_FILE, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split()

            if len(parts) < 2:
                continue

            filename = parts[0]
            url = parts[1]

            doc_id = extract_doc_id(filename)
            if doc_id is None:
                continue

            doc_urls[doc_id] = url

    return doc_urls


# загружает все документы как векторы tf-idf
def load_doc_vectors():
    doc_vectors = {}
    doc_norms = {}
    idf_dict = {}

    for filename in os.listdir(LEMMAS_TFIDF_DIR):
        doc_id = extract_doc_id(filename)
        if doc_id is None:
            continue

        vector = {}
        norm_sq = 0.0

        with open(os.path.join(LEMMAS_TFIDF_DIR, filename), encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 3:
                    continue

                lemma, idf_str, tfidf_str = parts
                idf = float(idf_str)
                tfidf = float(tfidf_str)

                vector[lemma] = tfidf
                norm_sq += tfidf ** 2

                if lemma not in idf_dict:
                    idf_dict[lemma] = idf

        doc_vectors[doc_id] = vector
        doc_norms[doc_id] = math.sqrt(norm_sq)

    return doc_vectors, doc_norms, idf_dict


def main():
    doc_urls = load_index()
    doc_vectors, doc_norms, idf_dict = load_doc_vectors()
    print(doc_urls)
    print("Загружено документов:", len(doc_vectors))


if __name__ == "__main__":
    main()