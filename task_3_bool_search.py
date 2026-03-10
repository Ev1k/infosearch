import re

# парсит файл с инвертированным списком
def load_index():
    index = {}
    with open(INDEX_FILE, encoding="utf-8") as f:
        for line in f:
            term, docs = line.strip().split(":")
            index[term] = set(docs.split())

    return index


# разбивает ввод на токены
def tokenize_query(query):
    return re.findall(r'\(|\)|and|or|not|[а-яё]+', query.lower())


#  упорядочивает слова, учитывая приоритет операций и скобки
def check_operators(tokenized_query):
    print(tokenized_query)
    output = []
    stack = []
    priority = {'not': 3, "and": 2, "or": 1}
    for token in tokenized_query:
        print(token, stack, output)
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
        print(stack)
        output.append(stack.pop())
    print(output)
    return output


INDEX_FILE = "inverted_index.txt"
index = load_index()
while True:
    query = input('Введите запрос: ').lower()
    if query == 'stop':
        break
    tokenized_query = tokenize_query(query)
    check_operators(tokenized_query)