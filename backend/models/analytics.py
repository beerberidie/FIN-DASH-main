"""Analytics models for trends, predictions, and financial health."""

from datetime import date as date_type
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Trend Analysis Models


class TrendDataPoint(BaseModel):
    """Single data point in a trend."""

    period: str = Field(..., description="Period label (e.g., '2025-01', 'Q1 2025')")
    value: float = Field(..., description="Value for this period")
    count: int = Field(default=0, description="Number of items in this period")


class TrendAnalysis(BaseModel):
    """Trend analysis for a metric over time."""

    metric: str = Field(..., description="Metric name (e.g., 'income', 'expenses')")
    period_type: str = Field(
        ..., description="Period type (monthly, quarterly, yearly)"
    )
    data_points: List[TrendDataPoint] = Field(..., description="Trend data points")
    average: float = Field(..., description="Average value across all periods")
    total: float = Field(..., description="Total value across all periods")
    trend_direction: str = Field(
        ..., description="Trend direction (increasing, decreasing, stable)"
    )
    trend_percentage: float = Field(
        ..., description="Percentage change from first to last period"
    )


# Year-over-Year Comparison Models


class YoYComparison(BaseModel):
    """Year-over-year comparison for a metric."""

    metric: str = Field(..., description="Metric name")
    current_year: int = Field(..., description="Current year")
    current_value: float = Field(..., description="Current year value")
    previous_year: int = Field(..., description="Previous year")
    previous_value: float = Field(..., description="Previous year value")
    change_amount: float = Field(..., description="Absolute change")
    change_percentage: float = Field(..., description="Percentage change")
    is_improvement: bool = Field(..., description="Whether change is positive")


class YoYReport(BaseModel):
    """Complete year-over-year report."""

    current_year: int = Field(..., description="Current year")
    previous_year: int = Field(..., description="Previous year")
    income_comparison: YoYComparison = Field(..., description="Income YoY comparison")
    expense_comparison: YoYComparison = Field(..., description="Expense YoY comparison")
    net_comparison: YoYComparison = Field(..., description="Net income YoY comparison")
    savings_rate_current: float = Field(..., description="Current year savings rate")
    savings_rate_previous: float = Field(..., description="Previous year savings rate")
    category_comparisons: List[Dict[str, Any]] = Field(
        default_factory=list, description="Category-level comparisons"
    )


# Spending Pattern Models


class SpendingPattern(BaseModel):
    """Detected spending pattern."""

    category: str = Field(..., description="Category name")
    pattern_type: str = Field(
        ..., description="Pattern type (consistent, increasing, decreasing, seasonal)"
    )
    average_amount: float = Field(..., description="Average spending amount")
    frequency: str = Field(
        ..., description="Spending frequency (daily, weekly, monthly)"
    )
    confidence: float = Field(..., description="Pattern confidence (0-1)")
    description: str = Field(..., description="Human-readable pattern description")


class CategoryInsight(BaseModel):
    """Deep-dive insight for a category."""

    category_id: str = Field(..., description="Category ID")
    category_name: str = Field(..., description="Category name")
    total_spent: float = Field(..., description="Total amount spent")
    transaction_count: int = Field(..., description="Number of transactions")
    average_transaction: float = Field(..., description="Average transaction amount")
    percentage_of_total: float = Field(..., description="Percentage of total spending")
    trend: str = Field(
        ..., description="Spending trend (increasing, decreasing, stable)"
    )
    top_merchants: List[str] = Field(
        default_factory=list, description="Top merchants/descriptions"
    )
    monthly_breakdown: List[TrendDataPoint] = Field(
        default_factory=list, description="Monthly spending breakdown"
    )


# Prediction Models


class Prediction(BaseModel):
    """Prediction for future period."""

    period: str = Field(..., description="Future period (e.g., '2025-11')")
    predicted_value: float = Field(..., description="Predicted value")
    confidence_interval_low: float = Field(
        ..., description="Lower bound of confidence interval"
    )
    confidence_interval_high: float = Field(
        ..., description="Upper bound of confidence interval"
    )
    confidence_level: float = Field(
        default=0.95, description="Confidence level (e.g., 0.95 for 95%)"
    )


class PredictionReport(BaseModel):
    """Prediction report for income and expenses."""

    metric: str = Field(
        ..., description="Metric being predicted (income, expenses, net)"
    )
    method: str = Field(
        ...,
        description="Prediction method (moving_average, linear_regression, seasonal)",
    )
    predictions: List[Prediction] = Field(..., description="Future predictions")
    historical_accuracy: Optional[float] = Field(
        None, description="Historical prediction accuracy"
    )


# Financial Health Models


class HealthMetric(BaseModel):
    """Individual health metric."""

    name: str = Field(..., description="Metric name")
    score: float = Field(..., description="Score (0-100)")
    status: str = Field(..., description="Status (excellent, good, fair, poor)")
    description: str = Field(..., description="Metric description")
    recommendation: Optional[str] = Field(
        None, description="Improvement recommendation"
    )


