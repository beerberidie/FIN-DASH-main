"""Tests for multi-currency support."""
import requests
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8777/api"


def test_list_currencies():
    """Test listing all currencies."""
    print("\n=== Test: List Currencies ===")
    response = requests.get(f"{BASE_URL}/currencies")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    currencies = response.json()
    print(f"✓ Found {len(currencies)} currencies")
    
    # Check for default currencies
    currency_codes = [c['code'] for c in currencies]
    assert 'ZAR' in currency_codes, "ZAR not found"
    assert 'USD' in currency_codes, "USD not found"
    assert 'EUR' in currency_codes, "EUR not found"
    print("✓ Default currencies present (ZAR, USD, EUR)")
    
    return currencies


def test_get_currency():
    """Test getting a specific currency."""
    print("\n=== Test: Get Currency ===")
    response = requests.get(f"{BASE_URL}/currencies/ZAR")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    currency = response.json()
    assert currency['code'] == 'ZAR', "Wrong currency code"
    assert currency['name'] == 'South African Rand', "Wrong currency name"
    assert currency['symbol'] == 'R', "Wrong currency symbol"
    print(f"✓ Retrieved currency: {currency['code']} - {currency['name']} ({currency['symbol']})")


def test_create_exchange_rate():
    """Test creating an exchange rate."""
    print("\n=== Test: Create Exchange Rate ===")

    today = str(date.today())
    rate_data = {
        "from_currency": "USD",
        "to_currency": "ZAR",
        "rate": 18.75,
        "date": today,
        "source": "test"
    }

    response = requests.post(f"{BASE_URL}/currencies/exchange-rates", json=rate_data)
    if response.status_code != 201:
        print(f"Error response: {response.status_code}")
        print(f"Error details: {response.text}")
    assert response.status_code == 201, f"Failed: {response.text}"
    
    rate = response.json()
    assert rate['from_currency'] == 'USD', "Wrong from_currency"
    assert rate['to_currency'] == 'ZAR', "Wrong to_currency"
    assert rate['rate'] == 18.75, "Wrong rate"
    print(f"✓ Created exchange rate: 1 USD = {rate['rate']} ZAR")
    
    return rate


def test_list_exchange_rates():
    """Test listing exchange rates."""
    print("\n=== Test: List Exchange Rates ===")
    response = requests.get(f"{BASE_URL}/currencies/exchange-rates/list")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    rates = response.json()
    print(f"✓ Found {len(rates)} exchange rates")
    
    # Test filtering
    response = requests.get(f"{BASE_URL}/currencies/exchange-rates/list?from_currency=USD")
    assert response.status_code == 200, f"Failed: {response.text}"
    filtered_rates = response.json()
    print(f"✓ Found {len(filtered_rates)} USD exchange rates")
    
    return rates


def test_get_latest_rate():
    """Test getting the latest exchange rate."""
    print("\n=== Test: Get Latest Exchange Rate ===")
    response = requests.get(f"{BASE_URL}/currencies/exchange-rates/latest/USD/ZAR")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    rate = response.json()
    print(f"✓ Latest rate: 1 USD = {rate['rate']} ZAR (date: {rate['date']})")
    
    return rate


def test_currency_conversion():
    """Test currency conversion."""
    print("\n=== Test: Currency Conversion ===")
    
    conversion_data = {
        "amount": 100.0,
        "from_currency": "USD",
        "to_currency": "ZAR"
    }
    
    response = requests.post(f"{BASE_URL}/currencies/convert", json=conversion_data)
    assert response.status_code == 200, f"Failed: {response.text}"
    
    result = response.json()
    assert result['original_amount'] == 100.0, "Wrong original amount"
    assert result['from_currency'] == 'USD', "Wrong from_currency"
    assert result['to_currency'] == 'ZAR', "Wrong to_currency"
    assert result['converted_amount'] > 0, "Converted amount should be positive"
    
    print(f"✓ Converted {result['original_amount']} {result['from_currency']} = "
          f"{result['converted_amount']:.2f} {result['to_currency']} "
          f"(rate: {result['exchange_rate']})")
    
    return result


def test_same_currency_conversion():
    """Test conversion between same currency."""
    print("\n=== Test: Same Currency Conversion ===")
    
    conversion_data = {
        "amount": 100.0,
        "from_currency": "ZAR",
        "to_currency": "ZAR"
    }
    
    response = requests.post(f"{BASE_URL}/currencies/convert", json=conversion_data)
    assert response.status_code == 200, f"Failed: {response.text}"
    
    result = response.json()
    assert result['converted_amount'] == 100.0, "Same currency should return same amount"
    assert result['exchange_rate'] == 1.0, "Same currency rate should be 1.0"
    print(f"✓ Same currency conversion: {result['original_amount']} ZAR = {result['converted_amount']} ZAR")


def test_multi_currency_transaction():
    """Test creating a transaction in a different currency."""
    print("\n=== Test: Multi-Currency Transaction ===")
    
    # Get an account
    accounts_response = requests.get(f"{BASE_URL}/accounts")
    accounts = accounts_response.json()
    account_id = accounts[0]['id'] if accounts else "acc_main"
    
    # Get a category
    categories_response = requests.get(f"{BASE_URL}/categories")
    categories = categories_response.json()
    category_id = categories[0]['id'] if categories else None
    
    # Create transaction in USD
    transaction_data = {
        "date": str(date.today()),
        "description": "Test USD Transaction",
        "amount": 50.0,
        "category_id": category_id,
        "account_id": account_id,
        "type": "income",
        "currency": "USD",
        "source": "test"
    }
    
    response = requests.post(f"{BASE_URL}/transactions", json=transaction_data)
    assert response.status_code == 201, f"Failed: {response.text}"
    
    transaction = response.json()
    assert transaction['currency'] == 'USD', "Wrong currency"
    assert transaction['amount'] == 50.0, "Wrong amount"
    print(f"✓ Created transaction: {transaction['amount']} {transaction['currency']} - {transaction['description']}")
    
    return transaction


def test_summary_with_multi_currency():
    """Test that summary correctly handles multi-currency transactions."""
    print("\n=== Test: Summary with Multi-Currency ===")
    
    response = requests.get(f"{BASE_URL}/summary")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    summary = response.json()
    assert 'base_currency' in summary, "base_currency not in summary"
    assert 'total_balance' in summary, "total_balance not in summary"
    
    print(f"✓ Summary base currency: {summary['base_currency']}")
    print(f"✓ Total balance: {summary['total_balance']} {summary['base_currency']}")
    print(f"✓ Monthly income: {summary['monthly_income']} {summary['base_currency']}")
    print(f"✓ Monthly expenses: {summary['monthly_expenses']} {summary['base_currency']}")


def run_all_tests():
    """Run all currency tests."""
    print("\n" + "="*60)
    print("MULTI-CURRENCY SUPPORT TESTS")
    print("="*60)
    
    try:
        # Test currencies
        test_list_currencies()
        test_get_currency()
        
        # Test exchange rates
        test_create_exchange_rate()
        test_list_exchange_rates()
        test_get_latest_rate()
        
        # Test conversions
        test_currency_conversion()
        test_same_currency_conversion()
        
        # Test transactions
        test_multi_currency_transaction()
        test_summary_with_multi_currency()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED!")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        raise
    except Exception as e:
        print(f"\n✗ ERROR: {e}\n")
        raise


if __name__ == "__main__":
    run_all_tests()

