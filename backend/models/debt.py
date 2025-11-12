"""Debt models."""

from typing import Optional
from pydantic import BaseModel, Field


class DebtBase(BaseModel):
    """Base debt model."""

    name: str = Field(..., min_length=1, max_length=100)
    debt_type: str = Field(
        ...,
        pattern="^(credit_card|personal_loan|student_loan|mortgage|car_loan|other)$",
    )
    original_balance: float = Field(..., gt=0)
    current_balance: float = Field(..., ge=0)
    interest_rate: float = Field(..., ge=0, le=100)
    minimum_payment: float = Field(..., ge=0)
    due_day: int = Field(..., ge=1, le=31)
    linked_account_id: Optional[str] = None
    notes: Optional[str] = None


class DebtCreate(DebtBase):
    """Model for creating a debt."""

    pass


class DebtUpdate(BaseModel):
    """Model for updating a debt."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    debt_type: Optional[str] = Field(
        None,
        pattern="^(credit_card|personal_loan|student_loan|mortgage|car_loan|other)$",
    )
    original_balance: Optional[float] = Field(None, gt=0)
    current_balance: Optional[float] = Field(None, ge=0)
    interest_rate: Optional[float] = Field(None, ge=0, le=100)
    minimum_payment: Optional[float] = Field(None, ge=0)
    due_day: Optional[int] = Field(None, ge=1, le=31)
    linked_account_id: Optional[str] = None
    notes: Optional[str] = None


class Debt(DebtBase):
    """Full debt model with ID and timestamps."""

    id: str
    created_at: str
    updated_at: str

    @classmethod
    def from_csv(cls, row: dict) -> "Debt":
        """Create Debt from CSV row."""
        return cls(
            id=row["id"],
            name=row["name"],
            debt_type=row["debt_type"],
            original_balance=float(row["original_balance"]),
            current_balance=float(row["current_balance"]),
            interest_rate=float(row["interest_rate"]),
            minimum_payment=float(row["minimum_payment"]),
            due_day=int(row["due_day"]),
            linked_account_id=row.get("linked_account_id") or None,
            notes=row.get("notes") or None,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_csv(self) -> dict:
        """Convert Debt to CSV row."""
        data = self.model_dump()
        # Convert None to empty string for CSV
        if data.get("linked_account_id") is None:
            data["linked_account_id"] = ""
        if data.get("notes") is None:
            data["notes"] = ""
        return data

    class Config:
        from_attributes = True


# Field names for CSV
DEBT_FIELDNAMES = [
    "id",
    "name",
    "debt_type",
    "original_balance",
    "current_balance",
    "interest_rate",
    "minimum_payment",
    "due_day",
    "linked_account_id",
    "notes",
    "created_at",
    "updated_at",
]
