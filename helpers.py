import datetime
from pprint import pprint

from db.model import get_account_by_number, get_application_id


def format_currency(value):
    value = value.replace('R$', '')
    value = value.replace(' ', '')

    value = value.replace('.', '')
    value = value.replace(',', '.')

    if value == '' or value == '-':
        value = 0
    else:
        value = float(value)

    return value


def convert_date(date):
    return datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")


def getMonthNumber(month_string):
    m = 0

    month_string = month_string.upper()

    if month_string == "JANEIRO":
        m = "01"
    elif month_string == "FEVEREIRO":
        m = "02"
    elif month_string == "MARÇO":
        m = "03"
    elif month_string == "ABRIL":
        m = "04"
    elif month_string == "MAIO":
        m = "05"
    elif month_string == "JUNHO":
        m = "06"
    elif month_string == "JULHO":
        m = "07"
    elif month_string == "AGOSTO":
        m = "08"
    elif month_string == "SETEMBRO":
        m = "09"
    elif month_string == "OUTUBRO":
        m = "10"
    elif month_string == "NOVEMBRO":
        m = "11"
    elif month_string == "DEZEMBRO":
        m = "12"

    return str(m)


def parse_transaction(str, amount, provider_id=None, buy_date=None):
    type = None
    to_account = None
    application_type = None
    application_id = None
    amount = format_currency(amount)

    str = str.upper()

    if "TED" in str:
        type = 1
        application_type = 0
        if "CTA" in str:
            to_split = str.split("CTA ")
            to_split = to_split[1].split(" -")
            to_account = to_split[0]

            if to_account:
                application_id = get_account_by_number(to_account)
    elif "PREGÃO" in str:
        type = 11
        application_type = 10
    elif "TIT PUBLICOS" in str or "TITLS.PUBL" in str:
        type = 11
        application_type = 12

        application = get_application_id(provider_id, application_type, '', buy_date)
        if application:
            application_id = application['application_id']
    elif "IR " in str or "IOF " in str:
        type = 3
    elif "TAXA " in str:
        type = 2
    elif "FUNDO DE INVESTIMENTO " in str:
        type = 11
        application_type = 11
    elif "COE  " in str:
        type = 11
        application_type = 9
    elif "COMPRA " in str:
        type = 10

    if amount > 0:
        in_out = "I"
    else:
        in_out = "O"

    return type, in_out, amount, application_type, application_id
