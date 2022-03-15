from connectDB import mydbfunc
import SaltHash
import AESencryption


# Function to check if email and password are valid
def validatemasterpassword(email, masterpassword):
    from connectDB import mydb
    mycursor = mydb.cursor()
    mycursor.execute("SELECT userid FROM usertable WHERE email = %s", (email,))
    try:
        userid = str(mycursor.fetchone()[0])
    except TypeError:
        print("Invalid email")
        return
    except:
        print("Unknown failure")
        return
    # redefines mydb and mycursor to access the database for the associated email
    mydb = mydbfunc(userid)
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("SELECT salt FROM masterpasswordt")
    salt = str(mycursor.fetchone()[0])
    hashedmasterpassword = SaltHash.hash(masterpassword + salt)
    hashedmasterpassword = hashedmasterpassword.hex()
    mycursor.execute("SELECT masterpassword FROM masterpasswordt")
    retrivedmasterpassword = str(mycursor.fetchone()[0])
    if retrivedmasterpassword == hashedmasterpassword:
        return userid
    else:
        return False


# Function to encrypt and store passwords into the database along with description and username
def storeMysql(userid, masterpassword, description, username, password):
    mydb = mydbfunc(userid)
    mycursor = mydb.cursor(buffered=True)

    """ A salt is generated to be combined with the masterpassword to generate a hash that will be used as
        the key to encrypt and decrypt the password using AES
    """
    salt = SaltHash.saltgen()
    key = SaltHash.hash(masterpassword + salt)
    # Key is used to encrypt the password.
    encryptedpassword, tag, nonce = AESencryption.encryption(key, password)
    # .hex is used to convert the encryption variables in order to be able to get stored in the database.
    encryptedpassword = encryptedpassword.hex()
    tag = tag.hex()
    nonce = nonce.hex()
    # Try except function in case the description is already in the database
    try:
        # Attempts to find the ID of description provided
        mycursor.execute("SELECT descriptionID FROM descriptionsT WHERE descriptions = %s", (description,))
        # Inserting variables with %s prevents injection.
        records = mycursor.fetchone()
        if not records:
            raise
    except:
        # Inserts description into database if it does not exist already
        mycursor.execute("INSERT INTO descriptionsT (descriptions) VALUES (%s)", (description,))

    # Inserts username, encrypted password, and descriptionID into database
    mycursor.execute("INSERT INTO logindetailsT (usernames, passwords, descriptionID) VALUES (%s, %s, "
                     "(SELECT descriptionID FROM descriptionsT WHERE %s = descriptions))",
                     (username, encryptedpassword,
                      description))

    # Inserts all encryption data for the password into database
    mycursor.execute(
        "INSERT INTO passwordsecretsT (logindetailsID, tag, nonce, salt) VALUES ((SELECT logindetailsID FROM "
        "logindetailsT WHERE %s = passwords), %s, %s, %s)", (encryptedpassword, tag, nonce, salt))
    mydb.commit()


# Function to take a userid and return every description and username belonging to the userid
def get_descriptions_and_usernames(userid):
    mydb = mydbfunc(userid)
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("select logindetailst.usernames, descriptionst.descriptions FROM logindetailst LEFT JOIN "
                     "descriptionst ON logindetailst.descriptionID = descriptionst.descriptionID")
    temp_descriptions_and_usernames = mycursor.fetchall()

    # List reversal to change the order they appear in GUI
    descriptions_and_usernames = []
    for i in temp_descriptions_and_usernames:
        inside_descriptions_and_usernames = ()
        for each in reversed(i):
            inside_descriptions_and_usernames = inside_descriptions_and_usernames + (each,)
        descriptions_and_usernames.append(inside_descriptions_and_usernames)

    return descriptions_and_usernames


# Function to retrieve password from the database and decrypt it
def fetchMysql(userid, masterpassword, description_username):
    mydb = mydbfunc(userid)
    mycursor = mydb.cursor(buffered=True)

    description = str(description_username[0])
    username = str(description_username[1])
    mycursor.execute("SELECT logindetailsID FROM logindetailst WHERE descriptionID = (SELECT descriptionID FROM "
                     "descriptionst WHERE descriptions = %s) AND usernames = %s", (description, username))
    logindetailsID = str(mycursor.fetchone()[0])

    # Pulls all required information from tables into variables
    mycursor.execute("SELECT usernames, passwords FROM logindetailst WHERE logindetailsID = %s", (logindetailsID,))
    username, password = mycursor.fetchall()[0]
    mycursor.execute("SELECT tag, nonce, salt FROM passwordsecretst WHERE logindetailsID = %s", (logindetailsID,))
    tag, nonce, salt = mycursor.fetchall()[0]

    # Reverts transformation done before storing the information
    password = bytes.fromhex(password)
    tag = bytes.fromhex(tag)
    nonce = bytes.fromhex(nonce)

    # Recreate key used for the encryption by combining master key with stored salt
    key = SaltHash.hash(masterpassword + salt)
    plaintextpassword = AESencryption.decryption(key, password, tag, nonce)
    return plaintextpassword


