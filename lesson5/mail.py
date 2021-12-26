from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from datetime import datetime

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://account.mail.ru/login')

driver.implicitly_wait(20)

elem = driver.find_element(By.NAME, 'username')
elem.send_keys('test@mail.ru')  # логин
elem.send_keys(Keys.ENTER)

elem = driver.find_element(By.NAME, 'password')
elem.send_keys('password')  # пароль
elem.send_keys(Keys.ENTER)

# собираем только уникальные ссылки
emails_set = set()

for i in range(5):
    articles = driver.find_elements(By.XPATH, "//a[contains(@class, 'js-letter-list-item')]")
    for el in articles:
        emails_set.add(el.get_attribute('href'))
    actions = ActionChains(driver)
    actions.move_to_element(articles[-1])
    actions.perform()
    time.sleep(5)

client = MongoClient('127.0.0.1', 27017)
db = client['mailru']
emails = db.emails
emails.delete_many({})

for link in emails_set:
    driver.get(link)
    author = driver.find_element(By.XPATH, "//div[contains(@class, 'letter__author')]/span[contains(@class, 'letter-contact')]").text
    date = driver.find_element(By.XPATH, "//div[contains(@class, 'letter__author')]/div[contains(@class, 'letter__date')]").text
    subject = driver.find_element(By.XPATH, "//h2[contains(@class, 'thread-subject')]").text
    text = driver.find_element(By.XPATH, "//div[contains(@class, 'letter-body__body-content')]").text
    email = {
        'author': author,
        'datetime':date.replace('Сегодня,', datetime.now().strftime("%Y-%m-%d")),
        'subject': subject,
        'text': text
    }
    emails.insert_one(email)

driver.close()
