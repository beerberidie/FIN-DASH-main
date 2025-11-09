"""Tests for investment tracking and portfolio management."""
import requests
from datetime import date

BASE_URL = "http://127.0.0.1:8777/api"


def test_create_investment():
    """Test creating an investment."""
    print("\n=== Test: Create Investment ===")
    
    investment_data = {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "type": "stock",
        "currency": "USD",
        "quantity": 0,
        "average_cost": 0,
        "current_price": 175.50,
        "last_updated": str(date.today()),
        "notes": "Tech stock"
    }
    
    response = requests.post(f"{BASE_URL}/investments", json=investment_data)
    assert response.status_code == 201, f"Failed: {response.text}"
    
    investment = response.json()
    assert investment['symbol'] == 'AAPL', "Wrong symbol"
    assert investment['name'] == 'Apple Inc.', "Wrong name"
    assert investment['type'] == 'stock', "Wrong type"
    print(f"✓ Created investment: {investment['symbol']} - {investment['name']}")
    
    return investment


def test_list_investments():
    """Test listing investments."""
    print("\n=== Test: List Investments ===")
    
    response = requests.get(f"{BASE_URL}/investments")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    investments = response.json()
    print(f"✓ Found {len(investments)} investments")
    
    return investments


def test_get_investment(investment_id):
    """Test getting a specific investment."""
    print("\n=== Test: Get Investment ===")
    
    response = requests.get(f"{BASE_URL}/investments/{investment_id}")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    investment = response.json()
    print(f"✓ Retrieved investment: {investment['symbol']} - {investment['name']}")
    
    return investment


def test_update_price(investment_id):
    """Test updating investment price."""
    print("\n=== Test: Update Price ===")
    
    price_update = {
        "current_price": 180.25,
        "last_updated": str(date.today())
    }
    
    response = requests.patch(f"{BASE_URL}/investments/{investment_id}/price", json=price_update)
    assert response.status_code == 200, f"Failed: {response.text}"
    
    investment = response.json()
    assert investment['current_price'] == 180.25, "Price not updated"
    print(f"✓ Updated price to ${investment['current_price']}")
    
    return investment


def test_create_buy_transaction(investment_id):
    """Test creating a buy transaction."""
    print("\n=== Test: Create Buy Transaction ===")
    
    transaction_data = {
        "investment_id": investment_id,
        "date": str(date.today()),
        "type": "buy",
        "quantity": 10,
        "price": 175.00,
        "fees": 5.00,
        "total_amount": 1755.00,  # (10 * 175) + 5
        "notes": "Initial purchase"
    }
    
    response = requests.post(f"{BASE_URL}/investments/transactions", json=transaction_data)
    assert response.status_code == 201, f"Failed: {response.text}"
    
    transaction = response.json()
    assert transaction['type'] == 'buy', "Wrong transaction type"
    assert transaction['quantity'] == 10, "Wrong quantity"
    print(f"✓ Created buy transaction: {transaction['quantity']} shares @ ${transaction['price']}")
    
    return transaction


def test_investment_updated_after_buy(investment_id):
    """Test that investment quantity and average cost are updated after buy."""
    print("\n=== Test: Investment Updated After Buy ===")
    
    response = requests.get(f"{BASE_URL}/investments/{investment_id}")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    investment = response.json()
    assert investment['quantity'] == 10, f"Expected quantity 10, got {investment['quantity']}"
    assert investment['average_cost'] == 175.50, f"Expected avg cost 175.50, got {investment['average_cost']}"
    print(f"✓ Investment updated: {investment['quantity']} shares @ avg ${investment['average_cost']}")


def test_create_another_buy_transaction(investment_id):
    """Test creating another buy transaction to test average cost calculation."""
    print("\n=== Test: Create Another Buy Transaction ===")
    
    transaction_data = {
        "investment_id": investment_id,
        "date": str(date.today()),
        "type": "buy",
        "quantity": 5,
        "price": 180.00,
        "fees": 3.00,
        "total_amount": 903.00,  # (5 * 180) + 3
        "notes": "Additional purchase"
    }
    
    response = requests.post(f"{BASE_URL}/investments/transactions", json=transaction_data)
    assert response.status_code == 201, f"Failed: {response.text}"
    
    transaction = response.json()
    print(f"✓ Created second buy transaction: {transaction['quantity']} shares @ ${transaction['price']}")
    
    return transaction


