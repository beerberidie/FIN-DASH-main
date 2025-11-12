"""Monthly report generation service."""

from typing import Dict, List
from datetime import datetime
from collections import defaultdict
from services.csv_manager import csv_manager
from services.budget_service import budget_service


class ReportService:
    """Service for generating financial reports."""

    def __init__(self):
        """Initialize report service."""
        pass

    def generate_monthly_report(self, year: int, month: int) -> Dict:
        """
        Generate comprehensive monthly financial report.

        Args:
            year: Report year
            month: Report month (1-12)

        Returns:
            Monthly report with income, expenses, categories, budget performance
        """
        # Load data
        transactions = csv_manager.read_csv("transactions.csv")
        categories = csv_manager.read_csv("categories.csv")
        budgets = csv_manager.read_csv("budgets.csv")

        # Filter transactions for the month
        month_transactions = [
            tx for tx in transactions if self._is_in_month(tx["date"], year, month)
        ]

        # Calculate income and expenses
        income = sum(
            float(tx["amount"]) for tx in month_transactions if float(tx["amount"]) > 0
        )
        expenses = abs(
            sum(
                float(tx["amount"])
                for tx in month_transactions
                if float(tx["amount"]) < 0
            )
        )
        net_income = income - expenses

        # Category breakdown
        category_spending = self._calculate_category_spending(
            month_transactions, categories
        )

        # Budget performance
        budget_performance = self._calculate_budget_performance(year, month, budgets)

        # Top spending categories
        top_categories = sorted(
            category_spending.items(), key=lambda x: x[1]["amount"], reverse=True
        )[:5]

        # Savings rate
        savings_rate = (net_income / income * 100) if income > 0 else 0

        # Transaction count
        transaction_count = len(month_transactions)
        income_count = sum(1 for tx in month_transactions if float(tx["amount"]) > 0)
        expense_count = sum(1 for tx in month_transactions if float(tx["amount"]) < 0)

        # Average transaction
        avg_expense = expenses / expense_count if expense_count > 0 else 0

        # Month-over-month comparison
        mom_comparison = self._calculate_mom_comparison(year, month, transactions)

        # Insights
        insights = self._generate_insights(
            income, expenses, savings_rate, budget_performance, category_spending
        )

        return {
            "year": year,
            "month": month,
            "period": f"{year}-{month:02d}",
            "summary": {
                "income": round(income, 2),
                "expenses": round(expenses, 2),
                "net_income": round(net_income, 2),
                "savings_rate": round(savings_rate, 2),
                "transaction_count": transaction_count,
                "income_count": income_count,
                "expense_count": expense_count,
                "avg_expense": round(avg_expense, 2),
            },
            "category_breakdown": category_spending,
            "top_categories": [
                {
                    "category_id": cat_id,
                    "category_name": data["name"],
                    "amount": round(data["amount"], 2),
                    "percentage": round(data["percentage"], 2),
                    "transaction_count": data["count"],
                }
                for cat_id, data in top_categories
            ],
            "budget_performance": budget_performance,
            "month_over_month": mom_comparison,
            "insights": insights,
        }

    def generate_ytd_summary(self, year: int) -> Dict:
        """
        Generate year-to-date summary.

        Args:
            year: Report year

        Returns:
            YTD summary
        """
        transactions = csv_manager.read_csv("transactions.csv")

        # Filter transactions for the year
        ytd_transactions = [
            tx for tx in transactions if tx["date"].startswith(str(year))
        ]

        # Calculate totals
        income = sum(
            float(tx["amount"]) for tx in ytd_transactions if float(tx["amount"]) > 0
        )
        expenses = abs(
            sum(
                float(tx["amount"])
                for tx in ytd_transactions
                if float(tx["amount"]) < 0
            )
        )
        net_income = income - expenses

        # Monthly breakdown
        monthly_data = defaultdict(lambda: {"income": 0, "expenses": 0})
        for tx in ytd_transactions:
            month = int(tx["date"].split("-")[1])
            amount = float(tx["amount"])
            if amount > 0:
                monthly_data[month]["income"] += amount
            else:
                monthly_data[month]["expenses"] += abs(amount)

        monthly_breakdown = [
            {
                "month": month,
                "income": round(data["income"], 2),
                "expenses": round(data["expenses"], 2),
                "net": round(data["income"] - data["expenses"], 2),
            }
            for month, data in sorted(monthly_data.items())
        ]

        return {
            "year": year,
            "summary": {
                "total_income": round(income, 2),
                "total_expenses": round(expenses, 2),
                "net_income": round(net_income, 2),
                "avg_monthly_income": round(income / 12, 2),
                "avg_monthly_expenses": round(expenses / 12, 2),
            },
            "monthly_breakdown": monthly_breakdown,
        }

    def _is_in_month(self, date_str: str, year: int, month: int) -> bool:
        """Check if date is in specified month."""
        try:
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return date.year == year and date.month == month
        except:
            return False

    def _calculate_category_spending(
        self, transactions: List[Dict], categories: List[Dict]
    ) -> Dict:
        """Calculate spending by category."""
        category_map = {cat["id"]: cat["name"] for cat in categories}
        category_totals = defaultdict(lambda: {"amount": 0, "count": 0})

        total_expenses = 0
        for tx in transactions:
            amount = float(tx["amount"])
            if amount < 0:  # Expenses only
                cat_id = tx["category_id"]
                category_totals[cat_id]["amount"] += abs(amount)
                category_totals[cat_id]["count"] += 1
                category_totals[cat_id]["name"] = category_map.get(cat_id, "Unknown")
                total_expenses += abs(amount)

        # Calculate percentages
        for cat_id, data in category_totals.items():
            data["percentage"] = (
                (data["amount"] / total_expenses * 100) if total_expenses > 0 else 0
            )

        return dict(category_totals)

    def _calculate_budget_performance(
        self, year: int, month: int, budgets: List[Dict]
    ) -> Dict:
        """Calculate budget vs actual performance."""
        # Find budget for the month
        budget = next(
            (b for b in budgets if int(b["year"]) == year and int(b["month"]) == month),
            None,
        )

        if not budget:
            return {"has_budget": False, "message": "No budget set for this month"}

        # Get budget status from budget service
        budget_status = budget_service.calculate_budget_status(budget["id"])

        return {
            "has_budget": True,
            "needs": {
                "planned": budget_status["needs_planned"],
                "actual": budget_status["needs_actual"],
                "variance": budget_status["needs_actual"]
                - budget_status["needs_planned"],
                "utilization": budget_status["needs_utilization"],
            },
            "wants": {
                "planned": budget_status["wants_planned"],
                "actual": budget_status["wants_actual"],
                "variance": budget_status["wants_actual"]
                - budget_status["wants_planned"],
                "utilization": budget_status["wants_utilization"],
            },
            "savings": {
                "planned": budget_status["savings_planned"],
                "actual": budget_status["savings_actual"],
                "variance": budget_status["savings_actual"]
                - budget_status["savings_planned"],
                "utilization": budget_status["savings_utilization"],
            },
            "total_utilization": budget_status["total_utilization"],
        }

    def _calculate_mom_comparison(
        self, year: int, month: int, transactions: List[Dict]
    ) -> Dict:
        """Calculate month-over-month comparison."""
        # Previous month
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1

        # Current month transactions
        current = [
            tx for tx in transactions if self._is_in_month(tx["date"], year, month)
        ]
        current_income = sum(
            float(tx["amount"]) for tx in current if float(tx["amount"]) > 0
        )
        current_expenses = abs(
            sum(float(tx["amount"]) for tx in current if float(tx["amount"]) < 0)
        )

        # Previous month transactions
        previous = [
            tx
            for tx in transactions
            if self._is_in_month(tx["date"], prev_year, prev_month)
        ]
        prev_income = sum(
            float(tx["amount"]) for tx in previous if float(tx["amount"]) > 0
        )
        prev_expenses = abs(
            sum(float(tx["amount"]) for tx in previous if float(tx["amount"]) < 0)
        )

        # Calculate changes
        income_change = (
            ((current_income - prev_income) / prev_income * 100)
            if prev_income > 0
            else 0
        )
        expense_change = (
            ((current_expenses - prev_expenses) / prev_expenses * 100)
            if prev_expenses > 0
            else 0
        )

        return {
            "income_change": round(income_change, 2),
            "expense_change": round(expense_change, 2),
            "previous_month": f"{prev_year}-{prev_month:02d}",
        }

    def _generate_insights(
        self,
        income: float,
        expenses: float,
        savings_rate: float,
        budget_performance: Dict,
        category_spending: Dict,
    ) -> List[str]:
        """Generate insights and recommendations."""
        insights = []

        # Savings rate insight
        if savings_rate >= 20:
            insights.append(
                f"Excellent! You're saving {savings_rate:.1f}% of your income."
            )
        elif savings_rate >= 10:
            insights.append(
                f"Good job! You're saving {savings_rate:.1f}% of your income. Try to reach 20%."
            )
        else:
            insights.append(
                f"Your savings rate is {savings_rate:.1f}%. Consider reducing expenses to save more."
            )

        # Budget performance insight
        if budget_performance.get("has_budget"):
            total_util = budget_performance.get("total_utilization", 0)
            if total_util > 100:
                insights.append(
                    f"You're {total_util - 100:.1f}% over budget this month. Review your spending."
                )
            elif total_util > 90:
                insights.append(
                    "You're close to your budget limit. Monitor spending carefully."
                )
            else:
                insights.append(
                    f"You're at {total_util:.1f}% of your budget. Great control!"
                )

        # Top spending category
        if category_spending:
            top_cat = max(category_spending.items(), key=lambda x: x[1]["amount"])
            insights.append(
                f"Your highest spending category is {top_cat[1]['name']} at R{top_cat[1]['amount']:.2f}."
            )

        return insights


# Global report service instance
report_service = ReportService()
