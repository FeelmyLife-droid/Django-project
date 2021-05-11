from datetime import date


def check_age(date_of_birth: date) -> int:
    age = (date.today() - date_of_birth)
    return int(age.days/365.25)
