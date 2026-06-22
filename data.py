import requests
from datetime import datetime, timedelta

TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"

CLIENT_ID = "-"
CLIENT_SECRET = "-"

TOKEN_REFRESH_MARGIN = 30


class TokenManager:
    def __init__(self):
        self.token = None
        self.expires_at = None

    def get_token(self):
        """Return a valid access token, refreshing automatically if needed."""
        if self.token and self.expires_at and datetime.now() < self.expires_at:
            return self.token
        return self._refresh()

    def _refresh(self):
        """Fetch a new access token from the OpenSky authentication server."""
        r = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
        )
        r.raise_for_status()

        data = r.json()
        self.token = data["access_token"]
        expires_in = data.get("expires_in", 1800)
        self.expires_at = datetime.now() + timedelta(seconds=expires_in - TOKEN_REFRESH_MARGIN)
        return self.token

    def headers(self):
        """Return request headers with a valid Bearer token."""
        return {"Authorization": f"Bearer {self.get_token()}"}


# Create a single shared instance for your script.
tokens = TokenManager()

location_params = {
    "lamin": 44.158776,  # Southernmost latitude
    "lamax": 44.777171,  # Northernmost latitude
    "lomin": 25.335175,  # Westernmost longitude
    "lomax": 26.782624,  # Easternmost longitude
}

# Use it for any API call - the token is refreshed automatically.
while 1:
    response = requests.get(
        "https://opensky-network.org/api/states/all",
        headers=tokens.headers(),
        params = location_params
    )
    if response.status_code == 200:
        data = response.json()
        states = data.get("states", [])
        
        for i in states:
            callsign = i[1].strip() if i[1] else "UNKNOWN"
            country = i[2],
            altitude = i[7],
            velocity = i[9],
            
            print(f"Flight: {callsign:<8} | Country: {country:} | Alt: {altitude}m | Speed: {velocity} m/s")
            print("!-----------------------------------------------!")
    else:
            print(f"Error fetching data: {response.status_code}")