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


@shared_task(max_retries=3, default_retry_delay=60, soft_time_limit=300, autoretry_for=(Exception,))
def get_balance(account, bank_id, login=None, password=None):
    methods = {
        1: get_balance_otk,
        2: get_balance_alfa,
        3: get_balance_modul,
        4: get_balance_raif,
        5: get_balance_psb,
    }
    method = methods.get(bank_id)
    method(account, login=login, password=password)


@shared_task(max_retries=3, default_retry_delay=60, soft_time_limit=300, autoretry_for=(Exception,))
def update_balance():
    firms = BankAccount.objects.exclude(bank_id=2)
    for firm in firms:
        get_balance.delay(firm.pk, firm.bank.pk, firm.login_bank, firm.password_bank)
    directors = Director.objects.all()
    for dir in directors:
        get_balance_alfa.delay(dir.pk)


def get_balance_otk(account=None, login=None, password=None):
    """ОК"""
    print(f'Запрос в банк ОТК {account}')
    url = "https://internetbankmb.open.ru/login"
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--start-maximized")
    options.add_argument('window-size=2560,1440')
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
    bal = float("{:.2f}".format(float(bank_account) + float(card)))
    BankAccount.objects.filter(pk=account).update(balance=bal, date_updated=timezone.now())


@shared_task(max_retries=3, default_retry_delay=60, soft_time_limit=300, autoretry_for=(Exception,))
def get_balance_alfa(name_director):
    """ОК"""
    accounts = BankAccount.objects.filter(company__directors=name_director, bank_id=2)
    if accounts:
        login, password = accounts[0].login_bank, accounts[0].password_bank
        print(f'Запрос в банк ALFA: {login}')
        url = "https://business.auth.alfabank.ru/passport/cerberus-mini-blue/dashboard-blue/corp-username?response_type=code&client_id=corp-albo&scope=openid%20corp-albo&acr_values=corp-username&non_authorized_user=true"
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument("--start-maximized")
        options.add_argument('window-size=2560,1440')
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
            WebDriverWait(browser, 60).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '/html/body/div[1]/div[1]/div[1]/section/div/div[1]/div/div/div/div[1]/button'))).click()
            list_company_temp = WebDriverWait(browser, 60).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="corp-header"]/div/div[1]/div/div/div/div[1]/div[2]/div/div[2]'))
            )
            spisok_temp = list_company_temp.text.split('\n')
            if len(spisok_temp) <= 3:
                spisok = spisok_temp[1::]
            elif len(spisok_temp) > 3:
                spisok = spisok_temp[2::]
            spisok_name = []
            start = 0
            end = 2
            while end <= len(spisok):
                mes = spisok[start:end]
                spisok_name.append(mes[0])
                BankAccount.objects.filter(company__name__iexact=mes[0], bank_id=2).update(
                    balance=mes[1].split('\u2009')[0].replace(",", ".").replace(" ", ""),
                    date_updated=timezone.now()
                )
                start = end
                end += 2
            radio_button = list_company_temp.find_elements_by_class_name('radio__container_umh77')
            count = 0


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
    options.add_argument("--start-maximized")
    options.add_argument('window-size=2560,1440')
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


def get_balance_psb(account, login=None, password=None):
    url = "https://business.psbank.ru/auth/login"
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--start-maximized")
    options.add_argument('window-size=2560,1440')
    with webdriver.Remote(desired_capabilities=options.to_capabilities(), options=options,
                          command_executor='http://127.0.0.1:4444/wd/hub') as browser:
        browser.get(url)

        WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.NAME, 'login'))).send_keys("pobeda123456")

        WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input.form-control:nth-child(1)'))).send_keys(
            "ASDzxc123qwe")

        button = WebDriverWait(browser, 180).until(
            EC.element_to_be_clickable((By.XPATH,
                                        '/html/body/smb-app/smb-login/div/div[1]/div/smb-login-form/div/form/div[3]/div[2]/psb-button/button'))).click()

        card_balance = WebDriverWait(browser, 180).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/smb-app/smb-app-main/div/div/div/div[2]/smb-main/smb-main-details/div[1]/div/smb-account-section/section/mat-tab-group/div/mat-tab-body[1]/div/div/div[4]/div/smb-account-cards/div/div/smb-card-container/div/div/div[1]/div[2]/div[2]'))).text

        card = float(card_balance.replace('ДОСТУПНО', '').split("₽")[0].replace(",", ".").replace(" ", ""))
        link = WebDriverWait(browser, 180).until(
            EC.element_to_be_clickable((By.XPATH,
                                        '//*[@id="mat-tab-label-1-1"]')))
        browser.execute_script("arguments[0].click();", link)

        chet_balance_temp = WebDriverWait(browser, 180).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 '//*[@id="mat-tab-content-1-1"]/div/div/div[2]/div/smb-account-balance/div'))).text
        chet = float(chet_balance_temp.split('₽')[0].replace(',', '.').replace(" ", ""))

        balance = card + chet

        BankAccount.objects.filter(pk=account).update(balance=balance, date_updated=timezone.now())