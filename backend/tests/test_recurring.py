"""Test script for recurring transactions functionality."""

import requests
import json
from datetime import date, timedelta

BASE_URL = "http://localhost:8777/api"


def print_response(title, response):
    """Print formatted response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    if response.status_code != 204:
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)


def test_recurring_transactions():
    """Test recurring transactions endpoints."""

    print("\n🧪 Testing Recurring Transactions Feature")
    print("=" * 60)

    # 1. Get all recurring transactions (should be empty initially)
    print("\n1️⃣ Getting all recurring transactions...")
    response = requests.get(f"{BASE_URL}/recurring")
    print_response("GET /recurring", response)

    # 2. Create a monthly salary recurring transaction
    print("\n2️⃣ Creating monthly salary recurring transaction...")
    salary_data = {
        "name": "Monthly Salary",
        "amount": 18000.00,
        "category_id": "cat_income_salary",
        "account_id": "acc_main",
        "type": "income",
        "frequency": "monthly",
        "start_date": "2025-10-01",
        "day_of_month": 25,
        "is_active": True,
        "notes": "Regular monthly salary payment",
    }
    response = requests.post(f"{BASE_URL}/recurring", json=salary_data)
    print_response("POST /recurring (Salary)", response)
    salary_id = response.json()["id"] if response.status_code == 201 else None

    # 3. Create a monthly rent recurring transaction
    print("\n3️⃣ Creating monthly rent recurring transaction...")
    rent_data = {
        "name": "Rent Payment",
        "amount": 4500.00,
        "category_id": "cat_needs_rent",
        "account_id": "acc_main",
        "type": "expense",
        "frequency": "monthly",
        "start_date": "2025-10-01",
        "day_of_month": 1,
        "is_active": True,
        "notes": "Monthly rent for apartment",
    }
    response = requests.post(f"{BASE_URL}/recurring", json=rent_data)
    print_response("POST /recurring (Rent)", response)
    rent_id = response.json()["id"] if response.status_code == 201 else None

    # 4. Create a weekly grocery shopping recurring transaction
    print("\n4️⃣ Creating weekly grocery shopping recurring transaction...")
    grocery_data = {
        "name": "Weekly Groceries",
        "amount": 800.00,
        "category_id": "cat_needs_groceries",
        "account_id": "acc_main",
        "type": "expense",
        "frequency": "weekly",
        "start_date": "2025-10-01",
        "day_of_week": 5,  # Saturday
        "is_active": True,
        "notes": "Weekly grocery shopping at Pick n Pay",
    }
    response = requests.post(f"{BASE_URL}/recurring", json=grocery_data)
    print_response("POST /recurring (Groceries)", response)
    grocery_id = response.json()["id"] if response.status_code == 201 else None

    # 5. Create a quarterly insurance payment
    print("\n5️⃣ Creating quarterly insurance payment...")
    insurance_data = {
        "name": "Car Insurance",
        "amount": 1200.00,
        "category_id": "cat_needs_transport",
        "account_id": "acc_main",
        "type": "expense",
        "frequency": "quarterly",
        "start_date": "2025-10-01",
        "day_of_month": 15,
        "is_active": True,
        "notes": "Quarterly car insurance premium",
    }
    response = requests.post(f"{BASE_URL}/recurring", json=insurance_data)
    print_response("POST /recurring (Insurance)", response)
    insurance_id = response.json()["id"] if response.status_code == 201 else None

    # 6. Get all recurring transactions
    print("\n6️⃣ Getting all recurring transactions...")
    response = requests.get(f"{BASE_URL}/recurring")
    print_response("GET /recurring (All)", response)

    # 7. Get only active recurring transactions
    print("\n7️⃣ Getting active recurring transactions...")
    response = requests.get(f"{BASE_URL}/recurring?active_only=true")
    print_response("GET /recurring?active_only=true", response)

    # 8. Get a specific recurring transaction
    if salary_id:
        print(f"\n8️⃣ Getting specific recurring transaction ({salary_id})...")
        response = requests.get(f"{BASE_URL}/recurring/{salary_id}")
        print_response(f"GET /recurring/{salary_id}", response)

    # 9. Update a recurring transaction
    if rent_id:
        print(f"\n9️⃣ Updating rent amount...")
        update_data = {
            "amount": 5000.00,
            "notes": "Rent increased from R4,500 to R5,000",
        }
        response = requests.put(f"{BASE_URL}/recurring/{rent_id}", json=update_data)
        print_response(f"PUT /recurring/{rent_id}", response)

    # 10. Toggle active status
    if grocery_id:
        print(f"\n🔟 Toggling grocery recurring transaction...")
        response = requests.post(f"{BASE_URL}/recurring/{grocery_id}/toggle")
        print_response(f"POST /recurring/{grocery_id}/toggle", response)

        # Toggle back
        print(f"\n   Toggling back to active...")
        response = requests.post(f"{BASE_URL}/recurring/{grocery_id}/toggle")
        print_response(f"POST /recurring/{grocery_id}/toggle (back)", response)

    # 11. Check due transactions
    print("\n1️⃣1️⃣ Checking due recurring transactions...")
    response = requests.get(f"{BASE_URL}/recurring/due/check")
    print_response("GET /recurring/due/check", response)

    # 12. Process recurring transactions (generate actual transactions)
    print("\n1️⃣2️⃣ Processing recurring transactions...")
    response = requests.post(f"{BASE_URL}/recurring/process/generate")
    print_response("POST /recurring/process/generate", response)

    # 13. Get transactions to see generated ones
    print("\n1️⃣3️⃣ Getting recent transactions...")
    response = requests.get(f"{BASE_URL}/transactions")
    print_response("GET /transactions", response)

    # 14. Delete a recurring transaction
    if insurance_id:
        print(f"\n1️⃣4️⃣ Deleting insurance recurring transaction...")
        response = requests.delete(f"{BASE_URL}/recurring/{insurance_id}")
        print_response(f"DELETE /recurring/{insurance_id}", response)

    # 15. Final check - get all recurring transactions
    print("\n1️⃣5️⃣ Final check - all recurring transactions...")
    response = requests.get(f"{BASE_URL}/recurring")
    print_response("GET /recurring (Final)", response)

    print("\n" + "=" * 60)
    print("✅ Recurring Transactions Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_recurring_transactions()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to backend API")
        print("   Make sure the backend is running on http://localhost:8777")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
