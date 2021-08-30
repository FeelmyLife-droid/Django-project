import httpx


def get_balance_modul(account=None,
                      login='',
                      password=None):
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
        a[f"ООО{i['companyName'].split('ОТВЕТСТВЕННОСТЬЮ')[-1]}"] = {k['accountName']: (k['balance'], k['status']) for k
                                                                     in i['bankAccounts']}

    for i in a.items():
        company = i[0]
        balance: int = 0
        in_block = False
        for k in i[1].values():
            balance += k[0]
            if k[1] != "New":
                in_block = True
        print(company)
        print(balance)
        print(in_block)


get_balance_modul()
