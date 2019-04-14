import datetime

from db import connection

mydb = connection.mydb


def update_stock(stock_symbol, application_id, balance, buy_date, initial_balance, qtd):
    mycursor = mydb.cursor()

    sql = "UPDATE current_account_applications SET balance = %s, initial_balance= %s, quantity= %s WHERE description= %s AND id= %s"

    val = (balance, initial_balance, qtd, stock_symbol, application_id)
    mycursor.execute(sql, val)

    mydb.commit()


def update_balance(current_account_id, application_id, balance, date=False):
    mycursor = mydb.cursor()
    sqlDate = ""

    if date:
        sqlDate = "and date='" + str(date) + "'"

    # return
    mycursor.execute("DELETE FROM balance where current_account_id=%s AND application_id=%s " + sqlDate,
                     (current_account_id, application_id))

    sql = "INSERT INTO balance (current_account_id, application_id, balance, date) VALUES (%s, %s, %s, %s)"
    val = (current_account_id, application_id, balance, datetime.datetime.today().strftime('%Y-%m-%d'))
    mycursor.execute(sql, val)

    mydb.commit()

    sql = "UPDATE current_account_applications SET balance = %s, updated_at=NOW() WHERE current_account_id= %s AND id= %s"
    val = (balance, current_account_id, application_id)
    mycursor.execute(sql, val)

    mydb.commit()

    print(mycursor.rowcount, "record(s) affected")


def update_stock_balance(ticker, quantity, balance, date=False):
    mycursor = mydb.cursor()
    sqlDate = ""

    individual_price = balance / quantity

    if date:
        sqlDate = "and date='" + str(date) + "'"

    mycursor.execute(
        "SELECT id, current_account_id, quantity FROM current_account_applications WHERE description=%s AND application_type_id=10",
        (ticker,))

    positions = mycursor.fetchall()

    for position in positions:
        application_id = position[0]
        current_account_id = position[1]
        qtd = position[2]

        # return
        mycursor.execute("DELETE FROM balance where current_account_id=%s AND application_id=%s " + sqlDate,
                         (current_account_id, application_id))

        sql = "INSERT INTO balance (current_account_id, application_id, balance, date) VALUES (%s, %s, %s, %s)"
        val = (
        current_account_id, application_id, individual_price * qtd, datetime.datetime.today().strftime('%Y-%m-%d'))
        mycursor.execute(sql, val)

    mydb.commit()

    sql = "UPDATE current_account_applications SET balance = %s * quantity, updated_at=NOW() WHERE description=%s " \
          "AND application_type_id=10"
    val = (individual_price, ticker)
    mycursor.execute(sql, val)

    mydb.commit()

    print(mycursor.rowcount, "record(s) affected")


def get_application_id(provider_id, application_type_id, description='', buy_date=None, account_id=None):
    mycursor = mydb.cursor()

    buy_date_sql = ""
    if buy_date:
        buy_date_sql = " AND (ca.buy_date BETWEEN DATE_SUB('" + buy_date + "', INTERVAL 3 DAY) AND " \
                                                                           "DATE_ADD('" + buy_date + "', INTERVAL 3 DAY) )"

    current_account_sql = ""
    if account_id:
        current_account_sql = " OR ca.id='" + str(account_id) + "' "

    mycursor.execute(
        "SELECT ca.current_account_id, ca.id, ca.description, cc.holder_name FROM current_account_applications ca"
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
            'holder_name': x[3],
        }


def clear_transactions(provider_id):
    mycursor = mydb.cursor()
    mycursor.execute("DELETE FROM movements WHERE provider_id=%s", (provider_id,))


def register_transaction(amount, from_account, to_account, date, description, movement_type_id, provider_id):
    mycursor = mydb.cursor()

    if amount > 0:
        in_out = 1
    else:
        in_out = -1
        amount *= -1

    sql = "INSERT INTO movements (amount, from_account_id, to_account_id, date, description, in_out, movement_type_id, provider_id) " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (amount, from_account, to_account, date, description, in_out, movement_type_id, provider_id)
    mycursor.execute(sql, val)

    mydb.commit()


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


def get_application_id_by_amount(amount, application_type):
    mycursor = mydb.cursor()

    mycursor.execute("SELECT caa.id FROM current_account_applications caa "
                     "WHERE floor(caa.initial_balance)=floor(%s) AND caa.application_type_id=%s",
                     (amount, application_type))

    myresult = mycursor.fetchall()

    if myresult:
        return myresult[0][0]
    else:
        return None


def search_bank_by_number(number):
    mycursor = mydb.cursor()

    number = number.replace("*", "%")
    number = number.replace("Conta ", "")

    sql = "SELECT provider_id FROM current_accounts WHERE guiabolso_alias LIKE '" + number + "'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()

    if myresult:
        return myresult[0][0]
    else:
        return None


def fix_movements():
    mycursor = mydb.cursor()

    sql = "SELECT date, from_account_id, to_account_id, amount, in_out, id FROM movements WHERE (to_account_id IS NULL OR from_account_id IS NULL) AND active=1"

    mycursor.execute(sql)
    myresult = mycursor.fetchall()

    if myresult:
        for item in myresult:
            to_account_id1 = item[2]
            from_account_id1 = item[1]
            date = item[0]
            amount = item[3]
            in_out1 = item[4]
            id1 = item[5]

            in_out2 = in_out1 * -1

            sql = "SELECT id, to_account_id, from_account_id FROM movements WHERE amount=%s AND in_out=%s and date=%s AND id!=%s"

            mycursor.execute(sql, (amount, in_out2, date, id1))
            match = mycursor.fetchall()

            if match:
                id2 = match[0][0]
                to_account_id2 = match[0][1]
                from_account_id2 = match[0][2]

                sql = "UPDATE movements SET active=0 WHERE in_out=-1 and ID IN (" + str(id1) + ", " + str(id2) + ")"
                mycursor.execute(sql)
                mydb.commit()

                if in_out1 == 1:
                    from_account_id = from_account_id2
                    to_account_id = to_account_id1
                elif in_out2 == 1:
                    from_account_id = from_account_id1
                    to_account_id = to_account_id2

                sql = "UPDATE movements SET from_account_id=%s, to_account_id=%s WHERE id in (" + str(id1) + ", " + str(
                    id2) + ")"
                mycursor.execute(sql, (from_account_id, to_account_id))
                mydb.commit()

    else:
        return None
