import os, hashlib, hmac
from config import verify_password

password = "TestPassword123"
salt = os.urandom(16)
hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
pwd_str = f"pbkdf2:${salt.hex()}:${hashed.hex()}"
print("PBKDF2 hash:", pwd_str)

v = verify_password(pwd_str, password)
print("Verification:", v)
