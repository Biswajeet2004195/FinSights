import sys
from config import verify_password, hash_password
import json

with open('../users.json', 'r') as f:
    users = json.load(f)

# The user is probably typing some password, but we don't know it.
# Let's generate a new one.
h = hash_password('TestPassword123')
print("New hash:", h)
v = verify_password(h, 'TestPassword123')
print("Verification:", v)

# wait, could the problem be the way bcrypt handles hashes?
# Or maybe the problem is that email is not found?
