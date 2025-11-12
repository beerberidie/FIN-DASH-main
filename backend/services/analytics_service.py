"""Analytics service for trend analysis, YoY comparisons, and pattern detection."""

from datetime import datetime, date as date_type, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
import statistics

from models.analytics import (
    TrendAnalysis,
    TrendDataPoint,
    YoYReport,
    YoYComparison,
    SpendingPattern,
    CategoryInsight,
    CustomReport,
    DrillDownResult,
)
from models.currency import CurrencyConversion
from services.csv_manager import csv_manager
from services.currency_service import currency_service


class AnalyticsService:
    """Service for advanced analytics and reporting."""

    def __init__(self):
        """Initialize analytics service."""
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

    def get_trend_analysis(
        self,
        metric: str,
        period_type: str = "monthly",
        start_date: Optional[date_type] = None,
        end_date: Optional[date_type] = None,
        category_id: Optional[str] = None,
        base_currency: str = "ZAR",
    ) -> TrendAnalysis:
        """
        Get trend analysis for a metric over time.

        Args:
            metric: Metric to analyze (income, expenses, net)
            period_type: Period type (monthly, quarterly, yearly)
            start_date: Start date filter
            end_date: End date filter
            category_id: Category ID for category-specific trends
            base_currency: Base currency for conversions

        Returns:
            TrendAnalysis with data points and trend direction
        """
        # Load transactions
        transactions = csv_manager.read_csv("transactions.csv")

        # Filter transactions
        filtered = self._filter_transactions(
            transactions, start_date, end_date, category_id
        )

        # Group by period
        period_data = self._group_by_period(
            filtered, period_type, metric, base_currency
        )

        # Create data points
        data_points = []
        for period, value in sorted(period_data.items()):
            data_points.append(
                TrendDataPoint(
                    period=period, value=value["total"], count=value["count"]
                )
            )

        # Calculate statistics
        values = [dp.value for dp in data_points]
        average = statistics.mean(values) if values else 0
        total = sum(values)

        # Determine trend direction
        trend_direction, trend_percentage = self._calculate_trend(values)

        return TrendAnalysis(
            metric=metric,
            period_type=period_type,
            data_points=data_points,
            average=average,
            total=total,
            trend_direction=trend_direction,
            trend_percentage=trend_percentage,
        )

    def get_yoy_comparison(
        self, current_year: Optional[int] = None, base_currency: str = "ZAR"
    ) -> YoYReport:
        """
        Get year-over-year comparison report.

        Args:
            current_year: Year to compare (defaults to current year)
            base_currency: Base currency for conversions

        Returns:
            YoYReport with comparisons
        """
        if current_year is None:
            current_year = datetime.now().year

        previous_year = current_year - 1

        # Load transactions
        transactions = csv_manager.read_csv("transactions.csv")

        # Calculate metrics for both years
        current_metrics = self._calculate_year_metrics(
            transactions, current_year, base_currency
        )
        previous_metrics = self._calculate_year_metrics(
            transactions, previous_year, base_currency
        )

        # Create comparisons
        income_comparison = self._create_yoy_comparison(
            "income",
            current_year,
            current_metrics["income"],
            previous_year,
            previous_metrics["income"],
            is_income=True,
        )

        expense_comparison = self._create_yoy_comparison(
            "expenses",
            current_year,
            current_metrics["expenses"],
            previous_year,
            previous_metrics["expenses"],
            is_income=False,
        )

        net_comparison = self._create_yoy_comparison(
            "net_income",
            current_year,
            current_metrics["net"],
            previous_year,
            previous_metrics["net"],
            is_income=True,
        )

        # Calculate savings rates
        savings_rate_current = (
            (current_metrics["net"] / current_metrics["income"] * 100)
            if current_metrics["income"] > 0
            else 0
        )
        savings_rate_previous = (
            (previous_metrics["net"] / previous_metrics["income"] * 100)
            if previous_metrics["income"] > 0
            else 0
        )

        # Category comparisons
        category_comparisons = self._get_category_comparisons(
            transactions, current_year, previous_year, base_currency
        )

        return YoYReport(
            current_year=current_year,
            previous_year=previous_year,
            income_comparison=income_comparison,
            expense_comparison=expense_comparison,
            net_comparison=net_comparison,
            savings_rate_current=savings_rate_current,
            savings_rate_previous=savings_rate_previous,
            category_comparisons=category_comparisons,
        )

    def detect_spending_patterns(
        self,
        start_date: Optional[date_type] = None,
        end_date: Optional[date_type] = None,
        base_currency: str = "ZAR",
    ) -> List[SpendingPattern]:
        """
        Detect spending patterns across categories.

        Args:
            start_date: Start date filter
            end_date: End date filter
            base_currency: Base currency for conversions

        Returns:
            List of detected spending patterns
        """
        # Load data
        transactions = csv_manager.read_csv("transactions.csv")
        categories = csv_manager.read_csv("categories.csv")
        category_map = {cat["id"]: cat["name"] for cat in categories}

        # Filter transactions
        filtered = self._filter_transactions(transactions, start_date, end_date)

        # Group by category
        category_data = defaultdict(list)
        for txn in filtered:
            if txn.get("type") == "expense":
                category_id = txn.get("category_id", "")
                amount = abs(float(txn.get("amount", 0)))

                # Convert to base currency
                txn_currency = txn.get("currency", base_currency)
                if txn_currency != base_currency:
                    txn_date = datetime.strptime(txn.get("date", ""), "%Y-%m-%d").date()
                    amount = self._convert_amount(
                        amount, txn_currency, base_currency, txn_date
                    )

                category_data[category_id].append(
                    {"amount": amount, "date": txn.get("date", "")}
                )

        # Detect patterns for each category
        patterns = []
        for category_id, txns in category_data.items():
            if len(txns) < 3:  # Need at least 3 transactions to detect pattern
                continue

            pattern = self._detect_category_pattern(
                category_id, category_map.get(category_id, "Unknown"), txns
            )
            if pattern:
                patterns.append(pattern)

        return patterns

    def get_category_insights(
        self,
        category_id: str,
        start_date: Optional[date_type] = None,
        end_date: Optional[date_type] = None,
        base_currency: str = "ZAR",
    ) -> CategoryInsight:
        """
        Get deep-dive insights for a specific category.

        Args:
            category_id: Category ID to analyze
            start_date: Start date filter
            end_date: End date filter
            base_currency: Base currency for conversions

        Returns:
            CategoryInsight with detailed breakdown
        """
        # Load data
        transactions = csv_manager.read_csv("transactions.csv")
        categories = csv_manager.read_csv("categories.csv")
        category_map = {cat["id"]: cat["name"] for cat in categories}

        # Filter transactions for this category
        filtered = [
            txn
            for txn in transactions
            if txn.get("category_id") == category_id
            and (not start_date or txn.get("date", "") >= str(start_date))
            and (not end_date or txn.get("date", "") <= str(end_date))
        ]

        if not filtered:
            return CategoryInsight(
                category_id=category_id,
                category_name=category_map.get(category_id, "Unknown"),
                total_spent=0,
                transaction_count=0,
                average_transaction=0,
                percentage_of_total=0,
                trend="stable",
            )

        # Calculate metrics
        total_spent = 0
        merchants = defaultdict(int)
        monthly_data = defaultdict(float)

        for txn in filtered:
            amount = abs(float(txn.get("amount", 0)))

            # Convert to base currency
            txn_currency = txn.get("currency", base_currency)
            if txn_currency != base_currency:
                txn_date = datetime.strptime(txn.get("date", ""), "%Y-%m-%d").date()
                amount = self._convert_amount(
                    amount, txn_currency, base_currency, txn_date
                )

            total_spent += amount

            # Track merchants
            description = txn.get("description", "Unknown")
            merchants[description] += 1

            # Track monthly spending
            month = txn.get("date", "")[:7]  # YYYY-MM
            monthly_data[month] += amount

        transaction_count = len(filtered)
        average_transaction = (
            total_spent / transaction_count if transaction_count > 0 else 0
        )

        # Get top merchants
        top_merchants = sorted(merchants.items(), key=lambda x: x[1], reverse=True)[:5]
        top_merchants = [merchant for merchant, _ in top_merchants]

        # Calculate percentage of total
        all_expenses = [
            txn
            for txn in transactions
            if txn.get("type") == "expense"
            and (not start_date or txn.get("date", "") >= str(start_date))
            and (not end_date or txn.get("date", "") <= str(end_date))
        ]
        total_expenses = sum(abs(float(txn.get("amount", 0))) for txn in all_expenses)
        percentage_of_total = (
            (total_spent / total_expenses * 100) if total_expenses > 0 else 0
        )

        # Monthly breakdown
        monthly_breakdown = [
            TrendDataPoint(period=month, value=amount, count=0)
            for month, amount in sorted(monthly_data.items())
        ]

        # Determine trend
        monthly_values = [dp.value for dp in monthly_breakdown]
        trend_direction, _ = self._calculate_trend(monthly_values)

        return CategoryInsight(
            category_id=category_id,
            category_name=category_map.get(category_id, "Unknown"),
            total_spent=total_spent,
            transaction_count=transaction_count,
            average_transaction=average_transaction,
            percentage_of_total=percentage_of_total,
            trend=trend_direction,
            top_merchants=top_merchants,
            monthly_breakdown=monthly_breakdown,
        )

    # Helper methods

    def _filter_transactions(
        self,
        transactions: List[Dict],
        start_date: Optional[date_type],
        end_date: Optional[date_type],
        category_id: Optional[str] = None,
    ) -> List[Dict]:
        """Filter transactions by date and category."""
        filtered = []
        for txn in transactions:
            # Date filter
            if start_date and txn.get("date", "") < str(start_date):
                continue
            if end_date and txn.get("date", "") > str(end_date):
                continue

            # Category filter
            if category_id and txn.get("category_id") != category_id:
                continue

            filtered.append(txn)

        return filtered

    def _group_by_period(
        self,
        transactions: List[Dict],
        period_type: str,
        metric: str,
        base_currency: str,
    ) -> Dict[str, Dict[str, Any]]:
        """Group transactions by period and calculate metric."""
        period_data = defaultdict(lambda: {"total": 0, "count": 0})

        for txn in transactions:
            # Get period key
            date_str = txn.get("date", "")
            if not date_str:
                continue

            period_key = self._get_period_key(date_str, period_type)

            # Calculate value based on metric
            amount = float(txn.get("amount", 0))
            txn_type = txn.get("type", "")

            # Convert to base currency
            txn_currency = txn.get("currency", base_currency)
            if txn_currency != base_currency:
                txn_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                amount = self._convert_amount(
                    abs(amount), txn_currency, base_currency, txn_date
                )
                # Restore sign
                if txn_type == "expense":
                    amount = -abs(amount)
                else:
                    amount = abs(amount)

            if metric == "income" and txn_type == "income":
                period_data[period_key]["total"] += abs(amount)
                period_data[period_key]["count"] += 1
            elif metric == "expenses" and txn_type == "expense":
                period_data[period_key]["total"] += abs(amount)
                period_data[period_key]["count"] += 1
            elif metric == "net":
                if txn_type == "income":
                    period_data[period_key]["total"] += abs(amount)
                else:
                    period_data[period_key]["total"] -= abs(amount)
                period_data[period_key]["count"] += 1

        return period_data

    def _get_period_key(self, date_str: str, period_type: str) -> str:
        """Get period key from date string."""
        if period_type == "monthly":
            return date_str[:7]  # YYYY-MM
        elif period_type == "quarterly":
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            quarter = (date_obj.month - 1) // 3 + 1
            return f"{date_obj.year}-Q{quarter}"
        elif period_type == "yearly":
            return date_str[:4]  # YYYY
        else:
            return date_str[:7]  # Default to monthly

    def _calculate_trend(self, values: List[float]) -> tuple:
        """Calculate trend direction and percentage change."""
        if len(values) < 2:
            return "stable", 0.0

        first_value = values[0]
        last_value = values[-1]

        if first_value == 0:
            return "stable", 0.0

        change_percentage = ((last_value - first_value) / first_value) * 100

        if abs(change_percentage) < 5:
            direction = "stable"
        elif change_percentage > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        return direction, change_percentage

    def _calculate_year_metrics(
        self, transactions: List[Dict], year: int, base_currency: str
    ) -> Dict[str, float]:
        """Calculate income, expenses, and net for a year."""
        income = 0
        expenses = 0

        for txn in transactions:
            date_str = txn.get("date", "")
            if not date_str or not date_str.startswith(str(year)):
                continue

            amount = float(txn.get("amount", 0))
            txn_type = txn.get("type", "")

            # Convert to base currency
            txn_currency = txn.get("currency", base_currency)
            if txn_currency != base_currency:
                txn_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                amount = self._convert_amount(
                    abs(amount), txn_currency, base_currency, txn_date
                )
            else:
                amount = abs(amount)

            if txn_type == "income":
                income += amount
            elif txn_type == "expense":
                expenses += amount

        return {"income": income, "expenses": expenses, "net": income - expenses}

    def _create_yoy_comparison(
        self,
        metric: str,
        current_year: int,
        current_value: float,
        previous_year: int,
        previous_value: float,
        is_income: bool,
    ) -> YoYComparison:
        """Create year-over-year comparison."""
        change_amount = current_value - previous_value
        change_percentage = (
            (change_amount / previous_value * 100) if previous_value > 0 else 0
        )

        # Determine if change is improvement
        if is_income:
            is_improvement = change_amount > 0
        else:
            is_improvement = change_amount < 0

        return YoYComparison(
            metric=metric,
            current_year=current_year,
            current_value=current_value,
            previous_year=previous_year,
            previous_value=previous_value,
            change_amount=change_amount,
            change_percentage=change_percentage,
            is_improvement=is_improvement,
        )

    def _get_category_comparisons(
        self,
        transactions: List[Dict],
        current_year: int,
        previous_year: int,
        base_currency: str,
    ) -> List[Dict[str, Any]]:
        """Get category-level year-over-year comparisons."""
        categories = csv_manager.read_csv("categories.csv")
        category_map = {cat["id"]: cat["name"] for cat in categories}

        # Group by category and year
        category_data = defaultdict(lambda: {"current": 0, "previous": 0})

        for txn in transactions:
            date_str = txn.get("date", "")
            if not date_str:
                continue

            year = int(date_str[:4])
            if year not in [current_year, previous_year]:
                continue

            if txn.get("type") != "expense":
                continue

            category_id = txn.get("category_id", "")
            amount = abs(float(txn.get("amount", 0)))

            # Convert to base currency
            txn_currency = txn.get("currency", base_currency)
            if txn_currency != base_currency:
                txn_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                amount = self._convert_amount(
                    amount, txn_currency, base_currency, txn_date
                )

            if year == current_year:
                category_data[category_id]["current"] += amount
            else:
                category_data[category_id]["previous"] += amount

        # Create comparisons
        comparisons = []
        for category_id, data in category_data.items():
            if data["current"] == 0 and data["previous"] == 0:
                continue

            change = data["current"] - data["previous"]
            change_pct = (
                (change / data["previous"] * 100) if data["previous"] > 0 else 0
            )

            comparisons.append(
                {
                    "category_id": category_id,
                    "category_name": category_map.get(category_id, "Unknown"),
                    "current_value": data["current"],
                    "previous_value": data["previous"],
                    "change_amount": change,
                    "change_percentage": change_pct,
                }
            )

        # Sort by current value descending
        comparisons.sort(key=lambda x: x["current_value"], reverse=True)

        return comparisons

    def _detect_category_pattern(
        self, category_id: str, category_name: str, transactions: List[Dict]
    ) -> Optional[SpendingPattern]:
        """Detect spending pattern for a category."""
        if len(transactions) < 3:
            return None

        amounts = [txn["amount"] for txn in transactions]
        average_amount = statistics.mean(amounts)

        # Calculate coefficient of variation
        std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
        cv = (std_dev / average_amount) if average_amount > 0 else 0

        # Determine pattern type
        if cv < 0.2:
            pattern_type = "consistent"
            confidence = 0.9
            description = (
                f"Consistent spending of ~{average_amount:.2f} per transaction"
            )
        elif cv < 0.5:
            pattern_type = "moderate"
            confidence = 0.7
            description = (
                f"Moderate variation in spending, average {average_amount:.2f}"
            )
        else:
            pattern_type = "variable"
            confidence = 0.5
            description = f"Highly variable spending, average {average_amount:.2f}"

        # Estimate frequency
        dates = [datetime.strptime(txn["date"], "%Y-%m-%d") for txn in transactions]
        dates.sort()

        if len(dates) > 1:
            avg_days_between = (dates[-1] - dates[0]).days / (len(dates) - 1)

            if avg_days_between < 7:
                frequency = "weekly"
            elif avg_days_between < 35:
                frequency = "monthly"
            elif avg_days_between < 100:
                frequency = "quarterly"
            else:
                frequency = "yearly"
        else:
            frequency = "unknown"

        return SpendingPattern(
            category=category_name,
            pattern_type=pattern_type,
            average_amount=average_amount,
            frequency=frequency,
            confidence=confidence,
            description=description,
        )


# Singleton instance
analytics_service = AnalyticsService()
