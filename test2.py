import sys
import json
import traceback
from config import verify_password

def test():
    try:
        with open('d:/infosys/users.json', 'r') as f:
            users = json.load(f)
            
        print("Users:", users.keys())
        
        # Test the biswa user
        user = users.get('biswa@gmail.com')
        if not user:
            print("biswa not found")
            return
            
        pwd = user['password']
        print(f"Stored hash: {pwd}")
        
        # Let's try some passwords if we don't know it, or just print the verify logic
        print("Prefix check pbkdf2:$:", pwd.startswith('pbkdf2:$'))
        
        import hashlib, hmac
        parts = pwd.split('$')
        print("Parts length:", len(parts))
        if len(parts) >= 3:
            salt = bytes.fromhex(parts[1])
            expected = bytes.fromhex(parts[2])
            print("Salt and expected extracted successfully")
        
    except Exception as e:
        print("Error:")
        traceback.print_exc()

test()
