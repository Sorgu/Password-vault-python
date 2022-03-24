from connectDB import mydbfunc
import SaltHash

def newuser(masterpassword, email):
    from connectDB import mydb
    mycursor = mydb.cursor(buffered=True)

    mycursor.execute("SHOW databases")
    showdb = mycursor.fetchall()
    dbi = 0
    flag = False

    while True:
        dbicheck = "`" + str(dbi) + "`"
        for each in showdb:
            for each1 in each:
                try:
                    each1 = int(each1)
                    if dbi == each1:
                        flag = True
                except:
                    pass
        if flag:
            dbi += 1
            flag = False
        else:
            sqlquery = "CREATE DATABASE {}"
            mycursor.execute(sqlquery.format(dbicheck))
            sqlquery2 = "INSERT INTO usertable (userid, email) VALUES ({}, %s)"
            mycursor.execute(sqlquery2.format(dbi), (email,))
            mydb.commit()
            userid = str(dbi)
            break
    # connect to new database
    mydb = mydbfunc(str(dbi))
    mycursor = mydb.cursor(buffered=True)
    salt = SaltHash.saltgen()
    masterpassword = SaltHash.hash(masterpassword + salt)
    masterpassword = masterpassword.hex()
    try:
        mycursor.execute("CREATE TABLE descriptionsT (descriptionID int auto_increment "
                         "PRIMARY KEY NOT NULL, descriptions varchar(255) NOT NULL, UNIQUE (descriptions)) ")
        mycursor.execute("CREATE TABLE logindetailsT (logindetailsID int auto_increment PRIMARY KEY NOT NULL, "
                         "usernames varchar(255) NOT NULL, passwords varchar(255) NOT NULL, "
                         "descriptionID int NOT NULL, FOREIGN KEY (descriptionID) "
                         "REFERENCES descriptionsT(descriptionID))")
        mycursor.execute("CREATE TABLE masterpasswordT (masterpassword varchar(255) PRIMARY KEY NOT NULL, "
                         "salt varchar(255) NOT NULL)")
        mycursor.execute("CREATE TABLE passwordsecretsT (passwordsecretsID int auto_increment PRIMARY KEY "
                         "NOT NULL, logindetailsID int NOT NULL, tag varchar(255) NOT NULL, "
                         "nonce varchar(255) NOT NULL, salt varchar(255) NOT NULL, "
                         "FOREIGN KEY (logindetailsID) REFERENCES logindetailsT(logindetailsID))")
        mycursor.execute("INSERT INTO masterpasswordT VALUES(%s, %s)", (masterpassword, salt))
    except Exception as e:
        print(e)
    mydb.commit()

    return userid
