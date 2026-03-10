# парсит файл с инвертированным списком
def load_index():
    index = {}
    with open(INDEX_FILE, encoding="utf-8") as f:
        for line in f:
            term, docs = line.strip().split(":")
            index[term] = set(docs.split())

    return index


INDEX_FILE = "inverted_index.txt"
index = load_index()
print(index)
