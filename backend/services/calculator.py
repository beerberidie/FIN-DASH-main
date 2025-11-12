"""Financial calculation services."""

from typing import List, Dict, Any, Optional
from datetime import datetime, date as date_type
from collections import defaultdict


class Calculator:
    """Financial calculations for dashboard and reports."""

    @staticmethod
    def _convert_to_base_currency(
        amount: float,
        from_currency: str,
        base_currency: str,
        conversion_date: Optional[date_type] = None,
    ) -> float:
        """
        Convert an amount from one currency to base currency.

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            base_currency: Target base currency code
            conversion_date: Date for conversion (uses latest if None)

        Returns:
            Converted amount in base currency
        """
        # If same currency, no conversion needed
        if from_currency == base_currency:
            return amount

        # Import here to avoid circular dependency
        from services.currency_service import currency_service
        from models.currency import CurrencyConversion

        try:
            conversion = CurrencyConversion(
                amount=abs(amount),  # Use absolute value for conversion
                from_currency=from_currency,
                to_currency=base_currency,
                date=conversion_date,
            )
            result = currency_service.convert_currency(conversion)
            # Preserve the sign of the original amount
            return result.converted_amount if amount >= 0 else -result.converted_amount
        except Exception:
            # If conversion fails, return original amount
            # This ensures backward compatibility
            return amount

    @staticmethod
    def calculate_account_balance(
        account_id: str,
        transactions: List[Dict],
        opening_balance: float,
        base_currency: str = "ZAR",
    ) -> float:
        """
        Calculate current balance for an account.

        Args:
            account_id: Account ID
            transactions: List of all transactions
            opening_balance: Opening balance of the account
            base_currency: Base currency for conversion (default: ZAR)

        Returns:
            Current balance in base currency
        """
        balance = opening_balance

        for tx in transactions:
            if tx.get("account_id") == account_id:
                amount = float(tx.get("amount", 0))
                tx_currency = tx.get("currency", "ZAR")

                # Convert to base currency if needed
                converted_amount = Calculator._convert_to_base_currency(
                    amount, tx_currency, base_currency
                )
                balance += converted_amount

        return balance

    @staticmethod
    def calculate_total_balance(
        accounts: List[Dict], transactions: List[Dict], base_currency: str = "ZAR"
    ) -> float:
        """
        Calculate total balance across all active accounts.

        Args:
            accounts: List of all accounts
            transactions: List of all transactions
            base_currency: Base currency for conversion (default: ZAR)

        Returns:
            Total balance in base currency
        """
        total = 0.0

        for account in accounts:
            if account.get("is_active", "true").lower() == "true":
                opening = float(account.get("opening_balance", 0))
                balance = Calculator.calculate_account_balance(
                    account["id"], transactions, opening, base_currency
                )
                total += balance

        return total

    @staticmethod
    def calculate_monthly_totals(
        month: str, transactions: List[Dict], base_currency: str = "ZAR"
    ) -> Dict[str, float]:
        """
        Calculate income and expenses for a specific month.

        Args:
            month: Month in YYYY-MM format
            transactions: List of all transactions
            base_currency: Base currency for conversion (default: ZAR)

        Returns:
            Dictionary with 'income' and 'expenses' totals in base currency
        """
        income = 0.0
        expenses = 0.0

        for tx in transactions:
            tx_date = tx.get("date", "")
            if tx_date.startswith(month):
                amount = float(tx.get("amount", 0))
                tx_currency = tx.get("currency", "ZAR")

                # Convert to base currency
                converted_amount = Calculator._convert_to_base_currency(
                    amount, tx_currency, base_currency
                )

                if converted_amount > 0:
                    income += converted_amount
                else:
                    expenses += abs(converted_amount)

        return {"income": income, "expenses": expenses, "net": income - expenses}

    @staticmethod
    def calculate_savings_rate(income: float, expenses: float) -> float:
        """
        Calculate savings rate as percentage.

        Args:
            income: Total income
            expenses: Total expenses

        Returns:
            Savings rate percentage (0-100)
        """
        if income == 0:
            return 0.0

        savings = income - expenses
        return (savings / income) * 100

    @staticmethod
    def calculate_category_spending(
        category_id: str,
        month: str,
        transactions: List[Dict],
        base_currency: str = "ZAR",
    ) -> float:
        """
        Calculate total spending for a category in a month.

        Args:
            category_id: Category ID
            month: Month in YYYY-MM format
            transactions: List of all transactions
            base_currency: Base currency for conversion (default: ZAR)

        Returns:
            Total spending (positive number) in base currency
        """
        total = 0.0

        for tx in transactions:
            if tx.get("category_id") == category_id and tx.get("date", "").startswith(
                month
            ):
                amount = float(tx.get("amount", 0))
                tx_currency = tx.get("currency", "ZAR")

                if amount < 0:  # Expense
                    # Convert to base currency
                    converted_amount = Calculator._convert_to_base_currency(
                        amount, tx_currency, base_currency
                    )
                    total += abs(converted_amount)

        return total

    @staticmethod
    def calculate_net_worth(total_balance: float, debts: List[Dict]) -> float:
        """
        Calculate net worth (assets - liabilities).

        Args:
            total_balance: Total account balance
            debts: List of all debts

        Returns:
            Net worth
        """
        total_debt = sum(float(debt.get("current_balance", 0)) for debt in debts)
        return total_balance - total_debt

    @staticmethod
    def calculate_month_over_month_change(
        current_month: str, transactions: List[Dict], base_currency: str = "ZAR"
    ) -> Dict[str, float]:
        """
        Calculate month-over-month changes.

        Args:
            current_month: Current month in YYYY-MM format
            transactions: List of all transactions
            base_currency: Base currency for conversion (default: ZAR)

        Returns:
            Dictionary with percentage changes
        """
        # Parse current month
        year, month = map(int, current_month.split("-"))

        # Calculate previous month
        if month == 1:
            prev_month = f"{year - 1}-12"
        else:
            prev_month = f"{year}-{month - 1:02d}"

        current = Calculator.calculate_monthly_totals(
            current_month, transactions, base_currency
        )
        previous = Calculator.calculate_monthly_totals(
            prev_month, transactions, base_currency
        )

        def calc_change(current_val: float, prev_val: float) -> float:
            if prev_val == 0:
                return 0.0 if current_val == 0 else 100.0
            return ((current_val - prev_val) / prev_val) * 100

        return {
            "income_change": calc_change(current["income"], previous["income"]),
            "expenses_change": calc_change(current["expenses"], previous["expenses"]),
            "net_change": calc_change(current["net"], previous["net"]),
        }

    @staticmethod
    def calculate_spending_by_group(
        month: str,
        transactions: List[Dict],
        categories: List[Dict],
        base_currency: str = "ZAR",
    ) -> Dict[str, float]:
        """
        Calculate spending grouped by category group (needs/wants/savings/debt).

        Args:
            month: Month in YYYY-MM format
            transactions: List of all transactions
            categories: List of all categories
            base_currency: Base currency for conversion (default: ZAR)

        Returns:
            Dictionary with spending by group in base currency
        """
        # Create category lookup
        category_map = {cat["id"]: cat for cat in categories}

        # Group spending
        group_totals = defaultdict(float)

        for tx in transactions:
            if tx.get("date", "").startswith(month):
                amount = float(tx.get("amount", 0))
                tx_currency = tx.get("currency", "ZAR")

                if amount < 0:  # Expense
                    cat_id = tx.get("category_id")
                    if cat_id and cat_id in category_map:
                        group = category_map[cat_id].get("group", "other")
                        # Convert to base currency
                        converted_amount = Calculator._convert_to_base_currency(
                            amount, tx_currency, base_currency
                        )
                        group_totals[group] += abs(converted_amount)

        return dict(group_totals)


# Singleton instance
calculator = Calculator()