def test_average_cost_calculation(investment_id):
    """Test that average cost is calculated correctly."""
    print("\n=== Test: Average Cost Calculation ===")
    
    response = requests.get(f"{BASE_URL}/investments/{investment_id}")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    investment = response.json()
    # Total cost: 1755 + 903 = 2658
    # Total quantity: 10 + 5 = 15
    # Average cost: 2658 / 15 = 177.20
    expected_quantity = 15
    expected_avg_cost = 177.20
    
    assert investment['quantity'] == expected_quantity, f"Expected quantity {expected_quantity}, got {investment['quantity']}"
    assert abs(investment['average_cost'] - expected_avg_cost) < 0.01, f"Expected avg cost {expected_avg_cost}, got {investment['average_cost']}"
    print(f"✓ Average cost calculated correctly: {investment['quantity']} shares @ avg ${investment['average_cost']}")


def test_create_sell_transaction(investment_id):
    """Test creating a sell transaction."""
    print("\n=== Test: Create Sell Transaction ===")
    
    transaction_data = {
        "investment_id": investment_id,
        "date": str(date.today()),
        "type": "sell",
        "quantity": 5,
        "price": 185.00,
        "fees": 3.00,
        "total_amount": 922.00,  # (5 * 185) - 3
        "notes": "Partial sale"
    }
    
    response = requests.post(f"{BASE_URL}/investments/transactions", json=transaction_data)
    assert response.status_code == 201, f"Failed: {response.text}"
    
    transaction = response.json()
    assert transaction['type'] == 'sell', "Wrong transaction type"
    print(f"✓ Created sell transaction: {transaction['quantity']} shares @ ${transaction['price']}")
    
    return transaction


def test_quantity_reduced_after_sell(investment_id):
    """Test that quantity is reduced after sell."""
    print("\n=== Test: Quantity Reduced After Sell ===")
    
    response = requests.get(f"{BASE_URL}/investments/{investment_id}")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    investment = response.json()
    expected_quantity = 10  # 15 - 5
    
    assert investment['quantity'] == expected_quantity, f"Expected quantity {expected_quantity}, got {investment['quantity']}"
    print(f"✓ Quantity reduced to {investment['quantity']} shares")


def test_list_transactions(investment_id):
    """Test listing transactions for an investment."""
    print("\n=== Test: List Transactions ===")
    
    response = requests.get(f"{BASE_URL}/investments/transactions/list?investment_id={investment_id}")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    transactions = response.json()
    assert len(transactions) == 3, f"Expected 3 transactions, got {len(transactions)}"
    print(f"✓ Found {len(transactions)} transactions")
    
    return transactions


def test_get_investment_performance(investment_id):
    """Test getting investment performance metrics."""
    print("\n=== Test: Get Investment Performance ===")
    
    response = requests.get(f"{BASE_URL}/investments/{investment_id}/performance")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    performance = response.json()
    assert 'profit_loss' in performance, "Missing profit_loss"
    assert 'profit_loss_percentage' in performance, "Missing profit_loss_percentage"
    
    print(f"✓ Performance metrics:")
    print(f"  - Quantity: {performance['quantity']}")
    print(f"  - Total Cost: ${performance['total_cost']:.2f}")
    print(f"  - Current Value: ${performance['current_value']:.2f}")
    print(f"  - Profit/Loss: ${performance['profit_loss']:.2f} ({performance['profit_loss_percentage']:.2f}%)")
    
    return performance


def test_create_crypto_investment():
    """Test creating a cryptocurrency investment."""
    print("\n=== Test: Create Crypto Investment ===")
    
    investment_data = {
        "symbol": "BTC",
        "name": "Bitcoin",
        "type": "crypto",
        "currency": "USD",
        "quantity": 0.5,
        "average_cost": 45000.00,
        "current_price": 48000.00,
        "last_updated": str(date.today()),
        "notes": "Cryptocurrency"
    }
    
    response = requests.post(f"{BASE_URL}/investments", json=investment_data)
    assert response.status_code == 201, f"Failed: {response.text}"
    
    investment = response.json()
    print(f"✓ Created crypto investment: {investment['symbol']} - {investment['name']}")
    
    return investment


