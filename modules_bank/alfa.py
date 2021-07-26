import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

temp_dict = {}


def get_mail(browser: webdriver.Remote, name_company: str) -> None:
    mail_company = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div/div[3]'))).text
    temp_dict[name_company]['mail'] = mail_company.split('\n')
    # return mail_company.split('\n')


def get_balance_firm(list_firm: str) -> None:
    spisok_temp = list_firm.split('\n')
    if len(spisok_temp) <= 3:
        spisok = spisok_temp[1::]
    elif len(spisok_temp) > 3:
        spisok = spisok_temp[2::]

    start = 0
    end = 2
    while end <= len(spisok):
        mes = spisok[start:end]
        temp_dict[mes[0]] = {'balance': mes[1].split('\u2009')[0]}
        start = end
        end += 2


url = "https://business.auth.alfabank.ru/passport/cerberus-mini-blue/dashboard-blue/corp-username?response_type=code&client_id=corp-albo&scope=openid%20corp-albo&acr_values=corp-username&non_authorized_user=true"
options = webdriver.ChromeOptions()
# options.add_argument('--headless')

with webdriver.Remote(desired_capabilities=options.to_capabilities(), options=options,
                      command_executor='http://127.0.0.1:4444/wd/hub') as browser:
    browser.get(url)

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.NAME, 'username'))).send_keys("Zerno@mailtorg.ru")

    button = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="login-submit"]')))
    browser.execute_script("arguments[0].click();", button)

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.NAME, 'password'))).send_keys("ASDzxc123qwe")

    button = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="password-submit"]')))
    browser.execute_script("arguments[0].click();", button)
    WebDriverWait(browser, 60).until(
        EC.element_to_be_clickable(
            (By.XPATH, '/html/body/div[1]/div[1]/div[1]/section/div/div[1]/div/div/div/div[1]/button'))).click()
    time.sleep(1)
    list_company_temp = WebDriverWait(browser, 60).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="corp-header"]/div/div[1]/div/div/div/div[1]/div[2]/div/div[2]'))
    )
    get_balance_firm(list_company_temp.text)

    radio_button = list_company_temp.find_elements_by_class_name('radio__container_umh77')
    count = 0
    while count <= len(radio_button):
        radio_button[count].click()
        WebDriverWait(browser, 60).until(
            EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div[1]/div/div[1]/section/div/div[3]/div/div/div/div[1]/div/a[7]'))
        ).click()
        name_company = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div/div[1]/section/div/div[1]/div/div/div/div[1]/button/span[2]'))).text
        get_mail(browser, name_company)
        WebDriverWait(browser, 60).until(
            EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div[1]/div[1]/div[1]/section/div/div[1]/div/div/div/div[1]/button'))).click()
        list_company_temp = WebDriverWait(browser, 60).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="corp-header"]/div/div[1]/div/div/div/div[1]/div[2]/div/div[2]'))
        )
        radio_button = list_company_temp.find_elements_by_class_name('radio__container_umh77')
        count += 1

    print(temp_dict)
    print(1)

    # mail_company = get_mail(browser)
    # print(mail_company)
    # name_company = WebDriverWait(browser, 10).until(
    #     EC.presence_of_element_located(
    #         (By.XPATH, '/html/body/div[1]/div/div[1]/section/div/div[1]/div/div/div/div[1]/button/span[2]'))).text_mail
    # lis = []
    # for i in tr.strip().split('\n'):
    #     lis.append(i.lstrip())
    # print(lis)
