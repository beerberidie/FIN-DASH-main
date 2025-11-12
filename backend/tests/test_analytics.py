"""Tests for analytics functionality (trends, predictions, health scores)."""

import requests
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8777/api"


def test_income_trend_analysis():
    """Test income trend analysis."""
    print("\n=== Test: Income Trend Analysis ===")

    response = requests.get(f"{BASE_URL}/analytics/trends/income")
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert "metric" in result, "Missing metric"
    assert result["metric"] == "income", "Wrong metric"
    assert "data_points" in result, "Missing data_points"
    assert "trend_direction" in result, "Missing trend_direction"
    assert "average" in result, "Missing average"

    print(
        f"✓ Income trend: {result['trend_direction']} ({result['trend_percentage']:.1f}%)"
    )
    print(f"  Average monthly income: {result['average']:.2f}")
    print(f"  Data points: {len(result['data_points'])}")

    return result


def test_expense_trend_analysis():
    """Test expense trend analysis."""
    print("\n=== Test: Expense Trend Analysis ===")

    response = requests.get(f"{BASE_URL}/analytics/trends/expenses?period_type=monthly")
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert result["metric"] == "expenses", "Wrong metric"
    assert result["period_type"] == "monthly", "Wrong period type"

    print(
        f"✓ Expense trend: {result['trend_direction']} ({result['trend_percentage']:.1f}%)"
    )
    print(f"  Average monthly expenses: {result['average']:.2f}")

    return result


def test_quarterly_trend():
    """Test quarterly trend analysis."""
    print("\n=== Test: Quarterly Trend Analysis ===")

    response = requests.get(f"{BASE_URL}/analytics/trends/net?period_type=quarterly")
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert result["period_type"] == "quarterly", "Wrong period type"

    print(f"✓ Quarterly net income trend: {result['trend_direction']}")
    print(f"  Data points: {len(result['data_points'])}")

    return result


def test_yoy_comparison():
    """Test year-over-year comparison."""
    print("\n=== Test: Year-over-Year Comparison ===")

    response = requests.get(f"{BASE_URL}/analytics/yoy-comparison")
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert "current_year" in result, "Missing current_year"
    assert "previous_year" in result, "Missing previous_year"
    assert "income_comparison" in result, "Missing income_comparison"
    assert "expense_comparison" in result, "Missing expense_comparison"
    assert "net_comparison" in result, "Missing net_comparison"

    income_comp = result["income_comparison"]
    expense_comp = result["expense_comparison"]

    print(f"✓ YoY Comparison: {result['current_year']} vs {result['previous_year']}")
    print(
        f"  Income: {income_comp['current_value']:.2f} vs {income_comp['previous_value']:.2f} ({income_comp['change_percentage']:.1f}%)"
    )
    print(
        f"  Expenses: {expense_comp['current_value']:.2f} vs {expense_comp['previous_value']:.2f} ({expense_comp['change_percentage']:.1f}%)"
    )
    print(
        f"  Savings rate: {result['savings_rate_current']:.1f}% vs {result['savings_rate_previous']:.1f}%"
    )

    return result


def test_spending_patterns():
    """Test spending pattern detection."""
    print("\n=== Test: Spending Pattern Detection ===")

    response = requests.get(f"{BASE_URL}/analytics/spending-patterns")
    assert response.status_code == 200, f"Failed: {response.text}"

    patterns = response.json()
    assert isinstance(patterns, list), "Expected list of patterns"

    print(f"✓ Detected {len(patterns)} spending patterns")

    if patterns:
        for i, pattern in enumerate(patterns[:3], 1):
            print(
                f"  {i}. {pattern['category']}: {pattern['pattern_type']} - {pattern['description']}"
            )

    return patterns


def test_category_insights():
    """Test category insights."""
    print("\n=== Test: Category Insights ===")

    # Get categories first
    categories_response = requests.get(f"{BASE_URL}/categories")
    categories = categories_response.json()

    if not categories:
        print("⚠ No categories found, skipping test")
        return None

    # Get insights for first category
    category_id = categories[0]["id"]
    category_name = categories[0]["name"]

    response = requests.get(f"{BASE_URL}/analytics/category-insights/{category_id}")
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert "category_id" in result, "Missing category_id"
    assert "total_spent" in result, "Missing total_spent"
    assert "transaction_count" in result, "Missing transaction_count"
    assert "trend" in result, "Missing trend"

    print(f"✓ Category insights for '{category_name}':")
    print(f"  Total spent: {result['total_spent']:.2f}")
    print(f"  Transactions: {result['transaction_count']}")
    print(f"  Average: {result['average_transaction']:.2f}")
    print(f"  Trend: {result['trend']}")
    print(f"  % of total: {result['percentage_of_total']:.1f}%")

    return result


def test_income_predictions():
    """Test income predictions."""
    print("\n=== Test: Income Predictions ===")

    response = requests.get(
        f"{BASE_URL}/analytics/predictions/income?periods_ahead=3&method=moving_average"
    )
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert "metric" in result, "Missing metric"
    assert result["metric"] == "income", "Wrong metric"
    assert "predictions" in result, "Missing predictions"
    assert "method" in result, "Missing method"

    print(f"✓ Income predictions ({result['method']}):")

    for pred in result["predictions"]:
        print(
            f"  {pred['period']}: {pred['predicted_value']:.2f} (CI: {pred['confidence_interval_low']:.2f} - {pred['confidence_interval_high']:.2f})"
        )

    if result.get("historical_accuracy"):
        print(f"  Historical accuracy: {result['historical_accuracy']:.1f}%")

    return result


