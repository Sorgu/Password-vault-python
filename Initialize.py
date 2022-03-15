import connectDB

mydb = connectDB.nodbfunc()
mycursor = mydb.cursor(buffered=True)
# Creates the table that manages user emails and userid
try:
    mycursor.execute("CREATE DATABASE main")
    mydb = connectDB.mydbfunc("main")
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("CREATE TABLE usertable (id int auto_increment PRIMARY KEY NOT NULL, "
                     "userid int NOT NULL UNIQUE, email varchar(255) NOT NULL UNIQUE)")
    mydb.commit()
except Exception as e:
    print("Already initialized", e)
