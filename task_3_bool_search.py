import re
import pymorphy3


# парсит файл с инвертированным списком
def load_index():
    index = {}
    with open(INDEX_FILE, encoding="utf-8") as f:
        for line in f:
            term, docs = line.strip().split(":")
            index[term] = set(docs.split())

    return index


# лемматизация одного слова
def lemmatize_word(word):
    return morph.parse(word)[0].normal_form


# разбивает ввод на токены + лемматизирует слова
def tokenize_query(query):
    tokens = re.findall(r'\(|\)|and|or|not|[а-яё]+', query.lower())
    norm_tokens = []
    for token in tokens:
        if token in ('and', 'or', 'not', '(', ')'):
            norm_tokens.append(token)
        else:
            norm_tokens.append(lemmatize_word(token))
    return norm_tokens


#  упорядочивает слова, учитывая приоритет операций и скобки
def check_operators(tokenized_query):
    output = []
    stack = []
    priority = {'not': 3, "and": 2, "or": 1}
    for token in tokenized_query:
        if token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        elif token in ("and", 'or', 'not'):
            while stack and stack[-1] != '(' and stack[-1] in priority and priority[stack[-1]] >= priority[token]:
                output.append(stack.pop())
            stack.append(token)
        else:
            output.append(token)
    while stack:
        output.append(stack.pop())
    return output


# вычисляет результат по RPN
def evaluate_rpn(rpn, index):
    stack = []
    # множество всех документов (для NOT)
    all_docs = set()
    for docs in index.values():
        all_docs |= docs
    for token in rpn:
        if token not in ("and", "or", "not"):
            stack.append(index.get(token, set()))
        elif token == "not":
            docs = stack.pop()
            stack.append(all_docs - docs)
        else:
            right = stack.pop()
            left = stack.pop()
            if token == "and":
                stack.append(left & right)
            elif token == "or":
                stack.append(left | right)

    if stack:
        return stack[0]
    else:
        return set()


morph = pymorphy3.MorphAnalyzer()
INDEX_FILE = "inverted_index.txt"
index = load_index()
while True:
    query = input('Введите запрос: ').lower()
    if query == 'stop':
        break
    tokenized_query = tokenize_query(query)
    rpn = check_operators(tokenized_query)
    result = evaluate_rpn(rpn, index)
    print("Документы:", sorted(result))