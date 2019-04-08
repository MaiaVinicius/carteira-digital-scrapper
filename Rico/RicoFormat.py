from pprint import pprint

from db import model
from db.model import register_transaction, clear_transactions
from helpers import format_currency, parse_transaction, convert_date

provider_id = 12


def format_json(json):
    applications = json['applications']
    date = json['date']

    in_account = format_currency(json['in_account'])

    # atualiza valor da conta corrente
    account = model.get_application_id(provider_id, 0)
    if account:
        current_account_id = account['application_id']
        model.update_balance(account['current_account_id'], current_account_id, in_account, date)

    # atualiza valor das aplicações (tesouro, fundo, COE...)
    for application in applications:
        db_application = model.get_application_id(provider_id, application['type_id'], application['description'],
                                                  convert_date(application['buy_date']))

        balance = format_currency(application['balance'])

        if db_application:
            model.update_balance(
                db_application['current_account_id'],
                db_application['application_id'],
                balance,
                date
            )

    # atualiza extrato
    transactions = json['movements']
    clear_transactions(provider_id)

    for transaction in transactions:
        # pprint(transaction)
        date = convert_date(transaction['date_liquidation'])
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
