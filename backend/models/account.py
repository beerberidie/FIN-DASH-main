"""Account models."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator

from utils.validation import validate_account_type


class AccountBase(BaseModel):
    """Base account model."""

    name: str = Field(..., min_length=1, max_length=100)
    type: str  # 'bank', 'cash', 'investment', 'virtual'
    opening_balance: float = 0.0
    is_active: bool = True

    @field_validator("type")
    @classmethod
    def validate_type_value(cls, v):
        validate_account_type(v)
        return v


class AccountCreate(AccountBase):
    """Model for creating an account."""

    pass


class AccountUpdate(BaseModel):
    """Model for updating an account."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = None
    is_active: Optional[bool] = None


class Account(AccountBase):
    """Full account model with ID and timestamp."""

    id: str
    created_at: str

    @classmethod
    def from_csv(cls, row: dict) -> "Account":
        """Create Account from CSV row."""
        row_copy = row.copy()
        row_copy["is_active"] = row_copy.get("is_active", "true").lower() == "true"
        row_copy["opening_balance"] = float(row_copy.get("opening_balance", 0))
        return cls(**row_copy)

    def to_csv(self) -> dict:
        """Convert Account to CSV row."""
        data = self.model_dump()
        data["is_active"] = "true" if data["is_active"] else "false"
        return data

    class Config:
        from_attributes = True


# Field names for CSV
ACCOUNT_FIELDNAMES = [
    "id",
    "name",
    "type",
    "opening_balance",
    "is_active",
    "created_at",
]
