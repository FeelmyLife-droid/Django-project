import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

temp_dict = {}

url = "https://business.psbank.ru/auth/login"
options = webdriver.ChromeOptions()
# options.add_argument('--headless')
options.add_argument("--start-maximized")
options.add_argument('window-size=2560,1440')
with webdriver.Remote(desired_capabilities=options.to_capabilities(), options=options,
                      command_executor='http://127.0.0.1:4444/wd/hub') as browser:
    browser.get(url)

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.NAME, 'login'))).send_keys("")

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input.form-control:nth-child(1)'))).send_keys("")

    WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH,
                                    '/html/body/smb-app/smb-login/div/div[1]/div/smb-login-form/div/form/div[3]/div[2]/psb-button/button'))).click()

    WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH,
                                    '/html/body/smb-app/smb-app-main/div/div/div/div[1]/smb-aside/aside/div/div/smb-menu/div/div/ul[1]/li[2]/a'))).click()

    info_account = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH,
                                                                                '/html/body/smb-app/smb-app-main/div/div/div/div[2]/smb-accounts/section/smb-account-groups/div/div')))

    balance_account = info_account.find_elements_by_class_name('content-row')
    in_block = False
    for i in balance_account:
        p = i.text.split('\n')
        if p[0] == "Расчётный":
            if p[-1] == "Заблокирован":
                in_block = True
            chet = float(p[2].split('₽')[0].replace(',', '.').replace(" ", ""))
        elif p[0] == "Карточный":
            number_cards = p[1].replace(' ', '')
    browser.get(f"https://business.psbank.ru/accounts/account/{number_cards}/cards")
    card_balance = WebDriverWait(browser, 60).until(
        EC.presence_of_element_located(
            (By.XPATH,
             '/html/body/smb-app/smb-app-main/div/div/div/div[2]/smb-account/section/mat-tab-group/div'))).text

    card = float(card_balance.split(" ")[-2].replace(",", ".").replace(" ", ""))

    balance = card + chet
    print(balance)
    print(in_block)

    # browser.get('https://business.psbank.ru/correspondence')
    #
    # mail_temp = WebDriverWait(browser, 10).until(
    #     EC.element_to_be_clickable((By.XPATH,
    #                                 '/html/body/smb-app/smb-app-main/div/div/div/div[2]/smb-correspondence/smb-letter-section/section/div[2]/smb-mailing-list/div'))).text
