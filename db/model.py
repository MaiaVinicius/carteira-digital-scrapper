import datetime

from db import connection

mydb = connection.mydb


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


def get_application_id(provider_id, application_type_id, description=''):
    mycursor = mydb.cursor()

    mycursor.execute("SELECT ca.current_account_id, ca.id, ca.description FROM current_account_applications ca"
                     " LEFT JOIN current_accounts cc ON cc.id=ca.current_account_id "
                     "WHERE cc.provider_id=%s AND ca.application_type_id=%s AND (%s LIKE concat(ca.description, '%') OR %s='') "
                     "LIMIT 1",
                     (provider_id, application_type_id, description, description))

    myresult = mycursor.fetchall()

    for x in myresult:
        return {
            'current_account_id': x[0],
            'application_id': x[1],
            'description': x[2],
        }
