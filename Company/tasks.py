import locale
import time
from datetime import datetime

import httpx
from celery import shared_task
from django.utils import timezone
from django.utils.timezone import make_aware
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Director.models import Director
from bank.models import BankAccount, Mailbank

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


@shared_task(max_retries=10, default_retry_delay=20, soft_time_limit=300, autoretry_for=(Exception,))
def get_balance(account, bank_id, login=None, password=None):
    methods = {
        1: get_balance_otk,
        # 2: get_balance_alfa,
        # 3: get_balance_modul,
        # 4: get_balance_raif
    }
    method = methods.get(bank_id)
    method(account, login=login, password=password)


@shared_task(max_retries=10, default_retry_delay=20, soft_time_limit=300, autoretry_for=(Exception,))
def update_balance():
    firms = BankAccount.objects.exclude(bank_id=2)
    for firm in firms:
        get_balance.delay(firm.pk, firm.bank.pk, firm.login_bank, firm.password_bank)
    # directors = Director.objects.all()
    # for dir in directors:
    #     get_balance_alfa.delay(dir.pk)


def get_message(account: int, text_mail: str):
    spisok = [str(i) for i in text_mail.split('\n')]
    start = 0
    end = 4

    while end <= len(spisok):
        mes = spisok[start:end]
        mes[3] = make_aware(datetime.strptime(mes[3], "%d %B %Y, %H:%M"))
        if not Mailbank.objects.filter(date_mail=mes[3]).exists():
            Mailbank.objects.create(account_id=account, title_mail=mes[0], sender_mail=mes[1], content_mail=mes[2],
                                    date_mail=mes[3])
        start = end
        end += 4


def get_balance_otk(account=None, login=None, password=None):
    """ОК"""
    print(f'Запрос в банк ОТК {account}')
    url = "https://internetbankmb.open.ru/login"
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    with webdriver.Remote(desired_capabilities=options.to_capabilities(), options=options,
                          command_executor='http://127.0.0.1:4444/wd/hub') as browser:
        browser.get(url)
        WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.NAME, 'username'))).send_keys(str(login))
        WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.NAME, 'password'))).send_keys(str(password))
        WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[type=submit]'))).click()
        bank_account = WebDriverWait(browser, 180).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/div[4]/main/div/div[3]/div/div[1]/div/div[3]/span'))
        ).text.split("₽")[0].replace(" ", "").replace(',', '.')
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
        browser.get('https://internetbankmb.open.ru/app/messages')
        try:
            text_mail = WebDriverWait(browser, 180).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'tabWrapper___J3M8A'))).text
        except:
            pass
    bal = float("{:.2f}".format(float(bank_account) + float(card)))
    get_message(account, text_mail)
    BankAccount.objects.filter(pk=account).update(balance=bal, date_updated=timezone.now())


# @shared_task(max_retries=10, default_retry_delay=20, soft_time_limit=300, autoretry_for=(Exception,))
def get_balance_alfa(name_director):
    """ОК"""
    accounts = BankAccount.objects.filter(company__directors=name_director, bank_id=2)
    if accounts:
        login, password = accounts[0].login_bank, accounts[0].password_bank
        print(f'Запрос в банк ALFA: {login}')
        url = "https://business.auth.alfabank.ru/passport/cerberus-mini-blue/dashboard-blue/corp-username?response_type=code&client_id=corp-albo&scope=openid%20corp-albo&acr_values=corp-username&non_authorized_user=true"
        url1 = 'https://link.alfabank.ru/shared/albo/dashboard'
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        with webdriver.Remote(desired_capabilities=options.to_capabilities(), options=options,
                              command_executor='http://127.0.0.1:4444/wd/hub') as browser:
            browser.get(url)
            WebDriverWait(browser, 180).until(
                EC.presence_of_element_located((By.NAME, 'username'))).send_keys(str(login))
            button = WebDriverWait(browser, 180).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="login-submit"]')))
            browser.execute_script("arguments[0].click();", button)
            WebDriverWait(browser, 180).until(
                EC.presence_of_element_located((By.NAME, 'password'))).send_keys(str(password))
            button = WebDriverWait(browser, 180).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="password-submit"]')))
            browser.execute_script("arguments[0].click();", button)
            time.sleep(10)
            browser.get(url1)
            tr = WebDriverWait(browser, 180).until(EC.presence_of_element_located((By.ID, 'isc_4Q'))).text
            lis = []
            for i in tr.strip().split('\n'):
                lis.append(i.lstrip())
        dict_firm = {}
        list = [str(i.company.name).upper() for i in accounts]
        for index, item in enumerate(lis):
            if index % 2 == 0:
                dict_firm[item] = lis[index + 1]
        for bal in dict_firm.items():
            if bal[0] in list:
                BankAccount.objects.filter(company__name__iexact=bal[0], bank_id=2).update(
                    balance=bal[1].split("R")[0].replace(",", ".").replace(" ", ""),
                    date_updated=timezone.now()
                )


def get_balance_modul(account=None, login=None, password=None):
    print(f'Запрос в банк MODUL {account}')
    url = "https://api.modulbank.ru/v1/account-info"
    headers = {
        "Host": "api.modulbank.ru",
        "Content-Type": "application/json",
        "Authorization": f'Bearer {login}'
    }
    response = httpx.post(url=url, headers=headers).json()
    a = {}
    for i in response:
        a[f"ООО{i['companyName'].split('ОТВЕТСТВЕННОСТЬЮ')[-1]}"] = {k['accountName']: k['balance'] for k in
                                                                     i['bankAccounts']}
    for i in a.items():
        company = i[0]
        balance: int = 0
        for k in i[1].values():
            balance += k
        BankAccount.objects.filter(company__name__iexact=company, bank_id=3).update(
            balance=balance,
            date_updated=timezone.now()
        )
        print(balance)


def get_balance_raif(account, login=None, password=None):
    url = "https://sso.rbo.raiffeisen.ru/signin"
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    with webdriver.Remote(desired_capabilities=options.to_capabilities(), options=options,
                          command_executor='http://127.0.0.1:4444/wd/hub') as browser:
        browser.get(url)
        WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='https://www.rbo.raiffeisen.ru']"))).click()
        WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.NAME, 'login'))).send_keys(str(login))
        WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.NAME, 'password'))).send_keys(str(password))
        WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.form__button'))).click()
        c = WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.b-home-container__accounts-list-item-balance'))).text
        balance = float(c.split("₽")[0].replace(" ", ""))
        print(balance)
        BankAccount.objects.filter(pk=account).update(balance=balance, date_updated=timezone.now())
