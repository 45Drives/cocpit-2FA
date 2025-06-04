import sys
import json
import pyotp

if len(sys.argv) != 3:
    print(json.dumps({"status": "error", "message": "Usage: verify.py <code> <secret>"}))
    sys.exit(1)

user_code = sys.argv[1]
secret = sys.argv[2]

totp = pyotp.TOTP(secret)

if totp.verify(user_code):
    print(json.dumps({"status": "valid"}))
else:
    print(json.dumps({"status": "invalid"}))
