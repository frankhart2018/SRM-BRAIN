import mysql.connector

db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "root",
    database = "srmbrain"
)

cursor = db.cursor()
