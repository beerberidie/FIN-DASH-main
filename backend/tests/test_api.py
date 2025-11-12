"""
Quick test script to verify the API is working correctly.
Run this after starting the backend server.
"""

import requests
import json

BASE_URL = "http://localhost:8777/api"


def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get("http://localhost:8777/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    return response.status_code == 200


def test_summary():
    """Test summary endpoint."""
    print("Testing summary endpoint...")
    response = requests.get(f"{BASE_URL}/summary")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total Balance: R {data['total_balance']}")
        print(f"Savings Rate: {data['savings_rate']}%")
        print(f"Monthly Surplus: R {data['monthly_surplus']}")
        print(f"Net Worth: R {data['net_worth']}\n")
    return response.status_code == 200


def test_transactions():
    """Test transactions endpoint."""
    print("Testing transactions endpoint...")
    response = requests.get(f"{BASE_URL}/transactions")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total transactions: {len(data)}")
        if data:
            print(
                f"First transaction: {data[0]['description']} - R {data[0]['amount']}\n"
            )
    return response.status_code == 200


def test_categories():
    """Test categories endpoint."""
    print("Testing categories endpoint...")
    response = requests.get(f"{BASE_URL}/categories")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total categories: {len(data)}")
        groups = {}
        for cat in data:
            group = cat["group"]
            groups[group] = groups.get(group, 0) + 1
        print(f"Categories by group: {groups}\n")
    return response.status_code == 200


def test_accounts():
    """Test accounts endpoint."""
    print("Testing accounts endpoint...")
    response = requests.get(f"{BASE_URL}/accounts")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total accounts: {len(data)}")
        for acc in data:
            print(f"  - {acc['name']} ({acc['type']}): R {acc['opening_balance']}\n")
    return response.status_code == 200


def test_create_transaction():
    """Test creating a transaction."""
    print("Testing transaction creation...")
    new_transaction = {
        "date": "2025-10-06",
        "description": "Test Transaction",
        "amount": -100.00,
        "account_id": "acc_main",
        "category_id": "cat_wants_entertainment",
        "type": "expense",
        "source": "manual",
        "tags": "test",
    }
    response = requests.post(f"{BASE_URL}/transactions", json=new_transaction)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"Created transaction: {data['id']}")
        print(f"Description: {data['description']}\n")
        return data["id"]
    return None


def test_delete_transaction(transaction_id):
    """Test deleting a transaction."""
    if not transaction_id:
        print("Skipping delete test (no transaction ID)\n")
        return False

    print(f"Testing transaction deletion...")
    response = requests.delete(f"{BASE_URL}/transactions/{transaction_id}")
    print(f"Status: {response.status_code}")
    print(f"Transaction deleted successfully\n")
    return response.status_code == 204


def main():
    """Run all tests."""
    print("=" * 50)
    print("FIN-DASH API Test Suite")
    print("=" * 50 + "\n")

    tests_passed = 0
    tests_total = 0

    # Run tests
    tests = [
        ("Health Check", test_health),
        ("Summary", test_summary),
        ("Transactions List", test_transactions),
        ("Categories List", test_categories),
        ("Accounts List", test_accounts),
    ]

    for name, test_func in tests:
        tests_total += 1
        try:
            if test_func():
                tests_passed += 1
                print(f"✓ {name} passed")
            else:
                print(f"✗ {name} failed")
        except Exception as e:
            print(f"✗ {name} failed with error: {e}")
        print()

    # Test create and delete
    tests_total += 2
    try:
        transaction_id = test_create_transaction()
        if transaction_id:
            tests_passed += 1
            print("✓ Transaction creation passed\n")

            if test_delete_transaction(transaction_id):
                tests_passed += 1
                print("✓ Transaction deletion passed\n")
            else:
                print("✗ Transaction deletion failed\n")
        else:
            print("✗ Transaction creation failed\n")
    except Exception as e:
        print(f"✗ Create/Delete test failed with error: {e}\n")

    # Summary
    print("=" * 50)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    print("=" * 50)

    if tests_passed == tests_total:
        print("\n✓ All tests passed! API is working correctly.")
    else:
        print(f"\n✗ {tests_total - tests_passed} test(s) failed.")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API.")
        print("Make sure the backend server is running on http://localhost:8777")
