import requests
import bs4

# функция для парсинга страницы url и нахождения ссылок
def find_hrefs(url):
    site = "https://dic.academic.ru"
    resp = requests.get(url)
    soup = bs4.BeautifulSoup(resp.text, 'html.parser')
    tag = soup.find('div', {"class": 'terms-wrap'})
    tags_ul = tag.find_all('ul')
    links = []
    for tag_ul in tags_ul:
        tags = tag_ul.find_all('li')
        for t in tags:
            a = t.find('a')
            href = a['href']
            links.append(site+href)
    return links


links = []
urls = [
"https://dic.academic.ru/contents.nsf/medic/?f=LdCQ0LfQsA%3D%3D&t=0LDQs9Cz0LA%3D&nt=127",
'https://dic.academic.ru/contents.nsf/medic/?f=LdCQ0LfQsA==&t=0LDQs9Cz0LA=&nt=127&p=1',
'https://dic.academic.ru/contents.nsf/medic/?f=LdCQ0LfQsA==&t=0LDQs9Cz0LA=&nt=127&p=2',
'https://dic.academic.ru/contents.nsf/medic/?f=0JDQs9Cz0Ls%3D&t=0LDQutGA0L4%3D&nt=127',
'https://dic.academic.ru/contents.nsf/medic/?f=0JDQs9Cz0Ls=&t=0LDQutGA0L4=&nt=127&p=1',
]

# проходимся по ссылкам из списка и сохраняем все найденные href на другие html страницы
for url in urls:
    links += find_hrefs(url)

# запись в файл urls.txt
f = open('urls.txt', 'w', encoding='UTF-8')
for link in links:
    f.write(link + '\n')
f.close()
