from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

"""ОК"""
url = "https://business.auth.alfabank.ru/passport/cerberus-mini-blue/dashboard-blue/corp-username?response_type=code" \
      "&client_id=corp-albo&scope=openid%20corp-albo&acr_values=corp-username&non_authorized_user=true "
options = webdriver.ChromeOptions()
# options.add_argument('--headless')
# options.add_argument("--start-maximized")
# options.add_argument('window-size=2560,1440')
with webdriver.Remote(desired_capabilities=options.to_capabilities(), options=options,
                      command_executor='http://127.0.0.1:4444/wd/hub') as browser:
    browser.get(url)
    WebDriverWait(browser, 180).until(
        EC.presence_of_element_located((By.NAME, 'username'))).send_keys("")
    button = WebDriverWait(browser, 180).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="login-submit"]')))
    browser.execute_script("arguments[0].click();", button)
    WebDriverWait(browser, 180).until(
        EC.presence_of_element_located((By.NAME, 'password'))).send_keys("")
    button = WebDriverWait(browser, 180).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="password-submit"]')))
    browser.execute_script("arguments[0].click();", button)

    name_firm = WebDriverWait(browser, 60).until(
        EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div[1]/div[1]/section/div/div[1]/div/div/div/div[1]/button/span[2]'))).text
    status_account = False
    try:
        block = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located(
                (By.XPATH,'/html/body/div[1]/div[1]/div[2]/div/div[1]/div[2]/div[1]/div[1]/div[2]/div/div/div/div[1]/div[3]/div/a/span'))).text
        if block:
            status_account = True
    except:
        pass
    WebDriverWait(browser, 60).until(
        EC.element_to_be_clickable(
            (By.XPATH, '/html/body/div[1]/div[1]/div[1]/section/div/div[1]/div/div/div/div[1]/button'))).click()

    list_company_temp = WebDriverWait(browser, 60).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="corp-header"]/div/div[1]/div/div/div/div[1]/div[2]/div/div[2]'))
    )
    spisok_company = {}
    for i, k in enumerate(list_company_temp.find_elements_by_class_name('radio__container_1y1vr')):
        spisok_company[f'firm{[i]}'] = str(k.text).split("\n")

    for i in spisok_company.values():
        if i[0] == name_firm:
            i.append(status_account)

    for i in range(1, len(list_company_temp.find_elements_by_class_name('radio__container_1y1vr'))):
        list_company_temp.find_elements_by_class_name('radio__container_1y1vr')[i].click()
        name_firm = WebDriverWait(browser, 60).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div[1]/div[1]/section/div/div[1]/div/div/div/div[1]/button/span[2]'))).text
        status_account = False
        try:
            block = WebDriverWait(browser, 1).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/div[1]/div[2]/div/div[1]/div[2]/div[1]/div[1]/div['
                                                '2]/div/div/div/div[1]/div[3]/div/a/span'))).text
            if block:
                status_account = True
        except:
            pass
        for i in spisok_company.values():
            if i[0] == name_firm:
                i.append(status_account)
        WebDriverWait(browser, 60).until(
            EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div[1]/div[1]/div[1]/section/div/div[1]/div/div/div/div[1]/button'))).click()
        list_company_temp = WebDriverWait(browser, 60).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="corp-header"]/div/div[1]/div/div/div/div[1]/div[2]/div/div[2]'))
        )

    print(spisok_company)

    # start = 0
    # end = 2
    # while end <= len(spisok):
    #     mes = spisok[start:end]
    #     spisok_name.append(mes[0])
    #     start = end
    #     end += 2
    #     radio_button = list_company_temp.find_elements_by_class_name('company-plate')
    #
    #     count = 0
    #     while count < len(radio_button):
    #         radio_button[count].click()
    #         WebDriverWait(browser, 60).until(
    #             EC.element_to_be_clickable(
    #                 (By.XPATH, '/html/body/div[1]/div[1]/div[1]/section/div/div[3]/div/div/div/div[1]/div/a[1]'))
    #         ).click()
    #         name_company = WebDriverWait(browser, 10).until(
    #             EC.presence_of_element_located(
    #                 (By.XPATH,'/html/body/div[1]/div/div[1]/section/div/div[1]/div/div/div/div[1]/button/span[2]'))).text
