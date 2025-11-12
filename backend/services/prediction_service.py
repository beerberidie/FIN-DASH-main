"""Prediction service for forecasting future income and expenses."""

from datetime import datetime, date as date_type, timedelta
from typing import List, Dict, Any
from collections import defaultdict
import statistics

from models.analytics import Prediction, PredictionReport
from models.currency import CurrencyConversion
from services.csv_manager import csv_manager
from services.currency_service import currency_service


class PredictionService:
    """Service for predicting future financial metrics."""

    def __init__(self):
        """Initialize prediction service."""
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

    def predict_metric(
        self,
        metric: str,
        periods_ahead: int = 3,
        method: str = "moving_average",
        base_currency: str = "ZAR",
    ) -> PredictionReport:
        """
        Predict future values for a metric.

        Args:
            metric: Metric to predict (income, expenses, net)
            periods_ahead: Number of months to predict
            method: Prediction method (moving_average, linear_regression, seasonal)
            base_currency: Base currency for conversions

        Returns:
            PredictionReport with predictions
        """
        # Get historical data
        historical_data = self._get_historical_monthly_data(metric, base_currency)

        if len(historical_data) < 3:
            # Not enough data for predictions
            return PredictionReport(
                metric=metric, method=method, predictions=[], historical_accuracy=None
            )

        # Generate predictions based on method
        if method == "moving_average":
            predictions = self._predict_moving_average(historical_data, periods_ahead)
        elif method == "linear_regression":
            predictions = self._predict_linear_regression(
                historical_data, periods_ahead
            )
        elif method == "seasonal":
            predictions = self._predict_seasonal(historical_data, periods_ahead)
        else:
            predictions = self._predict_moving_average(historical_data, periods_ahead)

        # Calculate historical accuracy
        accuracy = self._calculate_historical_accuracy(historical_data, method)

        return PredictionReport(
            metric=metric,
            method=method,
            predictions=predictions,
            historical_accuracy=accuracy,
        )

    def predict_category_spending(
        self, category_id: str, periods_ahead: int = 3, base_currency: str = "ZAR"
    ) -> PredictionReport:
        """
        Predict future spending for a specific category.

        Args:
            category_id: Category ID to predict
            periods_ahead: Number of months to predict
            base_currency: Base currency for conversions

        Returns:
            PredictionReport with category predictions
        """
        # Get historical data for category
        historical_data = self._get_category_historical_data(category_id, base_currency)

        if len(historical_data) < 3:
            return PredictionReport(
                metric=f"category_{category_id}",
                method="moving_average",
                predictions=[],
                historical_accuracy=None,
            )

        # Use moving average for category predictions
        predictions = self._predict_moving_average(historical_data, periods_ahead)

        return PredictionReport(
            metric=f"category_{category_id}",
            method="moving_average",
            predictions=predictions,
            historical_accuracy=None,
        )

    # Prediction methods

    def _predict_moving_average(
        self,
        historical_data: List[Dict[str, Any]],
        periods_ahead: int,
        window_size: int = 3,
    ) -> List[Prediction]:
        """Predict using moving average method."""
        predictions = []

        # Get last N values for moving average
        recent_values = [item["value"] for item in historical_data[-window_size:]]
        avg_value = statistics.mean(recent_values)

        # Calculate standard deviation for confidence interval
        std_dev = (
            statistics.stdev(recent_values)
            if len(recent_values) > 1
            else avg_value * 0.1
        )

        # Get last period
        last_period = historical_data[-1]["period"]
        last_date = datetime.strptime(last_period, "%Y-%m")

        # Generate predictions
        for i in range(1, periods_ahead + 1):
            # Calculate next period
            next_date = last_date + timedelta(days=30 * i)
            next_period = next_date.strftime("%Y-%m")

            # Confidence interval (95% = ~2 standard deviations)
            confidence_interval_low = max(0, avg_value - (2 * std_dev))
            confidence_interval_high = avg_value + (2 * std_dev)

            predictions.append(
                Prediction(
                    period=next_period,
                    predicted_value=round(avg_value, 2),
                    confidence_interval_low=round(confidence_interval_low, 2),
                    confidence_interval_high=round(confidence_interval_high, 2),
                    confidence_level=0.95,
                )
            )

        return predictions

    def _predict_linear_regression(
        self, historical_data: List[Dict[str, Any]], periods_ahead: int
    ) -> List[Prediction]:
        """Predict using simple linear regression."""
        # Prepare data
        n = len(historical_data)
        x_values = list(range(n))
        y_values = [item["value"] for item in historical_data]

        # Calculate linear regression coefficients
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(y_values)

        numerator = sum(
            (x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n)
        )
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            # Fall back to moving average
            return self._predict_moving_average(historical_data, periods_ahead)

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        # Calculate residual standard error for confidence interval
        predictions_fitted = [slope * x + intercept for x in x_values]
        residuals = [y_values[i] - predictions_fitted[i] for i in range(n)]
        residual_std = statistics.stdev(residuals) if len(residuals) > 1 else 0

        # Get last period
        last_period = historical_data[-1]["period"]
        last_date = datetime.strptime(last_period, "%Y-%m")

        # Generate predictions
        predictions = []
        for i in range(1, periods_ahead + 1):
            # Calculate next period
            next_date = last_date + timedelta(days=30 * i)
            next_period = next_date.strftime("%Y-%m")

            # Predict value
            x_future = n + i - 1
            predicted_value = slope * x_future + intercept

            # Confidence interval
            confidence_interval_low = max(0, predicted_value - (2 * residual_std))
            confidence_interval_high = predicted_value + (2 * residual_std)

            predictions.append(
                Prediction(
                    period=next_period,
                    predicted_value=round(max(0, predicted_value), 2),
                    confidence_interval_low=round(confidence_interval_low, 2),
                    confidence_interval_high=round(confidence_interval_high, 2),
                    confidence_level=0.95,
                )
            )

        return predictions

    def _predict_seasonal(
        self, historical_data: List[Dict[str, Any]], periods_ahead: int
    ) -> List[Prediction]:
        """Predict using seasonal patterns (12-month cycle)."""
        if len(historical_data) < 12:
            # Not enough data for seasonal analysis, fall back to moving average
            return self._predict_moving_average(historical_data, periods_ahead)

        # Calculate average for each month of the year
        monthly_averages = defaultdict(list)

        for item in historical_data:
            period = item["period"]
            month = int(period.split("-")[1])  # Extract month number
            monthly_averages[month].append(item["value"])

        # Calculate average for each month
        seasonal_pattern = {}
        for month, values in monthly_averages.items():
            seasonal_pattern[month] = statistics.mean(values)

        # Get last period
        last_period = historical_data[-1]["period"]
        last_date = datetime.strptime(last_period, "%Y-%m")

        # Generate predictions
        predictions = []
        for i in range(1, periods_ahead + 1):
            # Calculate next period
            next_date = last_date + timedelta(days=30 * i)
            next_period = next_date.strftime("%Y-%m")
            next_month = next_date.month

            # Get seasonal value
            predicted_value = seasonal_pattern.get(
                next_month, statistics.mean(seasonal_pattern.values())
            )

            # Calculate confidence interval based on historical variance for this month
            month_values = monthly_averages.get(next_month, [predicted_value])
            std_dev = (
                statistics.stdev(month_values)
                if len(month_values) > 1
                else predicted_value * 0.1
            )

            confidence_interval_low = max(0, predicted_value - (2 * std_dev))
            confidence_interval_high = predicted_value + (2 * std_dev)

            predictions.append(
                Prediction(
                    period=next_period,
                    predicted_value=round(predicted_value, 2),
                    confidence_interval_low=round(confidence_interval_low, 2),
                    confidence_interval_high=round(confidence_interval_high, 2),
                    confidence_level=0.95,
                )
            )

        return predictions

    # Helper methods

    def _get_historical_monthly_data(
        self, metric: str, base_currency: str, months_back: int = 12
    ) -> List[Dict[str, Any]]:
        """Get historical monthly data for a metric."""
        transactions = csv_manager.read_csv("transactions.csv")

        # Group by month
        monthly_data = defaultdict(float)

        for txn in transactions:
            date_str = txn.get("date", "")
            if not date_str:
                continue

            month = date_str[:7]  # YYYY-MM
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

            # Add to monthly total based on metric
            if metric == "income" and txn_type == "income":
                monthly_data[month] += abs(amount)
            elif metric == "expenses" and txn_type == "expense":
                monthly_data[month] += abs(amount)
            elif metric == "net":
                if txn_type == "income":
                    monthly_data[month] += abs(amount)
                else:
                    monthly_data[month] -= abs(amount)

        # Convert to list and sort
        historical_data = [
            {"period": month, "value": value}
            for month, value in sorted(monthly_data.items())
        ]

        # Return last N months
        return historical_data[-months_back:]

    def _get_category_historical_data(
        self, category_id: str, base_currency: str, months_back: int = 12
    ) -> List[Dict[str, Any]]:
        """Get historical monthly data for a category."""
        transactions = csv_manager.read_csv("transactions.csv")

        # Group by month
        monthly_data = defaultdict(float)

        for txn in transactions:
            if txn.get("category_id") != category_id:
                continue

            date_str = txn.get("date", "")
            if not date_str:
                continue

            month = date_str[:7]  # YYYY-MM
            amount = abs(float(txn.get("amount", 0)))

            # Convert to base currency
            txn_currency = txn.get("currency", base_currency)
            if txn_currency != base_currency:
                txn_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                amount = self._convert_amount(
                    amount, txn_currency, base_currency, txn_date
                )

            monthly_data[month] += amount

        # Convert to list and sort
        historical_data = [
            {"period": month, "value": value}
            for month, value in sorted(monthly_data.items())
        ]

        # Return last N months
        return historical_data[-months_back:]

    def _calculate_historical_accuracy(
        self, historical_data: List[Dict[str, Any]], method: str
    ) -> float:
        """Calculate historical prediction accuracy."""
        if len(historical_data) < 6:
            return None

        # Use first 75% of data to predict last 25%
        split_point = int(len(historical_data) * 0.75)
        train_data = historical_data[:split_point]
        test_data = historical_data[split_point:]

        # Make predictions
        if method == "moving_average":
            predictions = self._predict_moving_average(train_data, len(test_data))
        elif method == "linear_regression":
            predictions = self._predict_linear_regression(train_data, len(test_data))
        else:
            predictions = self._predict_moving_average(train_data, len(test_data))

        # Calculate accuracy
        errors = []
        for i, pred in enumerate(predictions):
            if i < len(test_data):
                actual = test_data[i]["value"]
                predicted = pred.predicted_value

                if actual > 0:
                    error = abs((actual - predicted) / actual)
                    errors.append(error)

        if not errors:
            return None

        # Return accuracy as percentage (100% - average error%)
        avg_error = statistics.mean(errors)
        accuracy = max(0, (1 - avg_error) * 100)

        return round(accuracy, 1)


# Singleton instance
prediction_service = PredictionService()
