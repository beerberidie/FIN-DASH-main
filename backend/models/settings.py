"""Settings model."""

from typing import Dict
from pydantic import BaseModel


class BudgetRule(BaseModel):
    """Budget rule percentages."""

    needs: float = 0.50
    wants: float = 0.30
    savings: float = 0.20
    debt: float = 0.00


class Settings(BaseModel):
    """Application settings."""

    currency: str = "ZAR"  # Deprecated: use base_currency instead
    base_currency: str = "ZAR"  # Primary currency for reporting and calculations
    locale: str = "en-ZA"
    budget_rule: BudgetRule = BudgetRule()
    auto_categorize: bool = True
    sync_google: bool = False
    google_sheets_id: str = ""
    lm_studio_url: str = "http://127.0.0.1:1234/v1"
    ai_model: str = "qwen/qwen3-4b-thinking-2507"
    weekly_report_day: str = "SUN"
    weekly_report_hour: int = 17
    backup_enabled: bool = True
    backup_retention_days: int = 90
    theme: str = "system"
    created_at: str = ""
    updated_at: str = ""

    class Config:
        from_attributes = True
