from __future__ import annotations

import logging
import math
import os
import re
from collections import Counter

from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PAGES_DIR = os.path.join(BASE_DIR, "text")
TOKENS_INDEX = os.path.join(BASE_DIR, "tokens_index.txt")
LEMMAS_INDEX = os.path.join(BASE_DIR, "lemmas_index.txt")

TERMS_TFIDF_DIR = os.path.join(BASE_DIR, "terms_tfidf")
LEMMAS_TFIDF_DIR = os.path.join(BASE_DIR, "lemmas_tfidf")

STOP_WORDS = {
    "в","на","с","со","к","по","из","у","о","об","от","до",
    "за","для","при","без","над","под","про","между","через",
    "перед","после","около","вокруг","среди","ради","вдоль",
    "и","а","но","или","да","ни","то","не","же","бы",
    "что","как","если","чтобы","хотя","либо","также",
    "тоже","однако","зато","причём","притом","когда",
    "пока","пусть","будто","словно","точно",
    "ли","ведь","вот","вон","даже","лишь","только",
    "уже","ещё","еще","именно","разве","неужели",
    "я","ты","он","она","оно","мы","вы","они",
    "мне","мной","тебе","тебя","его","её","ее","их",
    "нас","нам","вас","вам","им","ему","ей",
    "себя","себе","собой","свой","своя","своё","свои",
    "этот","эта","это","эти","тот","та","те","то",
    "весь","вся","все","всё","всех","всем",
    "кто","что","какой","какая","какое","какие",
    "который","которая","которое","которые",
    "такой","такая","такое","такие",
    "сам","сама","само","сами",
    "так","там","тут","здесь","где","куда","откуда",
    "тогда","потом","затем","поэтому","потому",
    "очень","более","менее","можно","нужно","надо",
    "быть","был","была","было","были","есть","будет",
    "будут","будем","является","являются","стал","стала",
    "при","же","ну","нет","может","могут",
    "другой","другая","другое","другие",
    "каждый","каждая","каждое",
    "один","одна","одно","одни",
}

WORD_PATTERN = re.compile(r"^[а-яё]{2,}$", re.IGNORECASE)
DOC_FILENAME_PATTERN = re.compile(r"^\d+\.txt$")


def format_float(value: float) -> str:
    return f"{value:.12f}".rstrip("0").rstrip(".") if value else "0"


def extract_text_from_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style", "noscript", "meta", "link", "header", "footer", "nav"]):
        tag.decompose()
    return soup.get_text(separator=" ")


def tokenize(text: str) -> list[str]:
    text = text.lower()
    raw_tokens = re.split(r"[^а-яё]+", text)
    return [token for token in raw_tokens if token]


def clean_tokens_with_frequency(tokens: list[str]) -> list[str]:
    clean_tokens = []
    for token in tokens:
        if token in STOP_WORDS:
            continue
        if WORD_PATTERN.fullmatch(token):
            clean_tokens.append(token)
    return clean_tokens


def load_terms(tokens_index_path: str) -> set[str]:
    if not os.path.exists(tokens_index_path):
        raise FileNotFoundError(f"Не найден файл терминов: {tokens_index_path}")

    terms = set()
    with open(tokens_index_path, "r", encoding="utf-8") as file:
        for line in file:
            term = line.strip()
            if term:
                terms.add(term)

    return terms


