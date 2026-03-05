import requests
import os

os.makedirs("text", exist_ok=True)

with open('urls.txt', 'r', encoding='UTF-8') as urls, \
     open("index.txt", "w", encoding="UTF-8") as index_file:

    cnt = 1
    for url in urls:
        url = url.strip()
        response = requests.get(url)

        filename = f"{cnt}.txt"
        filepath = os.path.join("text", filename)

        with open(filepath, 'w', encoding='UTF-8') as new_file:
            new_file.write(response.text)

        index_file.write(f"{filename} {url}\n")
        cnt += 1