import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Payflex Configuration (Sandbox/Dev defaults)
# Note: Real Payflex URLs vary based on integration type (Direct vs Peach Payments)
# This mimics the direct "BNPL" API flow found in their developer docs.
PAYFLEX_AUTH_URL = "https://payflex.eu.auth0.com/oauth/token" 
PAYFLEX_API_BASE = "https://api.payflex.co.za/v1" # Example Base URL
CLIENT_ID = "your_payflex_client_id"
CLIENT_SECRET = "your_payflex_client_secret"
AUDIENCE = "https://api.payflex.co.za/"

def get_payflex_token():
    """Authenticates with Payflex and retrieves a Bearer token."""
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "audience": AUDIENCE,
        "grant_type": "client_credentials"
    }
    
    response = requests.post(PAYFLEX_AUTH_URL, json=payload)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

@app.route('/create-payflex-checkout', methods=['POST'])
def create_checkout():
    data = request.json
    amount = data.get('amount')
    customer_email = data.get('email')

    # 1. Get Auth Token
    token = get_payflex_token()
    if not token:
        return jsonify({"error": "Failed to authenticate with Payflex"}), 500

    # 2. Create Checkout Session
    # This endpoint creates the transaction and gets a URL for the user to complete payment
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    checkout_payload = {
        "amount": amount,
        "currency": "ZAR",
        "merchantReference": "ORDER-001",
        "customer": {
            "email": customer_email,
            "firstName": "Luthando", # Dynamic in real app
            "surname": "Demo"
        },
        "redirect": {
            "returnUrl": "http://localhost:5000/success",
            "cancelUrl": "http://localhost:5000/cancel"
        }
    }

    # Mocking the call to Payflex API (replace with real endpoint)
    # response = requests.post(f"{PAYFLEX_API_BASE}/checkout", json=checkout_payload, headers=headers)
    
    # SIMULATION RESPONSE (Since we don't have real credentials)
    # In a real scenario, you return response.json()['redirectUrl']
    simulated_response = {
        "status": "created",
        "payflex_id": "PF-123456789",
        "redirect_url": "https://checkout.payflex.co.za/secure/123456789"
    }
    
    return jsonify(simulated_response)

if __name__ == '__main__':
    app.run(port=5000, debug=True)