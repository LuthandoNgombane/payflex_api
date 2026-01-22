#LN Import the library that allows us to send messages to other websites or APIs
import requests
#LN Import the necessary tools from Flask to build our web server and handle data
from flask import Flask, request, jsonify

#LN Create the main application object for our web server
app = Flask(__name__)

# Payflex Configuration (Sandbox/Dev defaults)
# Note: Real Payflex URLs vary based on integration type (Direct vs Peach Payments)
# This mimics the direct "BNPL" API flow found in their developer docs.

#LN Store the web address where we send our username and password to log in
PAYFLEX_AUTH_URL = "https://payflex.eu.auth0.com/oauth/token" 
#LN Store the main web address for the Payflex services we want to use
PAYFLEX_API_BASE = "https://api.payflex.co.za/v1" # Example Base URL
#LN Store the unique ID that identifies our specific application to Payflex
CLIENT_ID = "your_payflex_client_id"
#LN Store the secret password that proves our application's identity
CLIENT_SECRET = "your_payflex_client_secret"
#LN Define which specific Payflex service we are asking permission to access
AUDIENCE = "https://api.payflex.co.za/"

#LN Define a helper function to handle the login process with Payflex
def get_payflex_token():
    """Authenticates with Payflex and retrieves a Bearer token."""
    #LN Create a bundle of information (dictionary) containing our login credentials
    payload = {
        #LN Add our unique Client ID to the bundle
        "client_id": CLIENT_ID,
        #LN Add our secret password to the bundle
        "client_secret": CLIENT_SECRET,
        #LN Specify the service we want to talk to
        "audience": AUDIENCE,
        #LN Tell them we are using standard client credentials to log in
        "grant_type": "client_credentials"
    }
    
    #LN Send our login bundle to the Payflex authentication URL
    response = requests.post(PAYFLEX_AUTH_URL, json=payload)
    
    #LN Check if the server replied with a "Success" code (200)
    if response.status_code == 200:
        #LN If successful, pick out the 'access_token' from the reply and return it
        return response.json().get("access_token")
    #LN If the login failed, return nothing
    return None

#LN Tell our server to run the function below when someone sends a POST message to this address
@app.route('/create-payflex-checkout', methods=['POST'])
#LN Define the function that sets up a new purchase/checkout
def create_checkout():
    #LN Grab the data (like price and email) sent by the user in their message
    data = request.json
    #LN Look inside that data and pull out the 'amount' value
    amount = data.get('amount')
    #LN Look inside that data and pull out the 'email' value
    customer_email = data.get('email')

    # 1. Get Auth Token
    #LN Call our helper function to get the security pass (token) we need
    token = get_payflex_token()
    #LN Check if we failed to get a token (if it is empty or None)
    if not token:
        #LN Send an error message back to the user saying authentication failed
        return jsonify({"error": "Failed to authenticate with Payflex"}), 500

    # 2. Create Checkout Session
    # This endpoint creates the transaction and gets a URL for the user to complete payment
    
    #LN Prepare the settings (headers) for our next message to Payflex
    headers = {
        #LN Attach our security token so Payflex knows we are allowed to do this
        "Authorization": f"Bearer {token}",
        #LN Tell Payflex we are sending the data in JSON format
        "Content-Type": "application/json"
    }
    
    #LN Create the main bundle of information describing the purchase order
    checkout_payload = {
        #LN Set the cost of the item
        "amount": amount,
        #LN Set the currency to South African Rand
        "currency": "ZAR",
        #LN Create a reference number for this order (you would usually generate this)
        "merchantReference": "ORDER-001",
        #LN Create a sub-section with details about the customer
        "customer": {
            #LN Add the customer's email address
            "email": customer_email,
            #LN Add the customer's first name
            "firstName": "Luthando", # Dynamic in real app
            #LN Add the customer's last name
            "surname": "Demo"
        },
        #LN Create a sub-section telling Payflex where to send the user after payment
        "redirect": {
            #LN The URL to go to if the payment succeeds
            "returnUrl": "http://localhost:5000/success",
            #LN The URL to go to if the user cancels
            "cancelUrl": "http://localhost:5000/cancel"
        }
    }

    # Mocking the call to Payflex API (replace with real endpoint)
    # response = requests.post(f"{PAYFLEX_API_BASE}/checkout", json=checkout_payload, headers=headers)
    
    # SIMULATION RESPONSE (Since we don't have real credentials)
    # In a real scenario, you return response.json()['redirectUrl']
    
    #LN Create a fake response that looks like what Payflex would send back
    simulated_response = {
        #LN mimic a status saying the order was created
        "status": "created",
        #LN mimic a unique ID for this transaction
        "payflex_id": "PF-123456789",
        #LN mimic the link the user needs to click to pay
        "redirect_url": "https://checkout.payflex.co.za/secure/123456789"
    }
    
    #LN Convert our fake response to JSON format and send it back to the user
    return jsonify(simulated_response)

#LN Check if this script is being run directly (not imported by another file)
if __name__ == '__main__':
    #LN Start the web server on port 5000 and show detailed error messages if it crashes
    app.run(port=5000, debug=True)