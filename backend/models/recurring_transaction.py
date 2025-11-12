"""Recurring Transaction model for FIN-DASH."""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime, date


class RecurringTransaction(BaseModel):
    """Recurring transaction model."""

    id: str
    name: str = Field(..., description="Name/description of the recurring transaction")
    amount: float = Field(
        ...,
        description="Transaction amount (positive for income, negative for expense)",
    )
    category_id: str = Field(..., description="Category ID")
    account_id: str = Field(..., description="Account ID")
    type: Literal["income", "expense"] = Field(..., description="Transaction type")

    # Recurrence settings
    frequency: Literal[
        "daily", "weekly", "biweekly", "monthly", "quarterly", "yearly"
    ] = Field(..., description="Frequency of recurrence")
    start_date: str = Field(
        ..., description="Date to start generating transactions (YYYY-MM-DD)"
    )
    end_date: Optional[str] = Field(None, description="Optional end date (YYYY-MM-DD)")

    # Day of period settings
    day_of_month: Optional[int] = Field(
        None,
        ge=1,
        le=31,
        description="Day of month for monthly/quarterly/yearly (1-31)",
    )
    day_of_week: Optional[int] = Field(
        None,
        ge=0,
        le=6,
        description="Day of week for weekly/biweekly (0=Monday, 6=Sunday)",
    )

    # Status and metadata
    is_active: bool = Field(
        True, description="Whether this recurring transaction is active"
    )
    last_generated: Optional[str] = Field(
        None, description="Date of last generated transaction"
    )
    next_due: Optional[str] = Field(
        None, description="Next due date for transaction generation"
    )

    tags: Optional[str] = Field("", description="Comma-separated tags")
    notes: Optional[str] = Field("", description="Additional notes")

    created_at: str
    updated_at: str


class RecurringTransactionCreate(BaseModel):
    """Model for creating a recurring transaction."""

    name: str
    amount: float
    category_id: str
    account_id: str
    type: Literal["income", "expense"]
    frequency: Literal["daily", "weekly", "biweekly", "monthly", "quarterly", "yearly"]
    start_date: str  # YYYY-MM-DD
    end_date: Optional[str] = None  # YYYY-MM-DD
    day_of_month: Optional[int] = None
    day_of_week: Optional[int] = None
    is_active: bool = True
    tags: Optional[str] = ""
    notes: Optional[str] = ""


class RecurringTransactionUpdate(BaseModel):
    """Model for updating a recurring transaction."""

    name: Optional[str] = None
    amount: Optional[float] = None
    category_id: Optional[str] = None
    account_id: Optional[str] = None
    type: Optional[Literal["income", "expense"]] = None
    frequency: Optional[
        Literal["daily", "weekly", "biweekly", "monthly", "quarterly", "yearly"]
    ] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    day_of_month: Optional[int] = None
    day_of_week: Optional[int] = None
    is_active: Optional[bool] = None
    tags: Optional[str] = None
    notes: Optional[str] = None
