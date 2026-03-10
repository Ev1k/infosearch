# парсит файл с инвертированным списком
def load_index():
    index = {}
    with open(INDEX_FILE, encoding="utf-8") as f:
        for line in f:
            term, docs = line.strip().split(":")
            index[term] = set(docs.split())

    return index

def check_operators(words):
    if "and" in words:
        pass
    elif 'or' in words:
        pass
    elif 'not' in words:
        pass


INDEX_FILE = "inverted_index.txt"
index = load_index()
while True:
    query = input('Введите запрос: ')
    if query == 'stop':
        break
    words = query.split()
    words = list(map(lambda x: x.lower(), words))
    print(words)
    check_operators(words)