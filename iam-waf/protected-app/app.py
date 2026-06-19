from flask import Flask, redirect, request, session, url_for
import requests
import os

app = Flask(__name__)
app.secret_key = "sentrix-secret-key"

KEYCLOAK_URL = "http://192.168.50.50:8080"
REALM = "sentrix-soc"
CLIENT_ID = "sentrix-app"
CLIENT_SECRET = "PASTE_YOUR_SECRET_HERE"
REDIRECT_URI = "http://localhost:5000/callback"

@app.route("/")
def home():
    if "user" in session:
        return f"<h2>Welcome {session['user']}</h2><p>Roles: {session['roles']}</p><a href='/logout'>Logout</a>"
    return "<a href='/login'>Login with Keycloak</a>"

@app.route("/login")
def login():
    auth_url = (
        f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/auth"
        f"?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"
    )
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    token_response = requests.post(token_url, data=data).json()
    access_token = token_response.get("access_token")

    import jwt
    decoded = jwt.decode(access_token, options={"verify_signature": False})
    session["user"] = decoded.get("preferred_username")
    session["roles"] = decoded.get("realm_access", {}).get("roles", [])
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
