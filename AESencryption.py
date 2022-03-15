from Crypto.Cipher import AES

# Function to encrypt input data with an inputted key using AES.
def encryption(key, data):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data.encode("ascii"))
    return ciphertext, tag, nonce

# Function to decrypt input data with an inputted key, tag, and nonce
def decryption(key, ciphertext, tag, nonce):
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    # Uses tag to check if data is the same as before encryption or not
    try:
        cipher.verify(tag)
        return plaintext.decode("ascii")
    except ValueError:
        pass

