import requests
import time
import json
from datetime import datetime, timezone
from collections import defaultdict

KEYCLOAK_URL = "http://localhost:8080"
REALM = "Fortress-SOC"
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"
LOG_FILE = "/var/log/keycloak_anomaly.log"

RAPID_LOGIN_WINDOW_SECONDS = 300
RAPID_LOGIN_THRESHOLD = 3
OFFHOURS_START_HOUR = 0
OFFHOURS_END_HOUR = 5

user_login_history = defaultdict(list)
seen_event_ids = set()

def get_admin_token():
    resp = requests.post(
        f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token",
        data={
            "client_id": "admin-cli",
            "username": ADMIN_USER,
            "password": ADMIN_PASS,
            "grant_type": "password",
        },
    )
    return resp.json().get("access_token")

def fetch_login_events(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM}/events?type=LOGIN&max=50",
        headers=headers,
    )
    if resp.status_code == 200:
        return resp.json()
    return []

def write_alert(message, severity):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "severity": severity,
        "source": "keycloak-anomaly-detector",
        "message": message,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[{severity}] {message}")

def analyze_event(event):
    event_id = str(event.get("time", "")) + str(event.get("userId", ""))
    if event_id in seen_event_ids:
        return
    seen_event_ids.add(event_id)

    username = event.get("details", {}).get("username", event.get("userId", "unknown"))
    event_time = event.get("time", 0) / 1000
    event_dt = datetime.fromtimestamp(event_time, tz=timezone.utc)

    write_alert(f"Login event: user={username} at {event_dt.isoformat()}", "INFO")

    if OFFHOURS_START_HOUR <= event_dt.hour < OFFHOURS_END_HOUR:
        write_alert(
            f"ANOMALY: Off-hours login detected for user={username} at {event_dt.isoformat()}",
            "HIGH",
        )

    user_login_history[username].append(event_time)
    recent = [t for t in user_login_history[username] if event_time - t <= RAPID_LOGIN_WINDOW_SECONDS]
    user_login_history[username] = recent

    if len(recent) >= RAPID_LOGIN_THRESHOLD:
        write_alert(
            f"ANOMALY: Rapid repeat logins for user={username} — {len(recent)} logins within "
            f"{RAPID_LOGIN_WINDOW_SECONDS}s window. Possible session abuse or credential sharing.",
            "HIGH",
        )

def main():
    print("Starting Keycloak login anomaly detector...")
    while True:
        try:
            token = get_admin_token()
            events = fetch_login_events(token)
            for event in events:
                analyze_event(event)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(10)

if __name__ == "__main__":
    main()
