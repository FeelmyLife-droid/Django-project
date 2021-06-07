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
        4: get_balance_raif
    }
    method = methods.get(bank_id)
    method(account, login=login, password=password)


@shared_task(max_retries=3, default_retry_delay=60, soft_time_limit=300, autoretry_for=(Exception,))
def update_balance():
    firms = BankAccount.objects.exclude(bank_id=2)
    for firm in firms:
        get_balance.delay(firm.pk, firm.bank.pk, firm.login_bank, firm.password_bank)
    directors = Director.objects.all()[:5]
    for dir in directors:
        get_balance_alfa.delay(dir.pk)


def get_message_otk(account: int, text_mail: str):
    spisok = [str(i) for i in text_mail.split('\n')]
    start = 5
    end = 9

    while end <= len(spisok):
        mes = spisok[start:end]
        mes[3] = make_aware(datetime.strptime(mes[3], "%d %B %Y, %H:%M"))
        if not Mailbank.objects.filter(date_mail=mes[3], account_id=account).exists():
            Mailbank.objects.create(account_id=account, title_mail=mes[0], sender_mail=mes[1], content_mail=mes[2],
                                    date_mail=mes[3])
        start = end
        end += 4


def get_message_raif(account: int, text: str):
    spisok = text.split('\n')[8:]
    start = 0
    end = 4
    while end <= len(spisok):
        mes = spisok[start:end]
        mes[0] = make_aware(datetime.strptime(mes[0] + ", 00:00", "%d.%m.%Y, %H:%M"))
        if not Mailbank.objects.filter(date_mail=mes[0], account_id=account).exists():
            Mailbank.objects.create(account_id=account, title_mail=mes[1], sender_mail=mes[3], content_mail=mes[1],
                                    date_mail=mes[0])
        start = end
        end += 4


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
        browser.get('https://internetbankmb.open.ru/app/messages')
        try:
            text_mail = WebDriverWait(browser, 180).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'react-tabs__tab-panel'))).text
        except:
            pass
    bal = float("{:.2f}".format(float(bank_account) + float(card)))
    get_message_otk(account, text_mail)
    BankAccount.objects.filter(pk=account).update(balance=bal, date_updated=timezone.now())


@shared_task
def get_balance_firm_alfa(list_firm: str) -> None:
    print('Получение баланса')
    spisok = list_firm.split('\n')[2::]
    start = 0
    end = 2
    while end <= len(spisok):
        mes = spisok[start:end]
        BankAccount.objects.filter(company__name__iexact=mes[0], bank_id=2).update(
            balance=mes[1].split('\u2009')[0].replace(",", ".").replace(" ", ""),
            date_updated=timezone.now()
        )
        start = end
        end += 2


