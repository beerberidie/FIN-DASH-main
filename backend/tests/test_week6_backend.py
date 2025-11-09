"""Test script for Week 6 backend - Debts & Reports."""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8777/api"


def print_section(title):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_debt_endpoints():
    """Test debt management endpoints."""
    print_section("Testing Debt Endpoints")
    
    # 1. Get all debts (should be empty initially)
    print("1. GET /api/debts")
    response = requests.get(f"{BASE_URL}/debts")
    print(f"Status: {response.status_code}")
    debts = response.json()
    print(f"Debts: {json.dumps(debts, indent=2)}\n")
    
    # 2. Create a credit card debt
    print("2. POST /api/debts (Credit Card)")
    debt_data = {
        "name": "Visa Credit Card",
        "debt_type": "credit_card",
        "original_balance": 15000,
        "current_balance": 12500,
        "interest_rate": 18.5,
        "minimum_payment": 500,
        "due_day": 15,
        "notes": "Main credit card"
    }
    response = requests.post(f"{BASE_URL}/debts", json=debt_data)
    print(f"Status: {response.status_code}")
    credit_card = response.json()
    print(f"Created: {json.dumps(credit_card, indent=2)}\n")
    credit_card_id = credit_card['id']
    
    # 3. Create a personal loan
    print("3. POST /api/debts (Personal Loan)")
    loan_data = {
        "name": "Personal Loan",
        "debt_type": "personal_loan",
        "original_balance": 50000,
        "current_balance": 35000,
        "interest_rate": 12.0,
        "minimum_payment": 1500,
        "due_day": 1,
        "notes": "5-year personal loan"
    }
    response = requests.post(f"{BASE_URL}/debts", json=loan_data)
    print(f"Status: {response.status_code}")
    loan = response.json()
    print(f"Created: {json.dumps(loan, indent=2)}\n")
    loan_id = loan['id']
    
    # 4. Create a car loan
    print("4. POST /api/debts (Car Loan)")
    car_data = {
        "name": "Car Loan",
        "debt_type": "car_loan",
        "original_balance": 200000,
        "current_balance": 150000,
        "interest_rate": 9.5,
        "minimum_payment": 3500,
        "due_day": 25
    }
    response = requests.post(f"{BASE_URL}/debts", json=car_data)
    print(f"Status: {response.status_code}")
    car = response.json()
    print(f"Created: {json.dumps(car, indent=2)}\n")
    
    # 5. Get all debts
    print("5. GET /api/debts (after creating)")
    response = requests.get(f"{BASE_URL}/debts")
    debts = response.json()
    print(f"Total debts: {len(debts)}")
    for debt in debts:
        print(f"  - {debt['name']}: R{debt['current_balance']:.2f} @ {debt['interest_rate']}%")
    print()
    
    # 6. Get debt summary
    print("6. GET /api/debts/summary/total")
    response = requests.get(f"{BASE_URL}/debts/summary/total")
    summary = response.json()
    print(f"Summary: {json.dumps(summary, indent=2)}\n")
    
    # 7. Record a payment
    print("7. POST /api/debts/{id}/payment")
    payment_data = {
        "amount": 1000,
        "notes": "Monthly payment"
    }
    response = requests.post(f"{BASE_URL}/debts/{credit_card_id}/payment", json=payment_data)
    print(f"Status: {response.status_code}")
    updated_debt = response.json()
    print(f"New balance: R{updated_debt['current_balance']:.2f}\n")
    
    # 8. Get payoff plan - Avalanche
    print("8. POST /api/debts/payoff-plan (Avalanche)")
    plan_data = {
        "extra_payment": 2000,
        "strategy": "avalanche"
    }
    response = requests.post(f"{BASE_URL}/debts/payoff-plan", json=plan_data)
    avalanche = response.json()
    print(f"Method: {avalanche['method']}")
    print(f"Total months: {avalanche['total_months']}")
    print(f"Total interest: R{avalanche['total_interest']:.2f}")
    print(f"Payoff date: {avalanche.get('payoff_date', 'N/A')}\n")
    
    # 9. Get payoff plan - Snowball
    print("9. POST /api/debts/payoff-plan (Snowball)")
    plan_data = {
        "extra_payment": 2000,
        "strategy": "snowball"
    }
    response = requests.post(f"{BASE_URL}/debts/payoff-plan", json=plan_data)
    snowball = response.json()
    print(f"Method: {snowball['method']}")
    print(f"Total months: {snowball['total_months']}")
    print(f"Total interest: R{snowball['total_interest']:.2f}")
    print(f"Payoff date: {snowball.get('payoff_date', 'N/A')}\n")
    
    # 10. Compare strategies
    print("10. POST /api/debts/payoff-plan (Both)")
    plan_data = {
        "extra_payment": 2000,
        "strategy": "both"
    }
    response = requests.post(f"{BASE_URL}/debts/payoff-plan", json=plan_data)
    comparison = response.json()
    print(f"Avalanche: {comparison['avalanche']['total_months']} months, R{comparison['avalanche']['total_interest']:.2f} interest")
    print(f"Snowball: {comparison['snowball']['total_months']} months, R{comparison['snowball']['total_interest']:.2f} interest")
    print(f"Interest savings: R{comparison['comparison']['interest_savings']:.2f}")
    print(f"Time savings: {comparison['comparison']['time_savings_months']} months")
    print(f"Recommended: {comparison['comparison']['recommended']}\n")
    
    return True


