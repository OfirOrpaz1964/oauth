from flask import Flask, request, redirect
import requests
import base64
import logging
import os

app = Flask(__name__)

# Set your actual Google OAuth credentials and redirect URI here
CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID"
CLIENT_SECRET = "YOUR_GOOGLE_CLIENT_SECRET"
REDIRECT_URI = "https://your-render-app.onrender.com/callback"

# Set up logging
logging.basicConfig(filename='redirector.log', level=logging.INFO, format='%(asctime)s %(message)s')

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
        logging.info(f"[REDIRECT] Decoded and redirecting to: {decoded_url}")
        return redirect(decoded_url)
    except Exception as e:
        logging.error(f"[ERROR] Base64 decode failed: {e}")
        return f"Invalid base64 input: {e}", 400

@app.route('/callback')
def callback():
    code = request.args.get("code")
    if not code:
        return "Missing code", 400

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
        token_data = response.json()
        logging.info(f"[TOKEN] Received: {token_data}")
        return f"<h3>Token received:</h3><pre>{token_data}</pre>"
    except Exception as e:
        logging.error(f"[ERROR] Token exchange failed: {e}")
        return f"Token exchange error: {e}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
