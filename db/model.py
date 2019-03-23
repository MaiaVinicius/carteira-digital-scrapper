import datetime

from db import connection

mydb = connection.mydb


def update_stock(stock_symbol, application_id, balance, buy_date, initial_balance, qtd):
    mycursor = mydb.cursor()

    sql = "UPDATE current_account_applications SET balance = %s, initial_balance= %s, quantity= %s WHERE description= %s AND id= %s"

    val = (balance, initial_balance, qtd, stock_symbol, application_id)
    mycursor.execute(sql, val)

    mydb.commit()


def update_balance(current_account_id, application_id, balance, date=datetime.datetime.today().strftime('%Y-%m-%d')):
    mycursor = mydb.cursor()

    mycursor.execute("DELETE FROM balance where current_account_id=%s AND application_id=%s and DATE=%s",
                     (current_account_id, application_id, date))

    sql = "INSERT INTO balance (current_account_id, application_id, balance, date) VALUES (%s, %s, %s, %s)"
    val = (current_account_id, application_id, balance, date)
    mycursor.execute(sql, val)

    mydb.commit()

    sql = "UPDATE current_account_applications SET balance = %s, updated_at=NOW() WHERE current_account_id= %s AND id= %s"
    val = (balance, current_account_id, application_id)
    mycursor.execute(sql, val)

    mydb.commit()

    print(mycursor.rowcount, "record(s) affected")


def get_application_id(provider_id, application_type_id, description='', buy_date=None, account_id=None):
    mycursor = mydb.cursor()

    buy_date_sql = ""
    if buy_date:
        buy_date_sql = " AND ca.buy_date='" + buy_date + "'"

    current_account_sql = ""
    if account_id:
        current_account_sql = " OR ca.id='" + str(account_id) + "' "

    mycursor.execute("SELECT ca.current_account_id, ca.id, ca.description FROM current_account_applications ca"
                     " LEFT JOIN current_accounts cc ON cc.id=ca.current_account_id "
                     "WHERE cc.provider_id=%s AND ca.application_type_id=%s AND (%s LIKE concat(ca.description, '%') OR %s='') " + buy_date_sql + current_account_sql +
                     "LIMIT 1",
                     (provider_id, application_type_id, description, description))

    myresult = mycursor.fetchall()

    for x in myresult:
        return {
            'current_account_id': x[0],
            'application_id': x[1],
            'description': x[2],
        }


# def register_transaction(application_id)


def get_account_by_number(number):
    mycursor = mydb.cursor()

    mycursor.execute("SELECT caa.id FROM current_accounts ca "
                     "INNER JOIN current_account_applications caa ON ca.id=caa.current_account_id "
                     "WHERE replace(ca.account_number, '-','')=%s", (number,))

    myresult = mycursor.fetchall()

    if myresult:
        return myresult[0][0]
    else:
        return None
