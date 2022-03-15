import secrets
import hashlib
import string


# Function that generates a pseudo random 64 character long string to be used for salting passwords
def saltgen():
    salt_string = ""
    for each in range(64):
        salt_string += secrets.SystemRandom().choice(string.ascii_letters + string.digits)
    return salt_string


# Function that generates a sha256 hash from the input
def hash(input):
    encoded_input = str.encode(input)
    output = hashlib.sha256(encoded_input)
    return output.digest()
