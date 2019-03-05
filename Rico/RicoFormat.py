from pprint import pprint

from db import model
from helpers import format_currency

provider_id = 12


def format_json(json):
    applications = json['applications']
    date = json['date']

    in_account = format_currency(json['in_account'])

    account = model.get_application_id(provider_id, 0)
    if account:
        model.update_balance(account['current_account_id'], account['application_id'], in_account, date)

    for application in applications:
        db_application = model.get_application_id(provider_id, application['type_id'], application['description'])

        balance = format_currency(application['balance'])


        if db_application:
            model.update_balance(
                db_application['current_account_id'],
                db_application['application_id'],
                balance,
                date
            )
