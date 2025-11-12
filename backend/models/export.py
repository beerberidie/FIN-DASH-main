"""Export models and configurations."""

from datetime import date as date_type
from typing import Optional, Literal
from pydantic import BaseModel, Field


# Export Types
ExportFormat = Literal["pdf", "excel", "csv"]
ExportType = Literal[
    "transactions",
    "budget_report",
    "debt_report",
    "investment_portfolio",
    "financial_summary",
    "income_statement",
    "balance_sheet",
]


class ExportRequest(BaseModel):
    """Base export request model."""

    export_type: ExportType = Field(..., description="Type of export")
    format: ExportFormat = Field(..., description="Export format (pdf, excel, csv)")
    start_date: Optional[date_type] = Field(
        None, description="Start date for date range filter"
    )
    end_date: Optional[date_type] = Field(
        None, description="End date for date range filter"
    )
    include_notes: bool = Field(default=True, description="Include notes in export")
    include_tags: bool = Field(default=True, description="Include tags in export")


class TransactionExportRequest(ExportRequest):
    """Transaction export request."""

    export_type: Literal["transactions"] = "transactions"
    account_id: Optional[str] = Field(None, description="Filter by account ID")
    category_id: Optional[str] = Field(None, description="Filter by category ID")
    transaction_type: Optional[Literal["income", "expense"]] = Field(
        None, description="Filter by transaction type"
    )


class BudgetReportExportRequest(ExportRequest):
    """Budget report export request."""

    export_type: Literal["budget_report"] = "budget_report"
    month: Optional[str] = Field(None, description="Month in YYYY-MM format")


class DebtReportExportRequest(ExportRequest):
    """Debt report export request."""

    export_type: Literal["debt_report"] = "debt_report"
    include_paid_off: bool = Field(default=False, description="Include paid-off debts")


class InvestmentPortfolioExportRequest(ExportRequest):
    """Investment portfolio export request."""

    export_type: Literal["investment_portfolio"] = "investment_portfolio"
    include_transactions: bool = Field(
        default=True, description="Include transaction history"
    )
    investment_type: Optional[str] = Field(
        None, description="Filter by investment type"
    )


class FinancialSummaryExportRequest(ExportRequest):
    """Financial summary export request."""

    export_type: Literal["financial_summary"] = "financial_summary"
    include_charts: bool = Field(default=True, description="Include charts in PDF")


class IncomeStatementExportRequest(ExportRequest):
    """Income statement export request."""

    export_type: Literal["income_statement"] = "income_statement"
    month: Optional[str] = Field(
        None,
        description="Month in YYYY-MM format (optional, defaults to current month)",
    )


class BalanceSheetExportRequest(ExportRequest):
    """Balance sheet export request."""

    export_type: Literal["balance_sheet"] = "balance_sheet"
    as_of_date: Optional[date_type] = Field(
        None, description="Balance sheet as of date (defaults to today)"
    )


class ExportResponse(BaseModel):
    """Export response model."""

    filename: str = Field(..., description="Generated filename")
    file_path: str = Field(..., description="File path relative to exports directory")
    file_size: int = Field(..., description="File size in bytes")
    export_type: str = Field(..., description="Type of export")
    format: str = Field(..., description="Export format")
    created_at: str = Field(..., description="Export creation timestamp")


class ExportConfig(BaseModel):
    """Export configuration."""

    company_name: str = Field(
        default="FIN-DASH", description="Company/App name for headers"
    )
    user_name: Optional[str] = Field(None, description="User name for personalization")
    base_currency: str = Field(default="ZAR", description="Base currency for reports")
    date_format: str = Field(default="%Y-%m-%d", description="Date format for exports")
    number_format: str = Field(
        default=",.2f", description="Number format for currency values"
    )
    page_size: Literal["A4", "Letter"] = Field(
        default="A4", description="PDF page size"
    )
    orientation: Literal["portrait", "landscape"] = Field(
        default="portrait", description="PDF orientation"
    )
