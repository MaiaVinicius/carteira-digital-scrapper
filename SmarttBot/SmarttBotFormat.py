import datetime
from pprint import pprint

from db import model
from db.model import register_transaction, clear_transactions
from helpers import format_currency, parse_transaction

provider_id = 13


def format_json(json):
    date = json['date']
    if 'bots' in json:

        for bot in json['bots']:
            total = format_currency(bot["total"])

            account = model.get_application_id(provider_id, 19, bot["bot_name"])
            if account:
                application_id = account['application_id']
                model.update_balance(account['current_account_id'], application_id, total, date)
