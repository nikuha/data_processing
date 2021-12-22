from lxml import html
import requests
from pprint import pprint
from datetime import datetime
import json

url = 'https://yandex.ru/news/'
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
                        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}

response = requests.get(url, headers=header)
dom = html.fromstring(response.text)

news_result = dom.xpath("//div[contains(@class, 'news-top-flexible')]//div[contains(@class, 'mg-card ')]")
# print(f'news_result={len(news_result)}')
news_list = []

for item in news_result:
    news = {}
    title_result = item.xpath(".//h2[contains(@class, 'mg-card__title')]/a/text()")
    link_result = item.xpath(".//h2[contains(@class, 'mg-card__title')]/a/@href")
    source_result = item.xpath(".//span[contains(@class, 'mg-card-source__source')]/a/text()")
    time_result = item.xpath(".//span[contains(@class, 'mg-card-source__time')]/text()")

    news['title'] = title_result[0].replace('\xa0', ' ') if len(title_result) else None
    news['link'] = link_result[0] if len(link_result) else None
    news['source'] = source_result[0] if len(source_result) else None
    news['datetime'] = datetime.now().strftime("%Y-%m-%d") + ' ' + time_result[0] if len(time_result) else None

    news_list.append(news)

pprint(news_list)

# with open('yandex-news.json', 'w') as f:
#     json.dump(news_list, f)
