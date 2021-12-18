from pprint import pprint
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['hh']

price_start = int(input('Ищем зарплату от (введите целое число) '))
find_ex = {'$or': [
    # вилка от до
    {'price.start': {'$lte': price_start}, 'price.end': {'$gte': price_start}},
    # начальная цена не меньшк указанной суммы
    {'price.start': {'$gte': price_start}},
    # конечная цена не меньше указанной суммы, но стартовой цены нет
    {'price.start': None, 'price.end': {'$gte': price_start}},
], 'price.currency': 'руб.'}

for doc in db.vacancies.find(find_ex):
    pprint(doc)
