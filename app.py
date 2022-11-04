import requests
import numpy as np
import re
import time
import telegram
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from config import *

QUOTATION_MARK_REGEX = "('|\")"

PUNCH_BUTTON_NAME = "punchConfig.punchButton ="


def init_bot():
    global bot
    bot = telegram.Bot(TELEGRAM_BOT_TOKEN)


def init_config():
    global button_selector
    button_selector = None


def send_message_by_tg(message: str):
    global bot
    print(message)
    bot.send_message(text=message, chat_id=TELEGRAM_ID)


def split_line_to_value(line: str) -> str:
    return re.split(QUOTATION_MARK_REGEX, line)[2]


def get_config() -> bool:
    global button_selector

    config_file = requests.get(CONFIG_URL).text
    text_array = np.array(config_file.split("\n"))

    for line in text_array:
        if PUNCH_BUTTON_NAME in line:
            button_selector = split_line_to_value(line)

    return button_selector is not None


def trigger_login_form(driver):
    driver.get(EVENT_PAGE_URL)
    driver.find_element(By.CSS_SELECTOR, button_selector).click()
    time.sleep(1)


def login(driver):
    driver.find_element(By.ID, "memId").send_keys(ACCOUNT)
    driver.execute_script("document.querySelector('#passwd').value='" + PASSWORD + "'")
    driver.execute_script(
        "document.querySelector('#loginForm > dl.leftArea > dd.loginBtn > input[type=image]').click()"
    )
    time.sleep(1)


def wait_for_alert(driver):
    return (
        WebDriverWait(driver, 100)
        .until(EC.presence_of_element_located((By.ID, "swal2-title")))
        .text
    )


def punch():
    global button_selector

    driver = webdriver.Chrome()

    trigger_login_form(driver)
    login(driver)

    # punch!
    driver.execute_script("punchReg()")

    msg = MSG_PREFIX + wait_for_alert(driver)
    send_message_by_tg(msg)

    driver.quit()


def main():
    init_bot()
    init_config()

    if not get_config():
        print("get config failed!")
        return

    while True:
        if datetime.now().hour == RUN_AT_HOUR:
            punch()
        print(f"zzz for {SLEEP_INTERVAL_SECONDS} seconds...")
        time.sleep(SLEEP_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
