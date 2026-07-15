import json
from config import hash_password, _sv_users, _ld_users

users = _ld_users()
if "xyz@gmail.com" in users:
    users["xyz@gmail.com"]["password"] = hash_password("Password123")
    _sv_users(users)
    print("Fixed xyz@gmail.com password to 'Password123'")
