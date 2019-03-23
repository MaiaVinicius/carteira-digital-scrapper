# coding=utf-8
from pprint import pprint

from db import model
from helpers import format_currency, parse_transaction


def get_provider_bank_id(bank_name):
    provider_id = None

    if bank_name == u'Banco Inter S.A.':
        provider_id = 7
    elif bank_name == u'Banco do Brasil S/A':
        provider_id = 10
    elif bank_name == u'Banco Bradesco S/A':
        provider_id = 8
    elif bank_name == u'Banco Itaú Unibanco S.A.':
        provider_id = 9

    return provider_id


def get_application_id(application_name):
    application_id = None

    if application_name == u'Conta corrente':
        application_id = 0
    elif application_name == u'Poupança':
        application_id = 1
    elif application_name == u'CDB':
        application_id = 9

    return application_id


def format_json(json):
    accounts = json['accounts']
    transactions = json['movements']
    date = json['date']

    for account in accounts:
        applications = account['applications']
        account_name = account['account_name']

        provider_id = get_provider_bank_id(account_name)

        for application in applications:
            application_type = application['application_type']
            application_type_id = get_application_id(application_type)
            balance = format_currency(application['amount'])

            db_application = model.get_application_id(provider_id, application_type_id)

            if db_application:
                model.update_balance(
                    db_application['current_account_id'],
                    db_application['application_id'],
                    balance,
                    date
                )
    for transaction in transactions:
        pprint(transaction)
        type, to_account, in_out, amount = parse_transaction(transaction["description"], transaction["amount"])
        pprint(type)
