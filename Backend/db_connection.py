import mysql.connector
def connect():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="aiml-b3",
        database="home_budget"
    )
    return mydb
