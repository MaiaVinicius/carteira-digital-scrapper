import datetime
from pprint import pprint

from db import model
from db.model import register_transaction, clear_transactions
from helpers import format_currency, parse_transaction

provider_id = 11


def format_json(json):
    date = json['date']
    if 'in_account' in json:
        applications = json["applications"]
        in_account = format_currency(json['in_account'])
        blocked = applications[2]
        current_account_id = 0

        blocked_amount = format_currency(blocked["amount"])
        in_account = in_account - blocked_amount

        # atualiza valor em conta corrente
        account = model.get_application_id(provider_id, 0)
        if account:
            current_account_id = account['application_id']
            model.update_balance(account['current_account_id'], current_account_id, in_account, date)

        # atualiza valor em Garantias
        blocked_application = model.get_application_id(provider_id, 15)
        if account:
            model.update_balance(blocked_application['current_account_id'], blocked_application['application_id'],
                                 blocked_amount, date)
        # atualiza valor das ações
        stocks = json['stock']
        for stock in stocks:
            current_total = format_currency(stock['current_total'])
            # buy_total = format_currency(stock["buy_total"])

            model.update_stock_balance(stock["symbol"], format_currency(stock['qtd']), current_total, date)

        # atualiza extrato
        transactions = json['movements']
        clear_transactions(provider_id)

        for transaction in transactions:
            # pprint(transaction)
            date = transaction['date_liquidation']
            try:
                datetime.datetime.strptime(date, '%Y-%m-%d')
                description = transaction["description"]

                movement_type, amount, application_type, to_account, from_account, proceed = \
                    parse_transaction(description, transaction["amount"], provider_id,
                                      date)

                if to_account == 0:
                    to_account = current_account_id

                if from_account == 0:
                    from_account = current_account_id

                # print(to_account)
                register_transaction(amount, from_account, to_account, date, description, movement_type, provider_id)
            except:
                pass
