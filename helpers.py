import datetime
from pprint import pprint

from db.model import get_account_by_number, get_application_id, get_application_id_by_amount


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
    if date:
        return datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")
    else:
        return False


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
    proceed = True
    to_account = None
    from_account = None
    application_type = None
    amount = format_currency(amount)

    str = str.upper()

    if "TAXA " in str or "SEGURO" in str or "DOC/TED INTERNET" in str:
        type = 2
        to_account = -1
        # from_account = 0
    elif "PAGTO" in str or "PORTABILIDADE" in str:
        type = 12
        # to_account = 0
    elif ("TED" in str or "DOC" in str or "TRANSFERÊNCIA" in str or "TRANSF.AUT" in str) and "FUNDO" not in str:
        type = 1
        # application_type = 0

        # pega a conta para qual foi feita a transferencia
        if amount < 0:
            # from_account = 0
            if "CTA" in str:
                to_split = str.split("CTA ")
                to_split = to_split[1].split(" -")
                to_account = to_split[0]

                if to_account:
                    to_account = get_account_by_number(to_account)
        # else:
        #     to_account = 0
    elif "PREGÃO" in str:
        type = 11
        application_type = 10

        # pega qual ação foi aplicada
        if amount < 0:
            to_account = get_application_id_by_amount(amount * -1, application_type)
            # from_account = 0

    elif "TIT PUBLICOS" in str or "TITLS.PUBL" in str:
        type = 11
        application_type = 12

        if amount < 0:
            # from_account = 0
            application = get_application_id(provider_id, application_type, '', buy_date)
            if application:
                to_account = application['application_id']
        # else:
        #     to_account = 0

    elif "IR " in str or "IOF" in str or "LIS" in str or "ISS" in str or "IRRF" in str:
        type = 3
        # from_account = 0
        to_account = -2
    elif "FUNDO" in str:
        type = 11
        application_type = 11
        # pega qual ação foi aplicada
        if amount < 0:
            to_account = get_application_id_by_amount(amount * -1, application_type)
            # from_account = 0
        # else:
        # from_account = get_application_id_by_amount(amount, application_type)
        # to_account = 0
    elif "COE  " in str:
        type = 11
        application_type = 9
        # from_account = 0
    elif "CDB " in str:
        type = 11
        application_type = 9
        # from_account = 0
    elif "POUPANÇA " in str:
        type = 11
        application_type = 1

        if amount < 0:
            to_account = get_application_id_by_amount(amount * -1, application_type)
        # from_account = 0
    elif "AJUSTE DAY-TRADE " in str:
        type = 5
        application_type = 15
        if amount > 0:
            from_account = -1
        else:
            to_account = -1
        # to_account = 0
    elif "COMPRA " in str:
        type = 10
        # from_account = 0
    elif "CANCELADO" in str:
        proceed = False
        # from_account = 0

    if from_account == None:
        if amount < 0:
            from_account = 0
    if to_account == None:
        if amount > 0:
            to_account = 0

    return type, amount, application_type, to_account, from_account, proceed
