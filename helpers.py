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
