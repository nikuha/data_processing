from pprint import pprint
import hashlib
from bs4 import BeautifulSoup as bs
import requests
import re
from pymongo import MongoClient
import json


def dict_hash(dictionary):
    d_hash = hashlib.md5()
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    d_hash.update(encoded)
    return d_hash.hexdigest()


client = MongoClient('127.0.0.1', 27017)
db = client['hh']
vacancies_collection = db.vacancies

main_url = 'https://hh.ru/search/vacancy'
params = {'text': 'Python', 'page': 1, 'items_on_page': 20}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}

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
        vacancy_data['_id'] = dict_hash(vacancy_data)
        try:
            vacancies_collection.insert_one(vacancy_data)
        except:
            pass

    print('страница: ' + str(params['page']))
    print('кол-во вакансий: ' + str(vacancies_collection.count_documents({})))
    if not dom.find('a', {'data-qa': 'pager-next'}):
        break
    params['page'] += 1
    response = requests.get(main_url, params=params, headers=headers)
