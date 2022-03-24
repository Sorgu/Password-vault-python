import mysql.connector

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Password123",
        database="main"
    )
except:
    pass

def mydbfunc(db):
    my_db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Password123",
        database=db
    )
    return my_db
def nodbfunc():
    my_db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Password123"
    )
    return my_db
