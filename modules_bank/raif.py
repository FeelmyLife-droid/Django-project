import locale
import time
from datetime import datetime

from django.utils.timezone import make_aware
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# from bank.models import Mailbank

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


# def get_message(account: int = None, text: str = None):
#     spisok = text.split('\n')[8:]
#     start = 0
#     end = 4
#
#     while end <= len(spisok):
#         mes = spisok[start:end]
#         mes[0] = make_aware(datetime.strptime(mes[0], "%d.%m.%Y"))
#         if not Mailbank.objects.filter(date_mail=mes[3], account_id=account).exists():
#             Mailbank.objeects.create(account_id=account, title_mail=mes[1], sender_mail=mes[3], content_mail=mes[1],
#                                      date_mail=mes[0])


def get_balance_raif(account=None, login=None, password=None):
    url = "https://sso.rbo.raiffeisen.ru/signin"
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument("--start-maximized")
    options.add_argument('window-size=1366,768')
    with webdriver.Remote(desired_capabilities=options.to_capabilities(), options=options,
                          command_executor='http://127.0.0.1:4444/wd/hub') as browser:
        browser.get(url)
        WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='https://www.rbo.raiffeisen.ru']"))).click()
        WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.NAME, 'login'))).send_keys('avtolaener')
        WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.NAME, 'password'))).send_keys('ASDzxc123qwe')
        WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.form__button'))).click()
        c = WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.b-home-container__accounts-list-item-balance'))).text
        balance = float(c.split("₽")[0].replace(" ", ""))
        browser.get('https://www.rbo.raiffeisen.ru/messages')
        p = WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'b-spreadsheet__table-body-inner'))
        )
        print(balance)
        print(p.text)
        # get_message(text=p, account=account)


get_balance_raif()
