"""Debt management service with payoff calculators."""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from services.csv_manager import csv_manager


class DebtService:
    """Service for debt management and payoff calculations."""

    def __init__(self):
        """Initialize debt service."""
        self.debts: List[Dict] = []
        self._load_debts()

    def _load_debts(self):
        """Load debts from CSV."""
        try:
            self.debts = csv_manager.read_csv("debts.csv")
        except Exception:
            self.debts = []

    def get_total_debt(self) -> float:
        """Calculate total debt balance."""
        self._load_debts()
        return sum(float(debt.get("current_balance", 0)) for debt in self.debts)

    def get_minimum_payment(self) -> float:
        """Calculate total minimum monthly payment."""
        self._load_debts()
        return sum(float(debt.get("minimum_payment", 0)) for debt in self.debts)

    def calculate_debt_to_income_ratio(self, monthly_income: float) -> float:
        """
        Calculate debt-to-income ratio.

        Args:
            monthly_income: Monthly gross income

        Returns:
            Debt-to-income ratio as percentage
        """
        if monthly_income <= 0:
            return 0.0

        total_minimum = self.get_minimum_payment()
        return (total_minimum / monthly_income) * 100

    def calculate_avalanche_plan(self, extra_payment: float = 0) -> Dict:
        """
        Calculate debt payoff using Avalanche method (highest interest first).

        Args:
            extra_payment: Extra amount to pay beyond minimums each month

        Returns:
            Payoff plan with timeline and total interest
        """
        self._load_debts()

        # Filter active debts and sort by interest rate (highest first)
        active_debts = [
            {
                "id": d["id"],
                "name": d["name"],
                "balance": float(d["current_balance"]),
                "interest_rate": float(d["interest_rate"]),
                "minimum_payment": float(d["minimum_payment"]),
            }
            for d in self.debts
            if float(d["current_balance"]) > 0
        ]

        if not active_debts:
            return {
                "method": "avalanche",
                "total_months": 0,
                "total_interest": 0,
                "total_paid": 0,
                "debts": [],
                "monthly_schedule": [],
            }

        # Sort by interest rate (highest first)
        active_debts.sort(key=lambda x: x["interest_rate"], reverse=True)

        return self._calculate_payoff_schedule(active_debts, extra_payment, "avalanche")

    def calculate_snowball_plan(self, extra_payment: float = 0) -> Dict:
        """
        Calculate debt payoff using Snowball method (smallest balance first).

        Args:
            extra_payment: Extra amount to pay beyond minimums each month

        Returns:
            Payoff plan with timeline and total interest
        """
        self._load_debts()

        # Filter active debts and sort by balance (smallest first)
        active_debts = [
            {
                "id": d["id"],
                "name": d["name"],
                "balance": float(d["current_balance"]),
                "interest_rate": float(d["interest_rate"]),
                "minimum_payment": float(d["minimum_payment"]),
            }
            for d in self.debts
            if float(d["current_balance"]) > 0
        ]

        if not active_debts:
            return {
                "method": "snowball",
                "total_months": 0,
                "total_interest": 0,
                "total_paid": 0,
                "debts": [],
                "monthly_schedule": [],
            }

        # Sort by balance (smallest first)
        active_debts.sort(key=lambda x: x["balance"])

        return self._calculate_payoff_schedule(active_debts, extra_payment, "snowball")

    def _calculate_payoff_schedule(
        self, debts: List[Dict], extra_payment: float, method: str
    ) -> Dict:
        """
        Calculate detailed payoff schedule.

        Args:
            debts: List of debts sorted by priority
            extra_payment: Extra monthly payment
            method: 'avalanche' or 'snowball'

        Returns:
            Detailed payoff plan
        """
        # Create working copy of debts
        working_debts = [d.copy() for d in debts]

        total_interest = 0
        total_paid = 0
        month = 0
        monthly_schedule = []
        debt_payoff_months = {}

        # Calculate until all debts are paid
        while any(d["balance"] > 0 for d in working_debts):
            month += 1

            # Safety check to prevent infinite loops
            if month > 600:  # 50 years max
                break

            month_payment = 0
            month_interest = 0

            # Calculate interest and minimum payments for all debts
            for debt in working_debts:
                if debt["balance"] > 0:
                    # Calculate monthly interest
                    monthly_rate = debt["interest_rate"] / 100 / 12
                    interest = debt["balance"] * monthly_rate
                    month_interest += interest
                    total_interest += interest

                    # Add interest to balance
                    debt["balance"] += interest

            # Distribute payments
            available_payment = (
                sum(d["minimum_payment"] for d in working_debts if d["balance"] > 0)
                + extra_payment
            )

            # Pay minimums on all debts except the priority one
            for i, debt in enumerate(working_debts):
                if debt["balance"] > 0:
                    if i == 0:  # Priority debt gets extra payment
                        payment = min(debt["balance"], available_payment)
                    else:
                        payment = min(debt["balance"], debt["minimum_payment"])
                        available_payment -= payment

                    debt["balance"] -= payment
                    month_payment += payment
                    total_paid += payment

                    # Record when debt is paid off
                    if debt["balance"] <= 0:
                        debt["balance"] = 0
                        if debt["id"] not in debt_payoff_months:
                            debt_payoff_months[debt["id"]] = month
                        # Redistribute this debt's minimum to priority debt
                        available_payment += debt["minimum_payment"]

            # Record monthly snapshot
            monthly_schedule.append(
                {
                    "month": month,
                    "payment": round(month_payment, 2),
                    "interest": round(month_interest, 2),
                    "remaining_balance": round(
                        sum(d["balance"] for d in working_debts), 2
                    ),
                    "debts": [
                        {
                            "id": d["id"],
                            "name": d["name"],
                            "balance": round(d["balance"], 2),
                        }
                        for d in working_debts
                    ],
                }
            )

            # Remove paid-off debts from priority queue
            working_debts = [d for d in working_debts if d["balance"] > 0]

        # Build debt summary
        debt_summary = []
        for debt in debts:
            payoff_month = debt_payoff_months.get(debt["id"], 0)
            debt_summary.append(
                {
                    "id": debt["id"],
                    "name": debt["name"],
                    "original_balance": debt["balance"],
                    "interest_rate": debt["interest_rate"],
                    "payoff_month": payoff_month,
                    "payoff_date": (
                        (datetime.now() + timedelta(days=30 * payoff_month)).strftime(
                            "%Y-%m-%d"
                        )
                        if payoff_month > 0
                        else None
                    ),
                }
            )

        return {
            "method": method,
            "total_months": month,
            "total_interest": round(total_interest, 2),
            "total_paid": round(total_paid, 2),
            "payoff_date": (
                (datetime.now() + timedelta(days=30 * month)).strftime("%Y-%m-%d")
                if month > 0
                else None
            ),
            "debts": debt_summary,
            "monthly_schedule": monthly_schedule[:12],  # Return first year for preview
        }

    def compare_strategies(self, extra_payment: float = 0) -> Dict:
        """
        Compare Avalanche vs Snowball strategies.

        Args:
            extra_payment: Extra monthly payment

        Returns:
            Comparison of both strategies
        """
        avalanche = self.calculate_avalanche_plan(extra_payment)
        snowball = self.calculate_snowball_plan(extra_payment)

        # Calculate savings
        interest_savings = snowball["total_interest"] - avalanche["total_interest"]
        time_savings = snowball["total_months"] - avalanche["total_months"]

        return {
            "avalanche": avalanche,
            "snowball": snowball,
            "comparison": {
                "interest_savings": round(interest_savings, 2),
                "time_savings_months": time_savings,
                "recommended": "avalanche" if interest_savings > 0 else "snowball",
            },
        }


# Global debt service instance
debt_service = DebtService()
