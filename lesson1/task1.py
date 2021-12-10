import json

import requests

# api для получения перемешанной колоды карт
shuffle_url = 'https://deckofcardsapi.com/api/deck/new/shuffle/'

# выбрать из этой колоды несколько карт
cards_url = 'https://deckofcardsapi.com/api/deck/<<deck_id>>/draw/'

params = {'deck_count': 1}
response = requests.get(shuffle_url, params=params)

if response.ok:
    data = json.loads(response.text)
    deck_id = data['deck_id']
    params = {'count': 2}
    card_response = requests.get(cards_url.replace('<<deck_id>>', deck_id), params=params)
    if card_response.ok:
        with open('task1-result.json', 'w') as f:
            f.write(card_response.text)
            print('Сохранили в файл')
    else:
        print('Что-то пошло не так при получении карт!')
else:
    print('Что-то пошло не так при получении колоды!')
