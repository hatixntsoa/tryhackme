import hashlib

username = input("Username : ")
date = "1403"
password = username + date

md5_hash = hashlib.md5(password.encode()).hexdigest()
print("Your initial password is:", md5_hash)
