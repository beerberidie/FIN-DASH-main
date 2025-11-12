"""Goal models."""

from typing import Optional
from pydantic import BaseModel, Field


class GoalBase(BaseModel):
    """Base goal model."""

    name: str = Field(..., min_length=1, max_length=100)
    target_amount: float = Field(..., gt=0)
    current_amount: float = Field(default=0.0, ge=0)
    target_date: Optional[str] = None  # ISO date string YYYY-MM-DD
    linked_account_id: Optional[str] = None
    color: str = Field(default="blue")
    icon: str = Field(default="Target", max_length=50)


class GoalCreate(GoalBase):
    """Model for creating a goal."""

    pass


class GoalUpdate(BaseModel):
    """Model for updating a goal."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    target_amount: Optional[float] = Field(None, gt=0)
    current_amount: Optional[float] = Field(None, ge=0)
    target_date: Optional[str] = None  # ISO date string YYYY-MM-DD
    linked_account_id: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)


class Goal(GoalBase):
    """Full goal model with ID and timestamps."""

    id: str
    created_at: str
    updated_at: str

    @classmethod
    def from_csv(cls, row: dict) -> "Goal":
        """Create Goal from CSV row."""
        row_copy = row.copy()
        row_copy["target_amount"] = float(row_copy.get("target_amount", 0))
        row_copy["current_amount"] = float(row_copy.get("current_amount", 0))
        # Handle empty target_date
        if not row_copy.get("target_date"):
            row_copy["target_date"] = None
        if not row_copy.get("linked_account_id"):
            row_copy["linked_account_id"] = None
        return cls(**row_copy)

    def to_csv(self) -> dict:
        """Convert Goal to CSV row."""
        data = self.model_dump()
        # Convert None to empty string for CSV
        if data["target_date"] is None:
            data["target_date"] = ""
        if data["linked_account_id"] is None:
            data["linked_account_id"] = ""
        return data

    class Config:
        from_attributes = True


# Field names for CSV
GOAL_FIELDNAMES = [
    "id",
    "name",
    "target_amount",
    "current_amount",
    "target_date",
    "linked_account_id",
    "color",
    "icon",
    "created_at",
    "updated_at",
]
