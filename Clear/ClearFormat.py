from pprint import pprint

from db import model
from helpers import format_currency

provider_id = 11


def format_json(json):
    date = json['date']
    if 'in_account' in json:
        applications = json["applications"]
        in_account = format_currency(json['in_account'])
        blocked = applications[2]

        blocked_amount = format_currency(blocked["amount"])
        in_account = in_account - blocked_amount

        account = model.get_application_id(provider_id, 0)
        if account:
            model.update_balance(account['current_account_id'], account['application_id'], in_account, date)

        blocked_application = model.get_application_id(provider_id, 15)
        if account:
            model.update_balance(blocked_application['current_account_id'], blocked_application['application_id'], blocked_amount, date)
