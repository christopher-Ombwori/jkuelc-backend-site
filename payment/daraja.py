"""
Daraja API Integration for M-Pesa payments.
This module handles all interactions with the Safaricom Daraja API for the JKUELC application.
"""
import base64
import json
import logging
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from django.conf import settings

logger = logging.getLogger(__name__)

# Get settings from Django settings.py
MPESA_CONSUMER_KEY = getattr(settings, 'MPESA_CONSUMER_KEY', '')
MPESA_CONSUMER_SECRET = getattr(settings, 'MPESA_CONSUMER_SECRET', '')
MPESA_PASSKEY = getattr(settings, 'MPESA_PASSKEY', '')
MPESA_SHORTCODE = getattr(settings, 'MPESA_SHORTCODE', '')
MPESA_ENV = getattr(settings, 'MPESA_ENVIRONMENT', 'sandbox')

# API URLs
if MPESA_ENV == "sandbox":
    BASE_URL = "https://sandbox.safaricom.co.ke"
else:
    BASE_URL = "https://api.safaricom.co.ke"

TOKEN_URL = f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
STK_PUSH_URL = f"{BASE_URL}/mpesa/stkpush/v1/processrequest"
QUERY_URL = f"{BASE_URL}/mpesa/stkpushquery/v1/query"


def get_timestamp():
    """Generate timestamp in the format YYYYMMDDHHmmss"""
    return datetime.now().strftime("%Y%m%d%H%M%S")


def generate_password(shortcode, passkey, timestamp):
    """Generate the M-Pesa API password using the provided credentials"""
    data_to_encode = shortcode + passkey + timestamp
    return base64.b64encode(data_to_encode.encode()).decode()


def get_access_token():
    """Get an OAuth access token from the M-Pesa API"""
    try:
        response = requests.get(
            TOKEN_URL,
            auth=HTTPBasicAuth(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET)
        )
        response.raise_for_status()
        result = response.json()
        return result.get("access_token")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting access token: {e}")
        return None


def initiate_stk_push(phone_number, amount, account_reference, transaction_desc, callback_url):
    """
    Initiate an STK Push request to the customer's phone
    
    Args:
        phone_number (str): Phone number in format 254XXXXXXXXX
        amount (int): Amount to pay
        account_reference (str): Payment reference e.g. "Order 123"
        transaction_desc (str): Description of the transaction
        callback_url (str): URL to receive payment notification
        
    Returns:
        dict: Response from the M-Pesa API
    """
    access_token = get_access_token()
    if not access_token:
        return {"error": "Could not get access token"}
    
    timestamp = get_timestamp()
    password = generate_password(MPESA_SHORTCODE, MPESA_PASSKEY, timestamp)
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }
    
    try:
        response = requests.post(STK_PUSH_URL, json=payload, headers=headers)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error initiating STK push: {e}")
        return {"error": str(e)}


def query_stk_status(checkout_request_id):
    """
    Query the status of an STK Push request
    
    Args:
        checkout_request_id (str): The CheckoutRequestID from the STK Push response
        
    Returns:
        dict: Response from the M-Pesa API
    """
    access_token = get_access_token()
    if not access_token:
        return {"error": "Could not get access token"}
    
    timestamp = get_timestamp()
    password = generate_password(MPESA_SHORTCODE, MPESA_PASSKEY, timestamp)
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_request_id
    }
    
    try:
        response = requests.post(QUERY_URL, json=payload, headers=headers)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error querying STK status: {e}")
        return {"error": str(e)}


def process_callback(callback_data):
    """
    Process the callback data from M-Pesa
    
    Args:
        callback_data (dict): The callback data from M-Pesa
        
    Returns:
        dict: Processed payment information
    """
    try:
        result_code = callback_data.get("Body", {}).get("stkCallback", {}).get("ResultCode")
        
        # Get callback metadata
        if result_code == 0:  # Successful payment
            callback_metadata = callback_data.get("Body", {}).get("stkCallback", {}).get("CallbackMetadata", {}).get("Item", [])
            
            payment_info = {
                "result_code": result_code,
                "result_desc": callback_data.get("Body", {}).get("stkCallback", {}).get("ResultDesc"),
                "checkout_request_id": callback_data.get("Body", {}).get("stkCallback", {}).get("CheckoutRequestID"),
                "merchant_request_id": callback_data.get("Body", {}).get("stkCallback", {}).get("MerchantRequestID"),
                "amount": None,
                "mpesa_receipt_number": None,
                "transaction_date": None,
                "phone_number": None
            }
            
            # Extract metadata values
            for item in callback_metadata:
                name = item.get("Name")
                value = item.get("Value")
                
                if name == "Amount":
                    payment_info["amount"] = value
                elif name == "MpesaReceiptNumber":
                    payment_info["mpesa_receipt_number"] = value
                elif name == "TransactionDate":
                    payment_info["transaction_date"] = value
                elif name == "PhoneNumber":
                    payment_info["phone_number"] = value
            
            return payment_info
        else:
            # Failed payment
            return {
                "result_code": result_code,
                "result_desc": callback_data.get("Body", {}).get("stkCallback", {}).get("ResultDesc"),
                "checkout_request_id": callback_data.get("Body", {}).get("stkCallback", {}).get("CheckoutRequestID"),
                "merchant_request_id": callback_data.get("Body", {}).get("stkCallback", {}).get("MerchantRequestID")
            }
    except Exception as e:
        logger.error(f"Error processing callback: {e}")
        return {"error": str(e)}
