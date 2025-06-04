import sys
import os
import random
import json

def generate_scratch_codes(count=5):
    return [str(random.randint(10000000, 99999999)) for _ in range(count)]

if len(sys.argv) != 2:
    print(json.dumps({"status": "error", "message": "Usage: python3 write_google_auth_file.py <secret>"}))
    sys.exit(1)

secret = sys.argv[1].strip()
file_path = os.path.expanduser("~/.google_authenticator")

try:
    scratch_codes = generate_scratch_codes()

    with open(file_path, "w") as f:
        f.write(secret + "\n")
        f.write('" RATE_LIMIT 3 30\n')
        f.write('" WINDOW_SIZE 17\n')
        f.write('" DISALLOW_REUSE\n')
        f.write('" TOTP_AUTH\n')
        for code in scratch_codes:
            f.write(code + "\n")

    os.chmod(file_path, 0o600)

    # ✅ Output JSON that Vue can parse
    print(json.dumps({
        "status": "success",
        "message": ".google_authenticator written",
        "scratch_codes": scratch_codes
    }))

except Exception as e:
    print(json.dumps({
        "status": "error",
        "message": str(e)
    }))
    sys.exit(1)
