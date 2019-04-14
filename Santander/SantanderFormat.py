# try:
import datetime
import os
from pprint import pprint

from bs4 import BeautifulSoup

from db import model
from db.model import register_transaction, clear_transactions
from helpers import convert_date, format_currency
import codecs

provider_id = 15


def parse_santander_html():
    dir = 'output/credit-card/'

    try:
        months = os.listdir(dir)
        clear_transactions(provider_id)

        for month_file in months:
            pprint(month_file)
            with codecs.open(dir + month_file, 'r', encoding='utf-8',
                             errors='ignore') as fdata:
                format_html(fdata.read(), month_file)
    except Exception as e:
        print(e)
        pass


# except ImportError:
#     from bs4 import BeautifulSoup

def format_html(html, filename):
    parsed_html = BeautifulSoup(html, 'html.parser')
    if "em Aberto" in filename:
        table = parsed_html.findAll("table")[13]
    else:
        table = parsed_html.findAll("table")[6]

    proximo_eh_item = False
    anterior_foi_item_divisao = False
    holder = ""

    transactions = {}

    transactions_index = -1

    trs = table.findAll("tr")

    holders_added = []

    for tr in trs:

        if proximo_eh_item:
            anterior_foi_item_divisao = False

            tem_texto = tr.find("span", attrs={'class': 'texto'})
            tem_tabela = tr.find("table")
            if tem_texto:
                if not tem_tabela:
                    tds = tr.findAll("td")
                    if transactions_index in transactions:
                        transactions[transactions_index]['transactions'].append({
                            "date": tds[0].text,
                            "description": tds[3].text,
                            "amountBRL": tds[5].text.strip(),
                            "amount": tds[7].text.strip(),
                        })
            else:
                anterior_foi_item_divisao = True

        # sempre q tem um item valido, tem uma tr com isso antes
        linha_pontilhada = tr.find("td", attrs={'class': 'linhaPontilhada'})
        if linha_pontilhada:
            proximo_eh_item = True
        else:
            proximo_eh_item = False

        if anterior_foi_item_divisao:
            texto_destaque = tr.find("span", attrs={'class': 'textoDestaque'})
            if texto_destaque:
                holder = texto_destaque.text.split(" - ")[0]
                it = {
                    'holder': holder,
                    'transactions': []
                }

                if not holder in holders_added:
                    holders_added.append(holder)
                    transactions_index += 1

                    transactions[transactions_index] = it

    db_application = model.get_application_id(provider_id, 20, '', None)
    application_id = db_application["application_id"]

    pprint(transactions)

    for i in transactions:
        holder = transactions[i]
        holder_name = holder["holder"]

        if holder_name == db_application["holder_name"]:
            for transaction in holder["transactions"]:
                date = convert_date(transaction['date'])
                amount = format_currency(transaction['amountBRL']) * -1
                description = transaction['description']

                register_transaction(amount, application_id, 0, date, description, 4, provider_id)