def test_create_etf_investment():
    """Test creating an ETF investment."""
    print("\n=== Test: Create ETF Investment ===")
    
    investment_data = {
        "symbol": "SPY",
        "name": "SPDR S&P 500 ETF",
        "type": "etf",
        "currency": "USD",
        "quantity": 20,
        "average_cost": 450.00,
        "current_price": 455.00,
        "last_updated": str(date.today()),
        "notes": "S&P 500 ETF"
    }
    
    response = requests.post(f"{BASE_URL}/investments", json=investment_data)
    assert response.status_code == 201, f"Failed: {response.text}"
    
    investment = response.json()
    print(f"✓ Created ETF investment: {investment['symbol']} - {investment['name']}")
    
    return investment


def test_get_portfolio_summary():
    """Test getting portfolio summary."""
    print("\n=== Test: Get Portfolio Summary ===")
    
    response = requests.get(f"{BASE_URL}/investments/portfolio/summary")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    summary = response.json()
    assert 'total_investments' in summary, "Missing total_investments"
    assert 'total_value' in summary, "Missing total_value"
    assert 'by_type' in summary, "Missing by_type"
    
    print(f"✓ Portfolio Summary:")
    print(f"  - Total Investments: {summary['total_investments']}")
    print(f"  - Total Value: ${summary['total_value']:.2f}")
    print(f"  - Total Cost: ${summary['total_cost']:.2f}")
    print(f"  - Profit/Loss: ${summary['total_profit_loss']:.2f} ({summary['total_profit_loss_percentage']:.2f}%)")
    print(f"  - Asset Allocation:")
    for inv_type, data in summary['by_type'].items():
        print(f"    * {inv_type}: {data['percentage']:.1f}% (${data['total_value']:.2f})")
    
    return summary


def test_get_asset_allocation():
    """Test getting asset allocation."""
    print("\n=== Test: Get Asset Allocation ===")
    
    response = requests.get(f"{BASE_URL}/investments/portfolio/allocation")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    allocation = response.json()
    print(f"✓ Asset Allocation:")
    for inv_type, percentage in allocation.items():
        print(f"  - {inv_type}: {percentage:.1f}%")
    
    return allocation


def test_get_portfolio_value():
    """Test getting total portfolio value."""
    print("\n=== Test: Get Portfolio Value ===")
    
    response = requests.get(f"{BASE_URL}/investments/portfolio/value")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    result = response.json()
    assert 'total_value' in result, "Missing total_value"
    print(f"✓ Total Portfolio Value: ${result['total_value']:.2f} {result['currency']}")
    
    return result


def test_summary_includes_portfolio():
    """Test that summary endpoint includes portfolio data."""
    print("\n=== Test: Summary Includes Portfolio ===")
    
    response = requests.get(f"{BASE_URL}/summary")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    summary = response.json()
    assert 'portfolio_summary' in summary, "Missing portfolio_summary"
    assert 'total_net_worth' in summary, "Missing total_net_worth"
    
    print(f"✓ Summary includes portfolio:")
    print(f"  - Portfolio Value: ${summary['portfolio_summary']['total_value']:.2f}")
    print(f"  - Portfolio P/L: ${summary['portfolio_summary']['profit_loss']:.2f}")
    print(f"  - Total Net Worth: ${summary['total_net_worth']:.2f}")


def run_all_tests():
    """Run all investment tests."""
    print("\n" + "="*60)
    print("INVESTMENT TRACKING TESTS")
    print("="*60)
    
    try:
        # Investment CRUD tests
        investment = test_create_investment()
        test_list_investments()
        test_get_investment(investment['id'])
        test_update_price(investment['id'])
        
        # Transaction tests
        test_create_buy_transaction(investment['id'])
        test_investment_updated_after_buy(investment['id'])
        test_create_another_buy_transaction(investment['id'])
        test_average_cost_calculation(investment['id'])
        test_create_sell_transaction(investment['id'])
        test_quantity_reduced_after_sell(investment['id'])
        test_list_transactions(investment['id'])
        
        # Performance tests
        test_get_investment_performance(investment['id'])
        
        # Multiple investment types
        test_create_crypto_investment()
        test_create_etf_investment()
        
        # Portfolio analytics tests
        test_get_portfolio_summary()
        test_get_asset_allocation()
        test_get_portfolio_value()
        
        # Integration test
        test_summary_includes_portfolio()
        
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