class FinancialHealthScore(BaseModel):
    """Complete financial health assessment."""

    overall_score: float = Field(..., description="Overall health score (0-100)")
    overall_status: str = Field(
        ..., description="Overall status (excellent, good, fair, poor)"
    )
    metrics: List[HealthMetric] = Field(..., description="Individual health metrics")
    strengths: List[str] = Field(
        default_factory=list, description="Financial strengths"
    )
    weaknesses: List[str] = Field(
        default_factory=list, description="Areas for improvement"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Actionable recommendations"
    )
    calculated_at: str = Field(..., description="Calculation timestamp")


class HealthMetricBreakdown(BaseModel):
    """Detailed breakdown of health metrics."""

    savings_rate: float = Field(..., description="Savings rate percentage")
    debt_to_income: float = Field(..., description="Debt-to-income ratio")
    emergency_fund_months: float = Field(
        ..., description="Months of expenses in emergency fund"
    )
    budget_adherence: float = Field(..., description="Budget adherence percentage")
    investment_diversification: float = Field(
        ..., description="Investment diversification score"
    )
    net_worth_trend: str = Field(
        ..., description="Net worth trend (increasing, decreasing, stable)"
    )


# Custom Report Models


class CustomReportRequest(BaseModel):
    """Request for custom date range report."""

    start_date: date_type = Field(..., description="Report start date")
    end_date: date_type = Field(..., description="Report end date")
    include_income: bool = Field(default=True, description="Include income analysis")
    include_expenses: bool = Field(default=True, description="Include expense analysis")
    include_categories: bool = Field(
        default=True, description="Include category breakdown"
    )
    include_trends: bool = Field(default=True, description="Include trend analysis")
    include_comparisons: bool = Field(
        default=False, description="Include period comparisons"
    )
    group_by: str = Field(
        default="month", description="Grouping period (day, week, month, quarter)"
    )


class CustomReport(BaseModel):
    """Custom date range report."""

    start_date: str = Field(..., description="Report start date")
    end_date: str = Field(..., description="Report end date")
    total_income: float = Field(..., description="Total income")
    total_expenses: float = Field(..., description="Total expenses")
    net_income: float = Field(..., description="Net income")
    savings_rate: float = Field(..., description="Savings rate percentage")
    category_breakdown: List[CategoryInsight] = Field(
        default_factory=list, description="Category insights"
    )
    trends: List[TrendAnalysis] = Field(
        default_factory=list, description="Trend analyses"
    )
    top_income_sources: List[Dict[str, Any]] = Field(
        default_factory=list, description="Top income sources"
    )
    top_expenses: List[Dict[str, Any]] = Field(
        default_factory=list, description="Top expenses"
    )


# Analytics Request Models


class TrendRequest(BaseModel):
    """Request for trend analysis."""

    metric: str = Field(
        ..., description="Metric to analyze (income, expenses, net, category)"
    )
    period_type: str = Field(
        default="monthly", description="Period type (monthly, quarterly, yearly)"
    )
    start_date: Optional[date_type] = Field(None, description="Start date (optional)")
    end_date: Optional[date_type] = Field(None, description="End date (optional)")
    category_id: Optional[str] = Field(
        None, description="Category ID for category-specific trends"
    )


class PredictionRequest(BaseModel):
    """Request for predictions."""

    metric: str = Field(..., description="Metric to predict (income, expenses, net)")
    periods_ahead: int = Field(default=3, description="Number of periods to predict")
    method: str = Field(default="moving_average", description="Prediction method")


class HealthScoreRequest(BaseModel):
    """Request for health score calculation."""

    include_investments: bool = Field(
        default=True, description="Include investment metrics"
    )
    include_debts: bool = Field(default=True, description="Include debt metrics")
    reference_date: Optional[date_type] = Field(
        None, description="Reference date for calculation"
    )


# Drill-down Models


class DrillDownRequest(BaseModel):
    """Request for drill-down analysis."""

    dimension: str = Field(
        ..., description="Dimension to drill down (category, account, merchant, tag)"
    )
    start_date: Optional[date_type] = Field(None, description="Start date filter")
    end_date: Optional[date_type] = Field(None, description="End date filter")
    parent_id: Optional[str] = Field(
        None, description="Parent dimension ID for hierarchical drill-down"
    )


class DrillDownResult(BaseModel):
    """Drill-down analysis result."""

    dimension: str = Field(..., description="Dimension analyzed")
    items: List[Dict[str, Any]] = Field(
        ..., description="Drill-down items with metrics"
    )
    total_value: float = Field(..., description="Total value across all items")
    item_count: int = Field(..., description="Number of items")
    top_item: Optional[Dict[str, Any]] = Field(None, description="Top item by value")
