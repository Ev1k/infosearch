import re

# парсит файл с инвертированным списком
def load_index():
    index = {}
    with open(INDEX_FILE, encoding="utf-8") as f:
        for line in f:
            term, docs = line.strip().split(":")
            index[term] = set(docs.split())

    return index

def tokenize_query(query):
    return re.findall(r'\(|\)|and|or|not|[а-яё]+', query.lower())

def check_operators(tokenized_query):
    for token in tokenized_query:
        if token == '(':
            pass
        elif token == '(':
            pass
        elif token == "and":
            pass
        elif token == "or":
            pass
        elif token == "not":
            pass
        else:
            pass


INDEX_FILE = "inverted_index.txt"
index = load_index()
while True:
    query = input('Введите запрос: ').lower()
    if query == 'stop':
        break
    tokenized_query = tokenize_query(query)
    check_operators(tokenized_query)