# Function to search for either a username or description
def searchMysql(userid, searchterm):
    mydb = mydbfunc(userid)
    mycursor = mydb.cursor(buffered=True)

    mycursor.execute("SELECT descriptionst.descriptions, logindetailst.usernames FROM descriptionst JOIN "
                     "logindetailst ON descriptionst.descriptionID = logindetailst.descriptionID")
    descriptions_and_usernames = mycursor.fetchall()
    searchresults = []

    # function to return true if "searchterm" is inside of "info"
    def filter_search(info):
        if info.lower().find(searchterm.lower()) > -1:
            return True
        else:
            return False
    for each in descriptions_and_usernames:
        description, username = each
        # uses "or" to avoid duplicate entries when searchterm fits both username and description
        if filter_search(description) or filter_search(username):
            searchresults.append(each)
    if searchresults:
        return searchresults
    else:
        pass


def appendMysql(userid, masterpassword, logindetailsID, sub_func, new_description="", new_username="",
                new_password=""):

    def description_func(new_description):
        mydb = mydbfunc(userid)
        mycursor = mydb.cursor(buffered=True)
        try:
            mycursor.execute("UPDATE logindetailst SET descriptionID = (SELECT descriptionID FROM descriptionst WHERE "
                             "descriptions = %s) WHERE logindetailsID = %s", (new_description, logindetailsID))
        except:
            mycursor.execute("INSERT INTO descriptionst (descriptions) VALUES (%s)", (new_description,))
            mycursor.execute(
                "UPDATE logindetailst SET descriptionID = (SELECT descriptionID FROM descriptionst WHERE "
                "descriptions = %s) WHERE logindetailsID = %s", (new_description, logindetailsID))
        mydb.commit()

    def username_func(new_username):
        mydb = mydbfunc(userid)
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute("UPDATE logindetailst SET usernames = %s WHERE logindetailsID = %s",
                         (new_username, logindetailsID))
        mydb.commit()

    def password_func(new_password):
        mydb = mydbfunc(userid)
        mycursor = mydb.cursor(buffered=True)
        salt = SaltHash.saltgen()
        key = SaltHash.hash(masterpassword + salt)
        # Key is used to encrypt the password.
        encryptedpassword, tag, nonce = AESencryption.encryption(key, new_password)
        # .hex is used to convert the encryption variables in order to be able to get stored in the database.
        encryptedpassword = encryptedpassword.hex()
        tag = tag.hex()
        nonce = nonce.hex()
        mycursor.execute("UPDATE logindetailst SET passwords = %s WHERE logindetailsID = %s",
                         (encryptedpassword, logindetailsID))
        mycursor.execute("UPDATE passwordsecretst SET salt = %s, tag = %s, nonce = %s WHERE logindetailsID = %s",
                         (salt, tag, nonce, logindetailsID))
        mydb.commit()

    if sub_func == 1:
        description_func(new_description)
    elif sub_func == 2:
        username_func(new_username)
    elif sub_func == 3:
        password_func(new_password)

def deleteMysql(userid, description_and_username):
    mydb = mydbfunc(userid)
    mycursor = mydb.cursor(buffered=True)
    description, username = description_and_username
    mycursor.execute("SELECT logindetailsID FROM logindetailst WHERE usernames = %s AND descriptionID = (SELECT "
                     "descriptionID FROM descriptionst WHERE descriptions = %s)", (username, description))
    logindetailsID = str(mycursor.fetchone()[0])
    mycursor.execute("DELETE FROM passwordsecretst WHERE logindetailsID = %s", (logindetailsID,))
    mycursor.execute("DELETE FROM logindetailst WHERE logindetailsID = %s", (logindetailsID,))
    mycursor.execute("SELECT descriptionID FROM descriptionst WHERE descriptions = %s", (description,))
    descriptionID = str(mycursor.fetchone()[0])
    mycursor.execute("SELECT * FROM logindetailst WHERE descriptionID = %s", (descriptionID,))
    if not mycursor.fetchall():
        mycursor.execute("DELETE FROM descriptionst WHERE descriptionID = %s", (descriptionID,))
    mydb.commit()

