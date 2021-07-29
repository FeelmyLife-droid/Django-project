import locale
import time
from datetime import datetime

from django.utils.timezone import make_aware
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# from bank.models import Mailbank

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


def get_message(account: int, text_mail: str):
    spisok = [str(i) for i in text_mail.split('\n')]
    print(spisok)
    start = 5
    end = 9

    while end <= len(spisok):
        mes = spisok[start:end]
        mes[3] = make_aware(datetime.strptime(mes[3], "%d %B %Y, %H:%M"))
        # if not Mailbank.objects.get(date_mail=mes[3], account_id=account):
        #     Mailbank.objects.create(account_id=account, title_mail=mes[0], sender_mail=mes[1], content_mail=mes[2],
        #                             date_mail=mes[3])
        start = end
        end += 4


def get_balance_otk(account=None, login=None, password=None):
    """ОК"""
    print(f'Запрос в банк ОТК')
    url = "https://internetbankmb.open.ru/login"
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    with webdriver.Remote(desired_capabilities=options.to_capabilities(), options=options,
                          command_executor='http://127.0.0.1:4444/wd/hub') as browser:
        browser.get(url)
        WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.NAME, 'username'))).send_keys('optovay')
        WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.NAME, 'password'))).send_keys('!@#123QWEasdzxc')
        WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[type=submit]'))).click()
        account = WebDriverWait(browser, 180).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/div[4]/main/div/div[3]/div/div[1]/div/div[3]/span'))

        ).text.split("₽")[0].replace(" ", "").replace(',', '.')
        in_block_status = WebDriverWait(browser, 180).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/div[4]/main/div/div[3]/div/div[1]/div/div[1]')
            )
        )
        t = len(in_block_status.find_elements_by_tag_name("svg"))
        time.sleep(3)
        browser.get('https://internetbankmb.open.ru/app/cards')
        card = 0
        try:
            c = WebDriverWait(browser, 180).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div[4]/main/div/div[2]/div'))).text
            for i in c.split("₽"):
                try:
                    card += float(i.split("\n")[-1].replace(',', '.').replace(" ", ""))
                except:
                    pass
        except:
            card = 0
        time.sleep(3)
        # browser.get('https://internetbankmb.open.ru/app/messages')
        # try:
        #     text_mail = WebDriverWait(browser, 180).until(
        #         EC.presence_of_element_located((By.CLASS_NAME, 'react-tabs__tab-panel'))).text
        # except:
        #     pass

    bal = float("{:.2f}".format(float(account) + float(card)))
    print(bal)
    if t != 1:
        print("чисто")
    print("Заблокирован")
    # print(1)
    # get_message(account, text_mail)


if __name__ == '__main__':
    get_balance_otk()
