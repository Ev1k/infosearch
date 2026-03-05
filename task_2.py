import os
import re
from bs4 import BeautifulSoup
import pymorphy3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAGES_DIR = BASE_DIR 
TOKENS_DIR = os.path.join(BASE_DIR, "tokens")
LEMMAS_DIR = os.path.join(BASE_DIR, "lemmas")
TOKENS_INDEX = os.path.join(BASE_DIR, "tokens_index.txt")
LEMMAS_INDEX = os.path.join(BASE_DIR, "lemmas_index.txt")

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

def extract_text(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style", "noscript", "meta", "link", "header", "footer", "nav"]):
        tag.decompose()
    return soup.get_text(separator=" ")

def tokenize(text: str) -> list[str]:
    return [t for t in re.split(r"[^а-яё]+", text.lower()) if t]

def clean_tokens(tokens: list[str]) -> list[str]:
    return sorted({t for t in tokens if WORD_PATTERN.match(t) and t not in STOP_WORDS})

def lemmatize(tokens: list[str], morph: pymorphy3.MorphAnalyzer) -> dict[str, set[str]]:
    lemmas = {}
    for t in tokens:
        lemma = morph.parse(t)[0].normal_form
        if lemma not in STOP_WORDS:
            lemmas.setdefault(lemma, set()).add(t)
    return lemmas

def process_documents(pages_dir: str = PAGES_DIR) -> None:
    if not os.path.isdir(pages_dir):
        return
    os.makedirs(TOKENS_DIR, exist_ok=True)
    os.makedirs(LEMMAS_DIR, exist_ok=True)

    html_files = sorted(f for f in os.listdir(pages_dir) if f.endswith(".txt"))
    morph = pymorphy3.MorphAnalyzer()
    all_tokens = set()
    all_lemmas = {}

    for filename in html_files:
        filepath = os.path.join(pages_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                html = f.read()
        except:
            continue

        text = extract_text(html)
        tokens = clean_tokens(tokenize(text))
        lemmas = lemmatize(tokens, morph)

        all_tokens.update(tokens)
        for lemma, toks in lemmas.items():
            if lemma not in all_lemmas:
                all_lemmas[lemma] = set()
            all_lemmas[lemma].update(toks)

    with open(TOKENS_INDEX, "w", encoding="utf-8") as f:
        for t in sorted(all_tokens):
            f.write(t + "\n")

    with open(LEMMAS_INDEX, "w", encoding="utf-8") as f:
        for lemma, toks in sorted(all_lemmas.items()):
            f.write(f"{lemma} {' '.join(sorted(toks))}\n")

if __name__ == "__main__":
    process_documents()