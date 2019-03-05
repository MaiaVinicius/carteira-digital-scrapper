import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv(verbose=True)

mydb = mysql.connector.connect(
  host=os.getenv("DB_HOST"),
  user=os.getenv("DB_USER"),
  db=os.getenv("DB_DATABASE"),
  passwd=os.getenv("DB_PWD")
)