def test_expense_predictions():
    """Test expense predictions with different methods."""
    print("\n=== Test: Expense Predictions (Linear Regression) ===")

    response = requests.get(
        f"{BASE_URL}/analytics/predictions/expenses?periods_ahead=3&method=linear_regression"
    )
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert result["metric"] == "expenses", "Wrong metric"
    assert result["method"] == "linear_regression", "Wrong method"

    print(f"✓ Expense predictions ({result['method']}):")

    for pred in result["predictions"]:
        print(f"  {pred['period']}: {pred['predicted_value']:.2f}")

    return result


def test_seasonal_predictions():
    """Test seasonal predictions."""
    print("\n=== Test: Seasonal Predictions ===")

    response = requests.get(
        f"{BASE_URL}/analytics/predictions/expenses?periods_ahead=6&method=seasonal"
    )
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert result["method"] == "seasonal", "Wrong method"

    print(f"✓ Seasonal predictions for expenses:")
    print(f"  Predicting {len(result['predictions'])} periods ahead")

    return result


def test_financial_health_score():
    """Test financial health score calculation."""
    print("\n=== Test: Financial Health Score ===")

    response = requests.get(f"{BASE_URL}/analytics/health-score")
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert "overall_score" in result, "Missing overall_score"
    assert "overall_status" in result, "Missing overall_status"
    assert "metrics" in result, "Missing metrics"
    assert "recommendations" in result, "Missing recommendations"

    print(
        f"✓ Financial Health Score: {result['overall_score']:.1f}/100 ({result['overall_status']})"
    )
    print(f"\n  Individual Metrics:")

    for metric in result["metrics"]:
        print(f"    {metric['name']}: {metric['score']:.0f}/100 ({metric['status']})")
        print(f"      {metric['description']}")

    if result["strengths"]:
        print(f"\n  Strengths: {', '.join(result['strengths'])}")

    if result["weaknesses"]:
        print(f"  Weaknesses: {', '.join(result['weaknesses'])}")

    if result["recommendations"]:
        print(f"\n  Top Recommendations:")
        for i, rec in enumerate(result["recommendations"][:3], 1):
            print(f"    {i}. {rec}")

    return result


def test_health_breakdown():
    """Test health metric breakdown."""
    print("\n=== Test: Health Metric Breakdown ===")

    response = requests.get(f"{BASE_URL}/analytics/health-breakdown")
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert "savings_rate" in result, "Missing savings_rate"
    assert "debt_to_income" in result, "Missing debt_to_income"
    assert "emergency_fund_months" in result, "Missing emergency_fund_months"

    print(f"✓ Health Metric Breakdown:")
    print(f"  Savings Rate: {result['savings_rate']:.1f}%")
    print(f"  Debt-to-Income: {result['debt_to_income']:.1f}%")
    print(f"  Emergency Fund: {result['emergency_fund_months']:.1f} months")
    print(f"  Budget Adherence: {result['budget_adherence']:.1f}%")
    print(f"  Investment Diversification: {result['investment_diversification']:.1f}")
    print(f"  Net Worth Trend: {result['net_worth_trend']}")

    return result


def test_income_analysis():
    """Test comprehensive income analysis."""
    print("\n=== Test: Income Analysis ===")

    response = requests.get(f"{BASE_URL}/analytics/income-analysis")
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert "trend" in result, "Missing trend"
    assert "predictions" in result, "Missing predictions"
    assert "average_monthly" in result, "Missing average_monthly"

    print(f"✓ Income Analysis:")
    print(f"  Average Monthly: {result['average_monthly']:.2f}")
    print(f"  Total: {result['total']:.2f}")
    print(f"  Growth Rate: {result['growth_rate']:.1f}%")
    print(f"  Trend: {result['trend']['trend_direction']}")

    return result


def test_expense_analysis():
    """Test comprehensive expense analysis."""
    print("\n=== Test: Expense Analysis ===")

    response = requests.get(f"{BASE_URL}/analytics/expense-analysis")
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert "trend" in result, "Missing trend"
    assert "predictions" in result, "Missing predictions"
    assert "patterns" in result, "Missing patterns"

    print(f"✓ Expense Analysis:")
    print(f"  Average Monthly: {result['average_monthly']:.2f}")
    print(f"  Total: {result['total']:.2f}")
    print(f"  Trend: {result['trend']['trend_direction']}")
    print(f"  Patterns Detected: {len(result['patterns'])}")

    return result


def test_date_range_filtering():
    """Test analytics with date range filtering."""
    print("\n=== Test: Date Range Filtering ===")

    end_date = date.today()
    start_date = end_date - timedelta(days=90)

    response = requests.get(
        f"{BASE_URL}/analytics/trends/income",
        params={"start_date": str(start_date), "end_date": str(end_date)},
    )
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()

    print(f"✓ Filtered trend analysis (last 90 days):")
    print(f"  Data points: {len(result['data_points'])}")
    print(f"  Average: {result['average']:.2f}")

    return result


def run_all_tests():
    """Run all analytics tests."""
    print("\n" + "=" * 60)
    print("ANALYTICS & REPORTING TESTS")
    print("=" * 60)

    try:
        # Trend analysis
        test_income_trend_analysis()
        test_expense_trend_analysis()
        test_quarterly_trend()

        # Year-over-year
        test_yoy_comparison()

        # Patterns and insights
        test_spending_patterns()
        test_category_insights()

        # Predictions
        test_income_predictions()
        test_expense_predictions()
        test_seasonal_predictions()

        # Financial health
        test_financial_health_score()
        test_health_breakdown()

        # Comprehensive analysis
        test_income_analysis()
        test_expense_analysis()

        # Filtering
        test_date_range_filtering()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60 + "\n")

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        raise
    except Exception as e:
        print(f"\n✗ ERROR: {e}\n")
        raise


if __name__ == "__main__":
    run_all_tests()
