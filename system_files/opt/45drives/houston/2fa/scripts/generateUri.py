# generate_auth_data.py
import pyotp
import json
import getpass
import socket

# Get current user and hostname
username = getpass.getuser()
hostname = socket.gethostname()

# Generate TOTP secret and URI
secret = pyotp.random_base32()
uri = pyotp.totp.TOTP(secret).provisioning_uri(
    name=f"{username}@{hostname}"  # or "houston", if you prefer fixed branding
)

# Output JSON
print(json.dumps({
    "secret": secret,
    "otpauth_uri": uri,
    "account": f"{username}@{hostname}",
    "issuer": hostname
}))
