import time

import httpx
from celery import shared_task
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.common.by import By

from Director.models import Director
from bank.models import BankAccount


@shared_task
def get_balance(account, bank_id, login=None, password=None):
    methods = {
        # 1: get_balance_otk,
        # 2: get_balance_alfa,
        # 3: get_balance_modul,
        4: get_balance_raif
    }
    method = methods.get(bank_id)
    method(account, login=login, password=password)


@shared_task
def update_balance():
    firms = BankAccount.objects.exclude(bank_id=2)
    for firm in firms:
        get_balance.delay(firm.pk, firm.bank.pk, firm.login_bank, firm.password_bank)
    # directors = Director.objects.all()
    # for dir in directors:
    #     get_balance_alfa.delay(dir.pk)


def get_balance_otk(account, login=None, password=None):
    """ОК"""
    print(f'Запрос в банк ОТК {account}')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    browser = webdriver.Chrome(options=options,
                               executable_path='/Users/qeqe/Desktop/Работа/siteDjango/mysite/chromedriver')
    browser.get('https://internetbankmb.open.ru/login')
    browser.find_element_by_name('username').send_keys(str(login))
    browser.find_element_by_name('password').send_keys(str(password))
    browser.find_element_by_css_selector("[type=submit]").click()
    time.sleep(15)
    browser.get('https://internetbankmb.open.ru/app/cards')
    time.sleep(10)
    c = browser.find_element_by_xpath('//*[@id="root"]/div[4]/main/div/div[2]/div/div/div/span').text
    bal = float(c.split("₽")[0].replace(" ", "").replace(',', '.'))
    browser.close()
    BankAccount.objects.filter(pk=account).update(balance=bal, date_updated=timezone.now())


# @shared_task
def get_balance_alfa(name_director):
    accounts = BankAccount.objects.filter(company__directors=name_director, bank_id=2)
    if accounts:
        login, password = accounts[0].login_bank, accounts[0].password_bank
        print('Запрос в банк ALFA')
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        browser = webdriver.Chrome(options=options,
                                   executable_path='/Users/qeqe/Desktop/Работа/siteDjango/mysite/chromedriver')
        browser.get('https://link.alfabank.ru/webclient/pages')
        time.sleep(10)
        browser.find_element_by_name('WELCOME_bound_mainPanel_loginPanel_login').send_keys(login)
        browser.find_element_by_name('WELCOME_bound_mainPanel_loginPanel_password').send_keys(password)
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
        dict_firm = {}
        list = [i.company.name for i in accounts]
        for index, item in enumerate(lis):
            if index % 2 == 0:
                dict_firm[item] = lis[index + 1]
        for bal in dict_firm.items():
            if bal[0] in list:
                BankAccount.objects.filter(company__name=bal[0], bank_id=2).update(
                    balance=bal[1].split("R")[0].replace(",", ".").replace(" ", ""),
                    date_updated=timezone.now()
                )


def get_balance_modul(account, login=None, password=None):
    print(f'Запрос в банк MODUL {account}')
    url = "https://api.modulbank.ru/v1/account-info"
    headers = {
        "Host": "api.modulbank.ru",
        "Content-Type": "application/json",
        "Authorization": f'Bearer {login}'
    }
    response = httpx.post(url=url, headers=headers).json()
    balance = 0
    for i in response[0]['bankAccounts']:
        balance + float(i["balance"])
    BankAccount.objects.filter(pk=account).update(balance=balance, date_updated=timezone.now())


def get_balance_raif(account, login=None, password=None):
    try:
        print(f'Запрос в банк Raf {account}')
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        browser = webdriver.Chrome(options=options,
                                   executable_path='/Users/qeqe/Desktop/Работа/siteDjango/mysite/chromedriver')
        browser.get('https://sso.rbo.raiffeisen.ru/signin')
        time.sleep(3)
        browser.find_element_by_xpath("//a[@href='https://www.rbo.raiffeisen.ru']").click()
        time.sleep(3)
        browser.find_element_by_name('login').send_keys(str(login))
        browser.find_element_by_name('password').send_keys(str(password))
        browser.find_element_by_css_selector(".form__button").click()

        time.sleep(15)
        bal = browser.find_element_by_css_selector(".b-home-container__accounts-list-item-balance").text
        balance = float(bal.split('₽')[0].replace(" ", ""))
        browser.close()
        BankAccount.objects.filter(pk=account).update(balance=balance, date_updated=timezone.now())
    except Exception as e:
        print(e)
