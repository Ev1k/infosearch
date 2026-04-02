import math
import os
import re

from collections import Counter
try:
    import pymorphy3
except ImportError:
    pymorphy3 = None


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEMMAS_TFIDF_DIR = os.path.join(BASE_DIR, "lemmas_tfidf")
INDEX_FILE = os.path.join(BASE_DIR, "index.txt")

DOC_FILENAME_PATTERN = re.compile(r"^(\d+)\.txt$")
TOKEN_PATTERN = re.compile(r"[а-яёa-z0-9]+", re.IGNORECASE)

morph = pymorphy3.MorphAnalyzer() if pymorphy3 else None

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


# токенизация запроса
def tokenize(text):
    return TOKEN_PATTERN.findall(text.lower())


# лемматизация запроса
def lemmatize_tokens(tokens):
    lemmas = []

    if morph is None:
        # fallback: если pymorphy3 не установлен, используем токены как есть
        return tokens

    for token in tokens:
        parsed = morph.parse(token)[0]

        if parsed.tag.POS in {"PREP", "CONJ", "PRCL", "INTJ"}:
            continue

        lemmas.append(parsed.normal_form)

    return lemmas


# строит tf-idf-вектор запроса
def build_query_vector(query, idf_dict):
    tokens = tokenize(query)
    lemmas = lemmatize_tokens(tokens)

    if not lemmas:
        return {}, 0.0

    counts = Counter(lemmas)
    max_freq = max(counts.values())

    query_vector = {}
    norm_sq = 0.0

    for lemma, freq in counts.items():
        if lemma not in idf_dict:
            continue

        # нормированный tf
        tf = freq / max_freq
        tfidf = tf * idf_dict[lemma]

        query_vector[lemma] = tfidf
        norm_sq += tfidf ** 2

    query_norm = math.sqrt(norm_sq)
    return query_vector, query_norm


# косинусное сходство между запросом и документом
def cosine_similarity(query_vector, query_norm, doc_vector, doc_norm):
    if query_norm == 0.0 or doc_norm == 0.0:
        return 0.0

    dot_product = 0.0

    if len(query_vector) <= len(doc_vector):
        for term, weight in query_vector.items():
            dot_product += weight * doc_vector.get(term, 0.0)
    else:
        for term, weight in doc_vector.items():
            dot_product += weight * query_vector.get(term, 0.0)

    return dot_product / (query_norm * doc_norm)


# поиск top-k документов
def search(query, doc_vectors, doc_norms, idf_dict, top_k=10):
    query_vector, query_norm = build_query_vector(query, idf_dict)

    if not query_vector:
        return []

    results = []

    for doc_id, doc_vector in doc_vectors.items():
        score = cosine_similarity(
            query_vector,
            query_norm,
            doc_vector,
            doc_norms[doc_id]
        )

        if score > 0:
            results.append((doc_id, score))

    results.sort(key=lambda item: item[1], reverse=True)
    return results[:top_k]


def main():
    doc_urls = load_index()
    doc_vectors, doc_norms, idf_dict = load_doc_vectors()
    print("Загружено документов:", len(doc_vectors))

    while True:
        query = input("\nВведите запрос (или 'exit' для выхода): ").strip()

        if query.lower() == "exit":
            break

        results = search(query, doc_vectors, doc_norms, idf_dict, top_k=10)

        if not results:
            print("Ничего не найдено.")
            continue

        print("\nТоп результатов:")
        for i, (doc_id, score) in enumerate(results, start=1):
            url = doc_urls.get(doc_id, "URL не найден")
            print(f"{i}. doc_id={doc_id}, score={score:.6f}, {url}")


if __name__ == "__main__":
    main()