def load_lemmas(lemmas_index_path: str) -> dict[str, set[str]]:
    if not os.path.exists(lemmas_index_path):
        raise FileNotFoundError(f"Не найден файл лемм: {lemmas_index_path}")

    lemma_to_forms = {}

    with open(lemmas_index_path, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split()
            if not parts:
                continue

            lemma = parts[0]
            forms = set(parts[1:])

            if lemma and forms:
                lemma_to_forms[lemma] = forms

    return lemma_to_forms


def load_documents() -> list[tuple[str, list[str]]]:
    if not os.path.isdir(PAGES_DIR):
        raise FileNotFoundError(f"Папка с документами не найдена: {PAGES_DIR}")

    documents = []

    filenames = sorted(
        filename for filename in os.listdir(PAGES_DIR)
        if DOC_FILENAME_PATTERN.fullmatch(filename)
    )

    if not filenames:
        raise ValueError(f"В папке {PAGES_DIR} не найдено документов вида 1.txt, 2.txt и т.д.")

    for filename in filenames:
        filepath = os.path.join(PAGES_DIR, filename)

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                html = file.read()
        except UnicodeDecodeError:
            with open(filepath, "r", encoding="cp1251") as file:
                html = file.read()

        text = extract_text_from_html(html)
        tokens = clean_tokens_with_frequency(tokenize(text))
        documents.append((filename, tokens))

    return documents


def build_term_counters(
    documents: list[tuple[str, list[str]]],
    allowed_terms: set[str],
) -> list[tuple[str, Counter[str], int]]:
    prepared_docs = []

    for filename, tokens in documents:
        filtered_tokens = [token for token in tokens if token in allowed_terms]
        term_counter = Counter(filtered_tokens)
        total_terms = len(filtered_tokens)
        prepared_docs.append((filename, term_counter, total_terms))

    return prepared_docs


def build_lemma_counters(
    documents: list[tuple[str, list[str]]],
    lemma_to_forms: dict[str, set[str]],
) -> list[tuple[str, Counter[str], int]]:
    prepared_docs = []

    form_to_lemma = {}
    for lemma, forms in lemma_to_forms.items():
        for form in forms:
            form_to_lemma[form] = lemma

    for filename, tokens in documents:
        lemma_counter = Counter()

        for token in tokens:
            lemma = form_to_lemma.get(token)
            if lemma:
                lemma_counter[lemma] += 1

        total_terms = sum(lemma_counter.values())
        prepared_docs.append((filename, lemma_counter, total_terms))

    return prepared_docs


def compute_idf(counters: list[Counter[str]], total_docs: int) -> dict[str, float]:
    doc_freq = Counter()

    for counter in counters:
        for item in counter.keys():
            doc_freq[item] += 1

    return {
        item: math.log(total_docs / df)
        for item, df in doc_freq.items()
        if df > 0
    }


def save_tfidf_file(
    filepath: str,
    tf_counter: Counter[str],
    total_terms: int,
    idf_map: dict[str, float],
) -> None:
    with open(filepath, "w", encoding="utf-8") as file:
        for item in sorted(tf_counter.keys()):
            tf = tf_counter[item] / total_terms if total_terms else 0.0
            idf = idf_map.get(item, 0.0)
            tf_idf = tf * idf
            file.write(f"{item} {format_float(idf)} {format_float(tf_idf)}\n")


def save_term_results(
    prepared_docs: list[tuple[str, Counter[str], int]],
    term_idf: dict[str, float],
) -> None:
    os.makedirs(TERMS_TFIDF_DIR, exist_ok=True)

    for filename, term_counter, total_terms in prepared_docs:
        output_path = os.path.join(TERMS_TFIDF_DIR, filename)
        save_tfidf_file(output_path, term_counter, total_terms, term_idf)


def save_lemma_results(
    prepared_docs: list[tuple[str, Counter[str], int]],
    lemma_idf: dict[str, float],
) -> None:
    os.makedirs(LEMMAS_TFIDF_DIR, exist_ok=True)

    for filename, lemma_counter, total_terms in prepared_docs:
        output_path = os.path.join(LEMMAS_TFIDF_DIR, filename)
        save_tfidf_file(output_path, lemma_counter, total_terms, lemma_idf)


def main() -> None:
    terms = load_terms(TOKENS_INDEX)
    lemma_to_forms = load_lemmas(LEMMAS_INDEX)
    documents = load_documents()

    total_docs = len(documents)

    term_docs = build_term_counters(documents, terms)
    lemma_docs = build_lemma_counters(documents, lemma_to_forms)

    term_counters = [counter for _, counter, _ in term_docs]
    lemma_counters = [counter for _, counter, _ in lemma_docs]
    term_idf = compute_idf(term_counters, total_docs)
    lemma_idf = compute_idf(lemma_counters, total_docs)
    save_term_results(term_docs, term_idf)
    save_lemma_results(lemma_docs, lemma_idf)

if __name__ == "__main__":
    main()