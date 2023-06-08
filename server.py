import time
import json
import random

import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from urllib.parse import quote, unquote
from fastapi.responses import PlainTextResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

from utils.config_reader import ConfigReader
from utils.logging_configuration import LoggingConfigurator

config = ConfigReader(config_rel_path='resources/config.yaml').get_config()
logger = LoggingConfigurator.get_logger(config=config, log_file_name='payments.log')

app = FastAPI()

chrome_options = Options()
chrome_options.add_argument("user-data-dir=selenium")
driver = webdriver.Chrome(options=chrome_options)


@app.post('/webhook')
async def webhook(request: Request):
    request = await request.body()
    values = unquote(request.decode('UTF-8')).split('&')
    values_dict = {}

    for item in values:
        key, value = item.split('=')
        values_dict[key] = value

    email = values_dict.get('customer_email')

    if values_dict.get('payment_status_description') == 'Успешная+оплата':
        logger.info('Successful payment' + ' ' + email)
        logger.info(json.dumps(values_dict))

        await invite(email)

    else:
        logger.error('Unsuccessful payment' + ' ' + email)
        logger.error(json.dumps(values_dict))

    response = PlainTextResponse('OK', status_code=200)

    return response


async def invite(email: str):
    action = ActionChains(driver)

    driver.get(f"https://www.notion.so/")
    time.sleep(random.uniform(0.8, 3.4))

    login_button = None
    try:
        login_button = driver.find_element(by=By.XPATH, value="//*[text()='Log in']")
    except NoSuchElementException:
        pass
    if login_button:
        action.move_to_element(to_element=login_button).click().perform()
        time.sleep(random.uniform(1.2, 2.1))

        email_input = driver.find_element(by=By.ID, value="notion-email-input-1")
        email_input.click()
        time.sleep(random.uniform(0.3, 1.1))
        email_input.send_keys(config.get("EMAIL"))
        time.sleep(random.uniform(1.1, 2.2))
        email_input.send_keys(Keys.ENTER)
        time.sleep(random.uniform(0.4, 1.3))

        password_input = driver.find_element(by=By.ID, value="notion-password-input-2")
        password_input.click()
        time.sleep(random.uniform(0.2, 0.9))
        password_input.send_keys(config.get("PASSWORD"))
        time.sleep(random.uniform(0.9, 1.2))
        password_input.send_keys(Keys.ENTER)
        time.sleep(random.uniform(5.3, 8.1))

    share_button = driver.find_element(by=By.CLASS_NAME, value="notion-topbar-share-menu")
    share_button.click()
    time.sleep(random.uniform(0.9, 2.7))

    email_input = driver.find_element(by=By.XPATH, value="//input[@placeholder='Add people, groups, or emails...']")
    email_input.click()
    time.sleep(random.uniform(0.5, 1.4))
    email_input.send_keys(email)
    time.sleep(random.uniform(1.1, 2.2))
    email_input.send_keys(Keys.ENTER)
    time.sleep(random.uniform(0.4, 1.3))

    access_button = None
    try:
        access_button = driver.find_element(by=By.XPATH, value="//*[text()='Full access']")
    except NoSuchElementException:
        logger.info(f"User with email {email} is Already in The Page")
    if access_button:
        action.move_to_element(to_element=access_button).click().perform()
        time.sleep(random.uniform(0.6, 1.1))

        can_view_button = driver.find_element(by=By.XPATH, value="//*[text()='Can view']")
        action.move_to_element(to_element=can_view_button).click().perform()
        time.sleep(random.uniform(0.4, 1))

        email_input = driver.find_element(by=By.XPATH, value="//input[@type='email']")
        email_input.send_keys(Keys.ENTER)
        time.sleep(random.uniform(2.4, 3.7))

        logger.info(f"User with email {email} is Invited")

        driver.quit()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