def get_mail_alfa(browser: webdriver.Remote, name_company: str) -> None:
    print('Получение почты')
    mail_company = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div/div[3]'))).text
    message = mail_company.split('\n')
    start = 0
    end = 3
    while end <= len(message):
        mes = message[start:end]
        if len(mes[1].split(' ')) == 2:
            mes[1] = make_aware(
                datetime.strptime(str(mes[1] + " " + str(datetime.now().year) + ", 00:00"), "%d %B %Y, %H:%M"))
        elif len(mes[1].split(' ')) == 3:
            mes[1] = make_aware(datetime.strptime(str(mes[1] + ", 00:00"), "%d %B %Y, %H:%M"))
        if not Mailbank.objects.filter(date_mail=mes[1], account_id__company_id__name=name_company,
                                       account_id__bank_id=2, content_mail=mes[2]).exists():
            Mailbank.objects.create(account_id__company_id__name=name_company, title_mail=mes[0],
                                    sender_mail='Альфа-Банк', content_mail=mes[2],
                                    date_mail=mes[1])
        start = end
        end += 3


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
            spisok = list_company_temp.text.split('\n')[2::]
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
            for i in range(len(radio_button)):
                radio_button[i].click()
                WebDriverWait(browser, 60).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '/html/body/div[1]/div/div[1]/section/div/div[3]/div/div/div/div[1]/div/a[7]'))
                ).click()
                name_company = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH,
                         '/html/body/div[1]/div/div[1]/section/div/div[1]/div/div/div/div[1]/button/span[2]'))).text

                mail_company = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div/div[3]'))).text
                message = mail_company.split('\n')
                start = 0
                end = 3
                while end <= len(message):
                    mes = message[start:end]
                    if len(mes[1].split(' ')) == 2:
                        mes[1] = make_aware(
                            datetime.strptime(str(mes[1] + " " + str(datetime.now().year) + ", 00:00"),
                                              "%d %B %Y, %H:%M"))
                    elif len(mes[1].split(' ')) == 3:
                        mes[1] = make_aware(datetime.strptime(str(mes[1] + ", 00:00"), "%d %B %Y, %H:%M"))
                    else:
                        mes[1] = timezone.now()
                    print(spisok_name[i])
                    account = BankAccount.objects.filter(bank_id=2, company_id__name=spisok_name[i])
                    print(account)
                    if not Mailbank.objects.filter(date_mail=mes[1], account_id=account[0].id,
                                                   content_mail=mes[2]).exists():
                        Mailbank.objects.create(account_id=account[0].id, title_mail=mes[0],
                                                sender_mail='Альфа-Банк', content_mail=mes[2],
                                                date_mail=mes[1])
                    start = end
                    end += 3
                WebDriverWait(browser, 60).until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                         '/html/body/div[1]/div[1]/div[1]/section/div/div[1]/div/div/div/div[1]/button'))).click()
                list_company_temp = WebDriverWait(browser, 60).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//*[@id="corp-header"]/div/div[1]/div/div/div/div[1]/div[2]/div/div[2]'))
                )
                radio_button = list_company_temp.find_elements_by_class_name('radio__container_umh77')


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

        browser.get('https://www.rbo.raiffeisen.ru/messages')
        mail = WebDriverWait(browser, 180).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'b-spreadsheet__main'))
        ).text
        if mail:
            get_message_raif(text=mail, account=account)

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

        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, 'login'))).send_keys("Inkom12345")

        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input.form-control:nth-child(1)'))).send_keys(
            "ASDzxc123qwe")

        button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        '/html/body/smb-app/smb-login/div/div[1]/div/smb-login-form/div/form/div[3]/div[2]/button'))).click()

        card_balance = WebDriverWait(browser, 60).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/smb-app/smb-app-main/div/div/div/div[2]/smb-main/smb-main-details/div[1]/div/smb-account-section/section/mat-tab-group/div/mat-tab-body[1]/div/div/div[4]/div/smb-account-cards/div/div/smb-card-container/div/div/div[1]/div[2]/div[2]'))).text

        card = float(card_balance.split(" ")[1].replace(',', '.'))

        chet_balance = WebDriverWait(browser, 60).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/smb-app/smb-app-main/div/div/div/div[1]/smb-aside/aside/div/div/smb-menu/div/div/ul[1]/li[2]/div[2]/scroll-bar/div/div[2]/div/a[2]/span'))).text
        chet = float(chet_balance.split('\n')[-1].split(' ')[0])
        balance = card + chet

        BankAccount.objects.filter(pk=account).update(balance=balance, date_updated=timezone.now())

        browser.get('https://business.psbank.ru/correspondence')

        mail_temp = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        '/html/body/smb-app/smb-app-main/div/div/div/div[2]/smb-correspondence/smb-letter-section/section/div[2]/smb-mailing-list/div'))).text

        mail = mail_temp.split('\n')[3::]
        if mail:
            start = 0
            end = 3
            while end <= len(mail):
                mes = mail[start:end]
                mes[0] = mes[0].replace(".", ' ')
                date = datetime.strptime(mes[0] + ', 00:00', "%d %m %Y, %H:%M")
                if not Mailbank.objects.filter(date_mail=date, account_id=account).exists():
                    Mailbank.objects.create(account_id=account, title_mail=mes[1], sender_mail=mes[2],
                                            content_mail=mes[1],
                                            date_mail=date)
                start = end
                end += 3
