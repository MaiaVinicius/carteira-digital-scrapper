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
