"""Analytics API endpoints for trends, predictions, and financial health."""

from datetime import date as date_type
from typing import Optional, List
from fastapi import APIRouter, Query

from models.analytics import (
    TrendAnalysis,
    YoYReport,
    SpendingPattern,
    CategoryInsight,
    PredictionReport,
    FinancialHealthScore,
    HealthMetricBreakdown,
    CustomReport,
    DrillDownResult,
)
from services.analytics_service import analytics_service
from services.health_service import health_service
from services.prediction_service import prediction_service
from services.csv_manager import csv_manager

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _get_base_currency() -> str:
    """Get base currency from settings."""
    settings = csv_manager.read_json("settings.json")
    return settings.get("base_currency", "ZAR")


# Trend Analysis Endpoints


@router.get("/trends/{metric}", response_model=TrendAnalysis)
def get_trend_analysis(
    metric: str,
    period_type: str = Query(
        default="monthly", description="Period type (monthly, quarterly, yearly)"
    ),
    start_date: Optional[str] = Query(
        None, description="Start date filter (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    category_id: Optional[str] = Query(
        None, description="Category ID for category-specific trends"
    ),
):
    """
    Get trend analysis for a metric over time.

    Path Parameters:
    - **metric**: Metric to analyze (income, expenses, net)

    Query Parameters:
    - **period_type**: Period type (monthly, quarterly, yearly) - default: monthly
    - **start_date**: Start date filter (YYYY-MM-DD format, optional)
    - **end_date**: End date filter (YYYY-MM-DD format, optional)
    - **category_id**: Category ID for category-specific trends (optional)

    Returns:
    - Trend analysis with data points and trend direction
    """
    from datetime import datetime

    # Parse date strings to date objects
    start_date_obj = (
        datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
    )
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

    base_currency = _get_base_currency()

    return analytics_service.get_trend_analysis(
        metric=metric,
        period_type=period_type,
        start_date=start_date_obj,
        end_date=end_date_obj,
        category_id=category_id,
        base_currency=base_currency,
    )


# Year-over-Year Comparison


@router.get("/yoy-comparison", response_model=YoYReport)
def get_yoy_comparison(
    current_year: Optional[int] = Query(
        None, description="Year to compare (defaults to current year)"
    )
):
    """
    Get year-over-year comparison report.

    Query Parameters:
    - **current_year**: Year to compare (defaults to current year)

    Returns:
    - Complete YoY report with income, expense, and net comparisons
    """
    base_currency = _get_base_currency()

    return analytics_service.get_yoy_comparison(
        current_year=current_year, base_currency=base_currency
    )


# Spending Patterns


