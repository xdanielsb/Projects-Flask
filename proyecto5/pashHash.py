from __future__ import print_function
from passlib.hash import sha256_crypt

password1= sha256_crypt.encrypt("password")
password2= sha256_crypt.encrypt("password")

print(password1)
print(password2)

##Verify
print(sha256_crypt.verify("password", password1))
print(sha256_crypt.verify("password", password2))
print(len(password1))
