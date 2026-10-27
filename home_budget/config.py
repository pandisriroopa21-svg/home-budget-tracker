import mysql.connector
def connect():
    mydb = mysql.connector.connect(
        host  = "local host",
        user = "root",
        password = "",
        database = ""
    )
    return mydb
