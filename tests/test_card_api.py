#!/usr/bin/env python3
"""Test card API endpoints."""
import requests
import json

API_BASE = "http://127.0.0.1:8777/api"

def test_create_card():
    """Test creating a credit card."""
    print("Testing card creation...")
    
    card_data = {
        "name": "Standard Bank Credit Card",
        "card_type": "credit",
        "last_four_digits": "1234",
        "account_id": "acc_creditcard",
        "issuer": "Standard Bank",
        "available_balance": 6946.0,
        "current_balance": -1053.0,
        "credit_limit": 8000.0,
        "expiry_month": 12,
        "expiry_year": 2027,
        "is_active": True,
        "color": "#dc2626",
        "icon": "CreditCard"
    }
    
    try:
        response = requests.post(f"{API_BASE}/cards", json=card_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_list_cards():
    """Test listing all cards."""
    print("\nTesting card listing...")
    
    try:
        response = requests.get(f"{API_BASE}/cards")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("CARD API TESTS")
    print("=" * 60)
    
    test_create_card()
    test_list_cards()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)

