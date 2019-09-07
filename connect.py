import mysql.connector

db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "root",
    database = "srm-brain"
)

cursor = db.cursor()
