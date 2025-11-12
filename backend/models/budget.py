"""Budget models."""

from pydantic import BaseModel, Field
from typing import Optional


class BudgetBase(BaseModel):
    """Base budget model with 50/30/20 rule."""

    year: int = Field(..., ge=2000, le=2100)
    month: int = Field(..., ge=1, le=12)
    needs_planned: float = Field(..., ge=0)
    wants_planned: float = Field(..., ge=0)
    savings_planned: float = Field(..., ge=0)
    notes: Optional[str] = None


class BudgetCreate(BudgetBase):
    """Model for creating a budget."""

    pass


class BudgetUpdate(BaseModel):
    """Model for updating a budget."""

    needs_planned: Optional[float] = Field(None, ge=0)
    wants_planned: Optional[float] = Field(None, ge=0)
    savings_planned: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class Budget(BudgetBase):
    """Full budget model with ID and timestamp."""

    id: str
    created_at: str
    updated_at: str

    @classmethod
    def from_csv(cls, row: dict) -> "Budget":
        """Create Budget from CSV row."""
        row_copy = row.copy()
        row_copy["year"] = int(row_copy.get("year", 0))
        row_copy["month"] = int(row_copy.get("month", 0))
        row_copy["needs_planned"] = float(row_copy.get("needs_planned", 0))
        row_copy["wants_planned"] = float(row_copy.get("wants_planned", 0))
        row_copy["savings_planned"] = float(row_copy.get("savings_planned", 0))
        return cls(**row_copy)

    def to_csv(self) -> dict:
        """Convert Budget to CSV row."""
        return self.model_dump()

    class Config:
        from_attributes = True


# Field names for CSV
BUDGET_FIELDNAMES = [
    "id",
    "year",
    "month",
    "needs_planned",
    "wants_planned",
    "savings_planned",
    "notes",
    "created_at",
    "updated_at",
]
