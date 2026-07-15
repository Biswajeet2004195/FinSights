import hashlib
import hmac

def verify_pbkdf2(stored_password_hash, input_password):
    parts = stored_password_hash.split('$')
    print("Parts:", parts)
    salt = bytes.fromhex(parts[1])
    expected = bytes.fromhex(parts[2])
    hashed = hashlib.pbkdf2_hmac('sha256', input_password.encode('utf-8'), salt, 100000)
    return hmac.compare_digest(expected, hashed)

pwd_str = "pbkdf2:$5c4efaa65f317b9e8aef0a0de911c05c:$edb388ac7d8019c4230866901e4f66c54ca3572bc5f298b34f2657ce7a4b2607"
try:
    verify_pbkdf2(pwd_str, "test")
except Exception as e:
    print("Error:", e)
