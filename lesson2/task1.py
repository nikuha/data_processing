from bs4 import BeautifulSoup as bs
import requests
import re
import json

main_url = 'https://hh.ru/search/vacancy'
params = {'text': 'Python', 'page': 1}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}

vacancies_list = []
response = requests.get(main_url, params=params, headers=headers)

while response.ok:
    dom = bs(response.text, 'html.parser')
    results = dom.find('div', {'data-qa': 'vacancy-serp__results'})
    if not results:
        break
    vacancies = results.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in vacancies:
        vacancy_data = {}
        link_tag = vacancy.find('a', {'class': 'bloko-link'})
        price_tag = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        vacancy_data['name'] = link_tag.text
        vacancy_data['link'] = link_tag.get('href')
        price = {'start': None, 'end': None, 'currency': None}  # , 'price_text': None
        if price_tag:
            # price['price_text'] = price_tag.text
            match = re.search(r'от(\s+)(\d+)(\s+)(\d+)(\s+)(.+)$', price_tag.text)
            if match:
                price['start'] = int(match[2] + match[4])
                price['currency'] = match[6]
            else:
                match = re.search(r'до(\s+)(\d+)(\s+)(\d+)(\s+)(.+)$', price_tag.text)
                if match:
                    price['end'] = int(match[2] + match[4])
                    price['currency'] = match[6]
                else:
                    match = re.search(r'(\d+)(\s+)(\d+)(\s+)–(\s+)(\d+)(\s+)(\d+)(\s+)(.+)$', price_tag.text)
                    if match:
                        price['start'] = int(match[1] + match[3])
                        price['end'] = int(match[6] + match[8])
                        price['currency'] = match[10]
        vacancy_data['price'] = price
        vacancy_data['site_link'] = response.url
        vacancies_list.append(vacancy_data)

    print('страница: ' + str(params['page']))
    print('кол-во вакансий: ' + str(len(vacancies_list)))
    if not dom.find('a', {'data-qa': 'pager-next'}):
        break
    params['page'] += 1
    response = requests.get(main_url, params=params, headers=headers)

with open('results.json', 'w') as f:
    json.dump(vacancies_list, f)
