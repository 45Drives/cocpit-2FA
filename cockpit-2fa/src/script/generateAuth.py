
import pexpect
import re
import json

def run():
    child = pexpect.spawn("google-authenticator", encoding='utf-8')
    output_lines = []

    child.logfile_read = None

    try:
        child.expect("Do you want authentication tokens to be time-based.*\\?")
        child.sendline("y")

        child.expect("Do you want me to update your .* file.*\\?")
        child.sendline("y")

        child.expect("Do you want to disallow multiple uses.*\\?")
        child.sendline("y")

        child.expect("Do you want to enable rate-limiting.*\\?")
        child.sendline("y")

        child.expect(pexpect.EOF, timeout=10)
        output = child.before
        output_lines = output.splitlines()

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "output": output_lines})

    # Extract QR code URL
    qr_url = next((line for line in output_lines if "https://www.google.com/chart?" in line), None)

    # Extract otpauth URI (from `chl=` param inside the QR URL)
    otp_uri = None
    if qr_url:
        match = re.search(r"chl=([^&\s]+)", qr_url)
        if match:
            otp_uri = match.group(1)

    # Extract scratch codes (8-digit numbers)
    scratch_codes = [line.strip() for line in output_lines if re.match(r"^\d{8}$", line.strip())]

    return json.dumps({
        "success": True,
        "qr_url": qr_url,
        "otp_uri": otp_uri,
        "scratch_codes": scratch_codes
    })

if __name__ == "__main__":
    print(run())
