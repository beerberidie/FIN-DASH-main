"""Summary/Dashboard API endpoints."""

from fastapi import APIRouter
from datetime import datetime

from services.csv_manager import csv_manager
from services.calculator import calculator
from services.debt_service import debt_service
from services.portfolio_service import portfolio_service
from utils.dates import get_current_month

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("")
def get_summary():
    """Get dashboard summary with all key metrics."""
    # Load all data
    accounts = csv_manager.read_csv("accounts.csv")
    transactions = csv_manager.read_csv("transactions.csv")
    categories = csv_manager.read_csv("categories.csv")
    debts = csv_manager.read_csv("debts.csv")
    goals = csv_manager.read_csv("goals.csv")
    settings_data = csv_manager.read_json("settings.json")

    # Get base currency from settings
    base_currency = settings_data.get("base_currency", "ZAR")

    # Get current month
    current_month = get_current_month()

    # Calculate total balance
    total_balance = calculator.calculate_total_balance(
        accounts, transactions, base_currency
    )

    # Calculate monthly totals
    monthly = calculator.calculate_monthly_totals(
        current_month, transactions, base_currency
    )

    # Calculate savings rate
    savings_rate = calculator.calculate_savings_rate(
        monthly["income"], monthly["expenses"]
    )

    # Calculate net worth
    net_worth = calculator.calculate_net_worth(total_balance, debts)

    # Calculate month-over-month changes
    mom_changes = calculator.calculate_month_over_month_change(
        current_month, transactions, base_currency
    )

    # Calculate spending by group
    spending_by_group = calculator.calculate_spending_by_group(
        current_month, transactions, categories, base_currency
    )

    # Calculate goal progress
    goals_summary = []
    for goal in goals:
        target = float(goal.get("target_amount", 0))
        current = float(goal.get("current_amount", 0))
        progress = (current / target * 100) if target > 0 else 0

        goals_summary.append(
            {
                "id": goal.get("id"),
                "name": goal.get("name"),
                "target_amount": target,
                "current_amount": current,
                "progress_percent": round(progress, 1),
                "remaining": target - current,
            }
        )

    # Get debt summary
    total_debt = debt_service.get_total_debt()
    minimum_payment = debt_service.get_minimum_payment()
    active_debts = [d for d in debts if float(d.get("current_balance", 0)) > 0]

    # Get portfolio summary
    try:
        portfolio_value = portfolio_service.get_total_portfolio_value(base_currency)
        portfolio_pl = portfolio_service.get_portfolio_profit_loss(base_currency)
    except Exception:
        # If no investments or error, set to 0
        portfolio_value = 0.0
        portfolio_pl = {
            "total_cost": 0.0,
            "total_value": 0.0,
            "profit_loss": 0.0,
            "profit_loss_percentage": 0.0,
        }

    # Calculate total net worth including investments
    total_net_worth = net_worth + portfolio_value

    return {
        "total_balance": round(total_balance, 2),
        "monthly_income": round(monthly["income"], 2),
        "monthly_expenses": round(monthly["expenses"], 2),
        "monthly_surplus": round(monthly["net"], 2),
        "savings_rate": round(savings_rate, 1),
        "net_worth": round(net_worth, 2),
        "total_net_worth": round(total_net_worth, 2),
        "base_currency": base_currency,
        "month_over_month": {
            "income_change": round(mom_changes["income_change"], 1),
            "expenses_change": round(mom_changes["expenses_change"], 1),
            "net_change": round(mom_changes["net_change"], 1),
        },
        "spending_by_group": {k: round(v, 2) for k, v in spending_by_group.items()},
        "goals": goals_summary,
        "current_month": current_month,
        "debt_summary": {
            "total_debt": round(total_debt, 2),
            "minimum_payment": round(minimum_payment, 2),
            "active_debt_count": len(active_debts),
        },
        "portfolio_summary": {
            "total_value": round(portfolio_value, 2),
            "total_cost": round(portfolio_pl["total_cost"], 2),
            "profit_loss": round(portfolio_pl["profit_loss"], 2),
            "profit_loss_percentage": round(portfolio_pl["profit_loss_percentage"], 1),
        },
    }
