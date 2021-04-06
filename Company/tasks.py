import time
from random import randint

from celery import shared_task
from selenium import webdriver
from selenium.webdriver.common.by import By

from bank.models import BankAccount


@shared_task
def update_balance():
    firms = BankAccount.objects.filter(bank_id=1)
    for i in firms:
        get_balance.delay(i.bank.pk, i.login_bank, i.password_bank)


def get_balance_otk(login=None, password=None):
    print('Запрос в банк ОТК')
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(options=options, executable_path='/Users/qeqe/Desktop/Работа/OGRN-PARSER/chromedriver')
    browser.get('https://link.alfabank.ru/webclient/pages')
    time.sleep(10)
    browser.find_element_by_name('WELCOME_bound_mainPanel_loginPanel_login').send_keys('antei@mailtorg.ru')
    browser.find_element_by_name('WELCOME_bound_mainPanel_loginPanel_password').send_keys('ASDzxc123qwe')
    browser.find_element(By.XPATH, '//*[@id="isc_1P"]/table/tbody/tr/td').click()
    time.sleep(15)
    browser.get('https://link.alfabank.ru/shared/albo/dashboard')
    time.sleep(15)
    tr = browser.find_elements_by_class_name('FTWStyledLabel')
    lis = []
    for i in tr[8::]:
        if i.text:
            if i.text == '</td></tr></tbody></table></div></div>':
                break
            lis.append(i.text)
    browser.quit()
    my_dict = {}
    for index, item in enumerate(lis):
        if index % 2 == 0:
            my_dict[item] = lis[index + 1]
    print(my_dict)


def get_balance_alfa(login=None, password=None):
    print('Запрос в банк ALFA')
    time.sleep(randint(5, 10))
    print(login, '|', password)


def get_balance_modul(login=None, password=None):
    print('Запрос в банк MODUL')
    time.sleep(randint(5, 10))
    print(login, '|', password)


def get_balance_rere(login=None, password=None):
    print('Запрос в банк RERE')
    time.sleep(randint(5, 10))
    print(login, '|', password)


@shared_task
def get_balance(bank_id, login=None, password=None):
    methods = {
        1: get_balance_otk,
        2: get_balance_alfa,
        3: get_balance_modul,
        4: get_balance_rere
    }
    method = methods.get(bank_id)
    method(login=login, password=password)
