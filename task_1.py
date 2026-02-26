import requests


urls = open('urls.txt', 'r', encoding='UTF-8')
index_file = open("index.txt", "w", encoding="UTF-8")

cnt = 1
for url in urls:
    response = requests.get(url)
    filename = f"{cnt}.txt"
    new_file = open(filename, 'w', encoding='UTF-8')
    new_file.write(response.text)
    index_file.write(f"{filename} {url}\n")
    cnt += 1
    new_file.close()

index_file.close()
urls.close()