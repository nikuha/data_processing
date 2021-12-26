from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.mvideo.ru/')

trend_button_xpath = "//span[contains(text(),'В тренде')]"
carousel_xpath = "/following::mvid-carousel[1]"
next_button_xpath = "//button[contains(@class, 'forward')][1]"
# products_xpath = "//mvid-product-cards-group"
product_name_xpath = "//a[@_ngcontent-serverapp-c242 and not(contains(@class, 'img'))]"
trend_button = driver.find_elements(By.XPATH, trend_button_xpath)

driver.implicitly_wait(5)

i = 0
while not trend_button and i < 10:
    try:
        trend_button = driver.find_element(By.XPATH, trend_button_xpath)
    except NoSuchElementException as e:
        trend_button = None
    driver.execute_script(f"window.scrollTo(0, {i*400});")
    time.sleep(5)
    i += 1

if trend_button:
    actions = ActionChains(driver)
    actions.move_to_element(trend_button)
    actions.perform()
    trend_button.click()
    carousel = driver.find_element(By.XPATH, trend_button_xpath + carousel_xpath)
    next_button = driver.find_element(By.XPATH, trend_button_xpath + carousel_xpath + next_button_xpath)
    try:
        while next_button.is_enabled():
            time.sleep(5)
            next_button.click()
    except ElementClickInterceptedException as e:
        pass

    products = driver.find_elements(By.XPATH, trend_button_xpath + carousel_xpath + product_name_xpath)

    client = MongoClient('127.0.0.1', 27017)
    db = client['mvideo']
    products_collection = db.products

    for el in products:
        products_collection.insert_one({
            'name': el.text,
            'link': el.get_attribute('href')
        })

driver.close()