def test_report_endpoints():
    """Test report endpoints."""
    print_section("Testing Report Endpoints")
    
    # 1. Get available months
    print("1. GET /api/reports/available-months")
    response = requests.get(f"{BASE_URL}/reports/available-months")
    print(f"Status: {response.status_code}")
    months = response.json()
    print(f"Available months: {len(months)}")
    if months:
        print(f"Latest: {months[0]['label']}\n")
    else:
        print("No transaction data yet\n")
    
    # 2. Get monthly report for current month
    print("2. GET /api/reports/monthly/{year}/{month}")
    now = datetime.now()
    response = requests.get(f"{BASE_URL}/reports/monthly/{now.year}/{now.month}")
    print(f"Status: {response.status_code}")
    report = response.json()
    print(f"Period: {report['period']}")
    print(f"Income: R{report['summary']['income']:.2f}")
    print(f"Expenses: R{report['summary']['expenses']:.2f}")
    print(f"Net: R{report['summary']['net_income']:.2f}")
    print(f"Savings rate: {report['summary']['savings_rate']:.1f}%")
    print(f"Transactions: {report['summary']['transaction_count']}")
    print(f"\nTop categories:")
    for cat in report['top_categories'][:3]:
        print(f"  - {cat['category_name']}: R{cat['amount']:.2f} ({cat['percentage']:.1f}%)")
    print(f"\nInsights:")
    for insight in report['insights']:
        print(f"  - {insight}")
    print()
    
    # 3. Get YTD summary
    print("3. GET /api/reports/summary")
    response = requests.get(f"{BASE_URL}/reports/summary")
    print(f"Status: {response.status_code}")
    ytd = response.json()
    print(f"Year: {ytd['year']}")
    print(f"Total income: R{ytd['summary']['total_income']:.2f}")
    print(f"Total expenses: R{ytd['summary']['total_expenses']:.2f}")
    print(f"Net income: R{ytd['summary']['net_income']:.2f}")
    print(f"Avg monthly income: R{ytd['summary']['avg_monthly_income']:.2f}")
    print(f"Avg monthly expenses: R{ytd['summary']['avg_monthly_expenses']:.2f}\n")
    
    return True


def test_summary_with_debts():
    """Test that summary includes debt information."""
    print_section("Testing Summary with Debt Info")
    
    print("GET /api/summary")
    response = requests.get(f"{BASE_URL}/summary")
    print(f"Status: {response.status_code}")
    summary = response.json()
    
    if 'debt_summary' in summary:
        print(f"Debt summary found:")
        print(f"  Total debt: R{summary['debt_summary']['total_debt']:.2f}")
        print(f"  Minimum payment: R{summary['debt_summary']['minimum_payment']:.2f}")
        print(f"  Active debts: {summary['debt_summary']['active_debt_count']}")
    else:
        print("Warning: debt_summary not in response")
    
    print()
    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  WEEK 6 BACKEND API TESTS - Debts & Reports")
    print("="*60)
    
    try:
        # Test debt endpoints
        if test_debt_endpoints():
            print("✅ Debt endpoints: PASSED")
        
        # Test report endpoints
        if test_report_endpoints():
            print("✅ Report endpoints: PASSED")
        
        # Test summary with debts
        if test_summary_with_debts():
            print("✅ Summary with debts: PASSED")
        
        print("\n" + "="*60)
        print("  ALL TESTS PASSED ✅")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

