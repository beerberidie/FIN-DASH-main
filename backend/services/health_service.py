"""Financial health scoring service."""

from datetime import datetime, date as date_type, timedelta
from typing import List, Optional
import statistics

from models.analytics import FinancialHealthScore, HealthMetric, HealthMetricBreakdown
from models.currency import CurrencyConversion
from services.csv_manager import csv_manager
from services.calculator import calculator
from services.currency_service import currency_service
from services.debt_service import debt_service
from services.portfolio_service import portfolio_service
from utils.dates import now_iso


class HealthService:
    """Service for calculating financial health scores."""

    def __init__(self):
        """Initialize health service."""
        pass

    def _convert_amount(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
        conversion_date: date_type,
    ) -> float:
        """
        Helper method to convert amount between currencies.

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            conversion_date: Date for exchange rate lookup

        Returns:
            Converted amount
        """
        if from_currency == to_currency:
            return amount

        conversion = CurrencyConversion(
            amount=amount,
            from_currency=from_currency,
            to_currency=to_currency,
            date=conversion_date,
        )
        result = currency_service.convert_currency(conversion)
        return result.converted_amount

    def calculate_health_score(
        self,
        include_investments: bool = True,
        include_debts: bool = True,
        reference_date: Optional[date_type] = None,
        base_currency: str = "ZAR",
    ) -> FinancialHealthScore:
        """
        Calculate comprehensive financial health score.

        Args:
            include_investments: Include investment metrics
            include_debts: Include debt metrics
            reference_date: Reference date for calculations
            base_currency: Base currency for conversions

        Returns:
            FinancialHealthScore with overall score and recommendations
        """
        if reference_date is None:
            reference_date = date_type.today()

        # Calculate individual metrics
        metrics = []

        # 1. Savings Rate (20 points)
        savings_metric = self._calculate_savings_rate_metric(
            reference_date, base_currency
        )
        metrics.append(savings_metric)

        # 2. Emergency Fund (20 points)
        emergency_metric = self._calculate_emergency_fund_metric(base_currency)
        metrics.append(emergency_metric)

        # 3. Debt-to-Income Ratio (20 points)
        if include_debts:
            debt_metric = self._calculate_debt_metric(reference_date, base_currency)
            metrics.append(debt_metric)

        # 4. Budget Adherence (15 points)
        budget_metric = self._calculate_budget_adherence_metric(
            reference_date, base_currency
        )
        metrics.append(budget_metric)

        # 5. Net Worth Trend (15 points)
        networth_metric = self._calculate_networth_trend_metric(base_currency)
        metrics.append(networth_metric)

        # 6. Investment Diversification (10 points)
        if include_investments:
            investment_metric = self._calculate_investment_metric()
            metrics.append(investment_metric)

        # Calculate overall score
        total_possible = sum(self._get_metric_weight(m.name) for m in metrics)
        total_score = sum(
            m.score * self._get_metric_weight(m.name) / 100 for m in metrics
        )
        overall_score = (
            (total_score / total_possible * 100) if total_possible > 0 else 0
        )

        # Determine overall status
        overall_status = self._get_status_from_score(overall_score)

        # Identify strengths and weaknesses
        strengths = [m.name for m in metrics if m.score >= 80]
        weaknesses = [m.name for m in metrics if m.score < 60]

        # Generate recommendations
        recommendations = []
        for metric in metrics:
            if metric.recommendation:
                recommendations.append(metric.recommendation)

        return FinancialHealthScore(
            overall_score=round(overall_score, 1),
            overall_status=overall_status,
            metrics=metrics,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            calculated_at=now_iso(),
        )

    def get_health_breakdown(
        self, reference_date: Optional[date_type] = None, base_currency: str = "ZAR"
    ) -> HealthMetricBreakdown:
        """
        Get detailed breakdown of health metrics.

        Args:
            reference_date: Reference date for calculations
            base_currency: Base currency for conversions

        Returns:
            HealthMetricBreakdown with detailed metrics
        """
        if reference_date is None:
            reference_date = date_type.today()

        # Calculate savings rate
        savings_rate = self._get_savings_rate(reference_date, base_currency)

        # Calculate debt-to-income ratio
        debt_to_income = self._get_debt_to_income_ratio(reference_date, base_currency)

        # Calculate emergency fund months
        emergency_fund_months = self._get_emergency_fund_months(base_currency)

        # Calculate budget adherence
        budget_adherence = self._get_budget_adherence(reference_date, base_currency)

        # Calculate investment diversification
        investment_diversification = self._get_investment_diversification()

        # Calculate net worth trend
        net_worth_trend = self._get_networth_trend(base_currency)

        return HealthMetricBreakdown(
            savings_rate=savings_rate,
            debt_to_income=debt_to_income,
            emergency_fund_months=emergency_fund_months,
            budget_adherence=budget_adherence,
            investment_diversification=investment_diversification,
            net_worth_trend=net_worth_trend,
        )

    # Metric calculation methods

    def _calculate_savings_rate_metric(
        self, reference_date: date_type, base_currency: str
    ) -> HealthMetric:
        """Calculate savings rate metric."""
        savings_rate = self._get_savings_rate(reference_date, base_currency)

        # Score based on savings rate
        if savings_rate >= 20:
            score = 100
            status = "excellent"
            recommendation = None
        elif savings_rate >= 15:
            score = 85
            status = "good"
            recommendation = "Try to increase your savings rate to 20% or more for optimal financial health."
        elif savings_rate >= 10:
            score = 70
            status = "fair"
            recommendation = "Aim to save at least 15% of your income. Review expenses to find savings opportunities."
        elif savings_rate >= 5:
            score = 50
            status = "poor"
            recommendation = "Your savings rate is low. Create a budget and identify areas to cut expenses."
        else:
            score = 25
            status = "poor"
            recommendation = "Critical: You're saving very little. Urgently review your spending and create a savings plan."

        return HealthMetric(
            name="Savings Rate",
            score=score,
            status=status,
            description=f"You're saving {savings_rate:.1f}% of your income",
            recommendation=recommendation,
        )

    def _calculate_emergency_fund_metric(self, base_currency: str) -> HealthMetric:
        """Calculate emergency fund metric."""
        months = self._get_emergency_fund_months(base_currency)

        # Score based on months of expenses
        if months >= 6:
            score = 100
            status = "excellent"
            recommendation = None
        elif months >= 3:
            score = 75
            status = "good"
            recommendation = "Build your emergency fund to cover 6 months of expenses for better security."
        elif months >= 1:
            score = 50
            status = "fair"
            recommendation = (
                "Increase your emergency fund to at least 3 months of expenses."
            )
        else:
            score = 25
            status = "poor"
            recommendation = "Critical: Build an emergency fund covering at least 1 month of expenses immediately."

        return HealthMetric(
            name="Emergency Fund",
            score=score,
            status=status,
            description=f"Your emergency fund covers {months:.1f} months of expenses",
            recommendation=recommendation,
        )

    def _calculate_debt_metric(
        self, reference_date: date_type, base_currency: str
    ) -> HealthMetric:
        """Calculate debt-to-income metric."""
        ratio = self._get_debt_to_income_ratio(reference_date, base_currency)

        # Score based on debt-to-income ratio
        if ratio <= 0:
            score = 100
            status = "excellent"
            recommendation = None
        elif ratio <= 20:
            score = 90
            status = "excellent"
            recommendation = None
        elif ratio <= 36:
            score = 75
            status = "good"
            recommendation = "Your debt level is manageable. Consider paying down high-interest debt faster."
        elif ratio <= 50:
            score = 50
            status = "fair"
            recommendation = (
                "Your debt-to-income ratio is high. Focus on debt reduction strategies."
            )
        else:
            score = 25
            status = "poor"
            recommendation = "Critical: Your debt level is very high. Seek debt counseling and create a repayment plan."

        return HealthMetric(
            name="Debt-to-Income Ratio",
            score=score,
            status=status,
            description=f"Your debt payments are {ratio:.1f}% of your income",
            recommendation=recommendation,
        )

    def _calculate_budget_adherence_metric(
        self, reference_date: date_type, base_currency: str
    ) -> HealthMetric:
        """Calculate budget adherence metric."""
        adherence = self._get_budget_adherence(reference_date, base_currency)

        # Score based on budget adherence
        if adherence >= 95:
            score = 100
            status = "excellent"
            recommendation = None
        elif adherence >= 85:
            score = 85
            status = "good"
            recommendation = (
                "Good budget discipline. Fine-tune your budget for even better results."
            )
        elif adherence >= 70:
            score = 70
            status = "fair"
            recommendation = (
                "Review your budget regularly and track spending more closely."
            )
        else:
            score = 50
            status = "poor"
            recommendation = (
                "Improve budget tracking and adjust budgets to be more realistic."
            )

        return HealthMetric(
            name="Budget Adherence",
            score=score,
            status=status,
            description=f"You're staying within budget {adherence:.1f}% of the time",
            recommendation=recommendation,
        )

    def _calculate_networth_trend_metric(self, base_currency: str) -> HealthMetric:
        """Calculate net worth trend metric."""
        trend = self._get_networth_trend(base_currency)

        # Score based on trend
        if trend == "increasing":
            score = 100
            status = "excellent"
            recommendation = None
        elif trend == "stable":
            score = 70
            status = "good"
            recommendation = "Your net worth is stable. Look for opportunities to increase income or reduce expenses."
        else:
            score = 40
            status = "poor"
            recommendation = "Your net worth is declining. Review your spending and income sources urgently."

        return HealthMetric(
            name="Net Worth Trend",
            score=score,
            status=status,
            description=f"Your net worth is {trend}",
            recommendation=recommendation,
        )

    def _calculate_investment_metric(self) -> HealthMetric:
        """Calculate investment diversification metric."""
        diversification = self._get_investment_diversification()

        # Score based on diversification
        if diversification >= 80:
            score = 100
            status = "excellent"
            recommendation = None
        elif diversification >= 60:
            score = 80
            status = "good"
            recommendation = "Consider diversifying across more asset types for better risk management."
        elif diversification >= 40:
            score = 60
            status = "fair"
            recommendation = (
                "Improve diversification by investing in different asset classes."
            )
        else:
            score = 40
            status = "poor"
            recommendation = "Your portfolio lacks diversification. Spread investments across multiple asset types."

        return HealthMetric(
            name="Investment Diversification",
            score=score,
            status=status,
            description=f"Your portfolio diversification score is {diversification:.1f}",
            recommendation=recommendation,
        )

    # Helper methods

    def _get_metric_weight(self, metric_name: str) -> float:
        """Get weight for a metric."""
        weights = {
            "Savings Rate": 20,
            "Emergency Fund": 20,
            "Debt-to-Income Ratio": 20,
            "Budget Adherence": 15,
            "Net Worth Trend": 15,
            "Investment Diversification": 10,
        }
        return weights.get(metric_name, 10)

    def _get_status_from_score(self, score: float) -> str:
        """Get status label from score."""
        if score >= 85:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 50:
            return "fair"
        else:
            return "poor"

    def _get_savings_rate(self, reference_date: date_type, base_currency: str) -> float:
        """Calculate savings rate for the last 3 months."""
        end_date = reference_date
        start_date = end_date - timedelta(days=90)

        transactions = csv_manager.read_csv("transactions.csv")

        income = 0
        expenses = 0

        for txn in transactions:
            date_str = txn.get("date", "")
            if not date_str:
                continue

            txn_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if txn_date < start_date or txn_date > end_date:
                continue

            amount = abs(float(txn.get("amount", 0)))

            # Convert to base currency
            txn_currency = txn.get("currency", base_currency)
            if txn_currency != base_currency:
                amount = self._convert_amount(
                    amount, txn_currency, base_currency, txn_date
                )

            if txn.get("type") == "income":
                income += amount
            elif txn.get("type") == "expense":
                expenses += amount

        if income == 0:
            return 0

        savings = income - expenses
        savings_rate = (savings / income) * 100

        return max(0, savings_rate)

    def _get_emergency_fund_months(self, base_currency: str) -> float:
        """Calculate months of expenses covered by emergency fund."""
        # Get current balance
        accounts = csv_manager.read_csv("accounts.csv")
        transactions = csv_manager.read_csv("transactions.csv")
        total_balance = calculator.calculate_total_balance(
            accounts, transactions, base_currency
        )

        # Get average monthly expenses (last 3 months)
        end_date = date_type.today()
        start_date = end_date - timedelta(days=90)

        transactions = csv_manager.read_csv("transactions.csv")

        total_expenses = 0

        for txn in transactions:
            date_str = txn.get("date", "")
            if not date_str:
                continue

            txn_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if txn_date < start_date or txn_date > end_date:
                continue

            if txn.get("type") == "expense":
                amount = abs(float(txn.get("amount", 0)))

                # Convert to base currency
                txn_currency = txn.get("currency", base_currency)
                if txn_currency != base_currency:
                    amount = self._convert_amount(
                        amount, txn_currency, base_currency, txn_date
                    )

                total_expenses += amount

        # Calculate average monthly expenses
        avg_monthly_expenses = total_expenses / 3

        if avg_monthly_expenses == 0:
            return 0

        months = total_balance / avg_monthly_expenses
        return max(0, months)

    def _get_debt_to_income_ratio(
        self, reference_date: date_type, base_currency: str
    ) -> float:
        """Calculate debt-to-income ratio."""
        # Get monthly income (last 3 months average)
        end_date = reference_date
        start_date = end_date - timedelta(days=90)

        transactions = csv_manager.read_csv("transactions.csv")

        total_income = 0

        for txn in transactions:
            date_str = txn.get("date", "")
            if not date_str:
                continue

            txn_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if txn_date < start_date or txn_date > end_date:
                continue

            if txn.get("type") == "income":
                amount = abs(float(txn.get("amount", 0)))

                # Convert to base currency
                txn_currency = txn.get("currency", base_currency)
                if txn_currency != base_currency:
                    amount = self._convert_amount(
                        amount, txn_currency, base_currency, txn_date
                    )

                total_income += amount

        avg_monthly_income = total_income / 3

        if avg_monthly_income == 0:
            return 0

        # Get total debt payments
        try:
            debts = debt_service.list_debts()
            total_monthly_payment = sum(
                debt.minimum_payment for debt in debts if not debt.is_paid_off
            )
        except:
            total_monthly_payment = 0

        ratio = (total_monthly_payment / avg_monthly_income) * 100
        return ratio

    def _get_budget_adherence(
        self, reference_date: date_type, base_currency: str
    ) -> float:
        """Calculate budget adherence percentage."""
        # Get current month budgets
        budgets = csv_manager.read_csv("budgets.csv")

        if not budgets:
            return 100  # No budgets set, assume perfect adherence

        # Get current month transactions
        current_month = reference_date.strftime("%Y-%m")
        transactions = csv_manager.read_csv("transactions.csv")

        # Calculate spending by category
        category_spending = {}
        for txn in transactions:
            if not txn.get("date", "").startswith(current_month):
                continue

            if txn.get("type") != "expense":
                continue

            category_id = txn.get("category_id", "")
            amount = abs(float(txn.get("amount", 0)))

            # Convert to base currency
            txn_currency = txn.get("currency", base_currency)
            if txn_currency != base_currency:
                txn_date = datetime.strptime(txn.get("date", ""), "%Y-%m-%d").date()
                amount = self._convert_amount(
                    amount, txn_currency, base_currency, txn_date
                )

            category_spending[category_id] = (
                category_spending.get(category_id, 0) + amount
            )

        # Check adherence
        within_budget_count = 0
        total_budgets = 0

        for budget in budgets:
            category_id = budget.get("category_id", "")
            budget_amount = float(budget.get("amount", 0))
            spent = category_spending.get(category_id, 0)

            total_budgets += 1
            if spent <= budget_amount:
                within_budget_count += 1

        if total_budgets == 0:
            return 100

        adherence = (within_budget_count / total_budgets) * 100
        return adherence

    def _get_networth_trend(self, base_currency: str) -> str:
        """Calculate net worth trend."""
        # Get net worth for last 3 months
        today = date_type.today()

        networth_values = []
        for months_ago in [2, 1, 0]:
            ref_date = today - timedelta(days=months_ago * 30)

            # Calculate net worth at that point
            accounts = csv_manager.read_csv("accounts.csv")
            transactions = csv_manager.read_csv("transactions.csv")
            debts = csv_manager.read_csv("debts.csv")
            total_balance = calculator.calculate_total_balance(
                accounts, transactions, base_currency
            )
            networth = calculator.calculate_net_worth(total_balance, debts)
            networth_values.append(networth)

        # Determine trend
        if len(networth_values) < 2:
            return "stable"

        # Calculate average change
        changes = [
            networth_values[i + 1] - networth_values[i]
            for i in range(len(networth_values) - 1)
        ]
        avg_change = sum(changes) / len(changes)

        if avg_change > 0:
            return "increasing"
        elif avg_change < 0:
            return "decreasing"
        else:
            return "stable"

    def _get_investment_diversification(self) -> float:
        """Calculate investment diversification score."""
        try:
            # Get portfolio summary
            portfolio = portfolio_service.get_portfolio_summary("ZAR")

            if portfolio.total_investments == 0:
                return 0

            # Get asset allocation
            allocation = portfolio_service.get_asset_allocation("ZAR")

            # Calculate diversification score based on number of asset types
            # and balance across them
            num_types = len(allocation)

            if num_types == 0:
                return 0
            elif num_types == 1:
                return 30
            elif num_types == 2:
                return 50
            elif num_types == 3:
                return 70
            elif num_types >= 4:
                # Check balance
                percentages = [item["percentage"] for item in allocation]
                max_pct = max(percentages)

                if max_pct > 70:
                    return 75
                elif max_pct > 50:
                    return 85
                else:
                    return 95

            return 50
        except:
            return 0


# Singleton instance
health_service = HealthService()