@router.get("/spending-patterns", response_model=List[SpendingPattern])
def get_spending_patterns(
    start_date: Optional[str] = Query(
        None, description="Start date filter (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
):
    """
    Detect spending patterns across categories.

    Query Parameters:
    - **start_date**: Start date filter (YYYY-MM-DD format, optional)
    - **end_date**: End date filter (YYYY-MM-DD format, optional)

    Returns:
    - List of detected spending patterns
    """
    from datetime import datetime

    start_date_obj = (
        datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
    )
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

    base_currency = _get_base_currency()

    return analytics_service.detect_spending_patterns(
        start_date=start_date_obj, end_date=end_date_obj, base_currency=base_currency
    )


# Category Insights


@router.get("/category-insights/{category_id}", response_model=CategoryInsight)
def get_category_insights(
    category_id: str,
    start_date: Optional[str] = Query(
        None, description="Start date filter (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
):
    """
    Get deep-dive insights for a specific category.

    Path Parameters:
    - **category_id**: Category ID to analyze

    Query Parameters:
    - **start_date**: Start date filter (YYYY-MM-DD format, optional)
    - **end_date**: End date filter (YYYY-MM-DD format, optional)

    Returns:
    - Detailed category insights with breakdown
    """
    from datetime import datetime

    start_date_obj = (
        datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
    )
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

    base_currency = _get_base_currency()

    return analytics_service.get_category_insights(
        category_id=category_id,
        start_date=start_date_obj,
        end_date=end_date_obj,
        base_currency=base_currency,
    )


# Predictions


@router.get("/predictions/{metric}", response_model=PredictionReport)
def get_predictions(
    metric: str,
    periods_ahead: int = Query(default=3, description="Number of periods to predict"),
    method: str = Query(
        default="moving_average",
        description="Prediction method (moving_average, linear_regression, seasonal)",
    ),
):
    """
    Get predictions for future periods.

    Path Parameters:
    - **metric**: Metric to predict (income, expenses, net)

    Query Parameters:
    - **periods_ahead**: Number of months to predict (default: 3)
    - **method**: Prediction method (moving_average, linear_regression, seasonal)

    Returns:
    - Prediction report with future predictions and confidence intervals
    """
    base_currency = _get_base_currency()

    return prediction_service.predict_metric(
        metric=metric,
        periods_ahead=periods_ahead,
        method=method,
        base_currency=base_currency,
    )


@router.get("/predictions/category/{category_id}", response_model=PredictionReport)
def get_category_predictions(
    category_id: str,
    periods_ahead: int = Query(default=3, description="Number of periods to predict"),
):
    """
    Get predictions for a specific category.

    Path Parameters:
    - **category_id**: Category ID to predict

    Query Parameters:
    - **periods_ahead**: Number of months to predict (default: 3)

    Returns:
    - Prediction report for category spending
    """
    base_currency = _get_base_currency()

    return prediction_service.predict_category_spending(
        category_id=category_id,
        periods_ahead=periods_ahead,
        base_currency=base_currency,
    )


# Financial Health


@router.get("/health-score", response_model=FinancialHealthScore)
def get_health_score(
    include_investments: bool = Query(
        default=True, description="Include investment metrics"
    ),
    include_debts: bool = Query(default=True, description="Include debt metrics"),
    reference_date: Optional[str] = Query(
        None, description="Reference date for calculation (YYYY-MM-DD)"
    ),
):
    """
    Calculate comprehensive financial health score.

    Query Parameters:
    - **include_investments**: Include investment metrics (default: true)
    - **include_debts**: Include debt metrics (default: true)
    - **reference_date**: Reference date for calculation (YYYY-MM-DD format, defaults to today)

    Returns:
    - Complete financial health assessment with scores and recommendations
    """
    from datetime import datetime

    reference_date_obj = (
        datetime.strptime(reference_date, "%Y-%m-%d").date() if reference_date else None
    )

    base_currency = _get_base_currency()

    return health_service.calculate_health_score(
        include_investments=include_investments,
        include_debts=include_debts,
        reference_date=reference_date_obj,
        base_currency=base_currency,
    )


@router.get("/health-breakdown", response_model=HealthMetricBreakdown)
def get_health_breakdown(
    reference_date: Optional[str] = Query(
        None, description="Reference date for calculation (YYYY-MM-DD)"
    )
):
    """
    Get detailed breakdown of health metrics.

    Query Parameters:
    - **reference_date**: Reference date for calculation (YYYY-MM-DD format, defaults to today)

    Returns:
    - Detailed breakdown of all health metrics
    """
    from datetime import datetime

    reference_date_obj = (
        datetime.strptime(reference_date, "%Y-%m-%d").date() if reference_date else None
    )

    base_currency = _get_base_currency()

    return health_service.get_health_breakdown(
        reference_date=reference_date_obj, base_currency=base_currency
    )


# Income Analysis


@router.get("/income-analysis")
def get_income_analysis(
    start_date: Optional[str] = Query(
        None, description="Start date filter (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
):
    """
    Get detailed income analysis.

    Query Parameters:
    - **start_date**: Start date filter (YYYY-MM-DD format, optional)
    - **end_date**: End date filter (YYYY-MM-DD format, optional)

    Returns:
    - Income analysis with sources, trends, and growth
    """
    from datetime import datetime

    start_date_obj = (
        datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
    )
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

    base_currency = _get_base_currency()

    # Get income trend
    income_trend = analytics_service.get_trend_analysis(
        metric="income",
        period_type="monthly",
        start_date=start_date_obj,
        end_date=end_date_obj,
        base_currency=base_currency,
    )

    # Get income predictions
    income_predictions = prediction_service.predict_metric(
        metric="income",
        periods_ahead=3,
        method="linear_regression",
        base_currency=base_currency,
    )

    return {
        "trend": income_trend,
        "predictions": income_predictions,
        "average_monthly": income_trend.average,
        "total": income_trend.total,
        "growth_rate": income_trend.trend_percentage,
    }


# Expense Analysis


@router.get("/expense-analysis")
def get_expense_analysis(
    start_date: Optional[str] = Query(
        None, description="Start date filter (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
):
    """
    Get detailed expense analysis.

    Query Parameters:
    - **start_date**: Start date filter (YYYY-MM-DD format, optional)
    - **end_date**: End date filter (YYYY-MM-DD format, optional)

    Returns:
    - Expense analysis with categories, trends, and patterns
    """
    from datetime import datetime

    start_date_obj = (
        datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
    )
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

    base_currency = _get_base_currency()

    # Get expense trend
    expense_trend = analytics_service.get_trend_analysis(
        metric="expenses",
        period_type="monthly",
        start_date=start_date_obj,
        end_date=end_date_obj,
        base_currency=base_currency,
    )

    # Get expense predictions
    expense_predictions = prediction_service.predict_metric(
        metric="expenses",
        periods_ahead=3,
        method="seasonal",
        base_currency=base_currency,
    )

    # Get spending patterns
    patterns = analytics_service.detect_spending_patterns(
        start_date=start_date_obj, end_date=end_date_obj, base_currency=base_currency
    )

    return {
        "trend": expense_trend,
        "predictions": expense_predictions,
        "patterns": patterns,
        "average_monthly": expense_trend.average,
        "total": expense_trend.total,
    }
