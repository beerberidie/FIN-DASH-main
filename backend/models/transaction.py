"""Transaction models."""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from utils.validation import validate_transaction_type


class TransactionBase(BaseModel):
    """Base transaction model."""
    date: date
    description: str = Field(..., min_length=1, max_length=500)
    amount: float
    category_id: Optional[str] = None
    account_id: str
    card_id: Optional[str] = None  # Link to payment card
    type: str  # 'income' or 'expense'
    currency: str = Field(default="ZAR", min_length=3, max_length=3, description="ISO 4217 currency code")
    source: str = "manual"  # 'manual', 'csv', 'ocr', 'api'
    external_id: Optional[str] = None
    tags: str = ""  # Semicolon-separated tags
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        validate_transaction_type(v)
        return v
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v, info):
        # Get the type from the data being validated
        data = info.data
        transaction_type = data.get('type')
        
        if transaction_type == 'income' and v < 0:
            raise ValueError('Income amount must be positive')
        if transaction_type == 'expense' and v > 0:
            raise ValueError('Expense amount must be negative')
        
        return v


class TransactionCreate(TransactionBase):
    """Model for creating a transaction."""
    pass


class TransactionUpdate(BaseModel):
    """Model for updating a transaction."""
    date: Optional[date] = None
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    amount: Optional[float] = None
    category_id: Optional[str] = None
    account_id: Optional[str] = None
    type: Optional[str] = None
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    tags: Optional[str] = None


class Transaction(TransactionBase):
    """Full transaction model with ID and timestamps."""
    id: str
    created_at: str
    updated_at: str

    @classmethod
    def from_csv(cls, row: dict) -> "Transaction":
        """Create Transaction from CSV row."""
        # Ensure backward compatibility: default to ZAR if currency not present
        row_copy = row.copy()
        if 'currency' not in row_copy or not row_copy['currency']:
            row_copy['currency'] = 'ZAR'
        return cls(**row_copy)
    
    def to_csv(self) -> dict:
        """Convert Transaction to CSV row."""
        return self.model_dump()
    
    class Config:
        from_attributes = True


# Field names for CSV
TRANSACTION_FIELDNAMES = [
    'id', 'date', 'description', 'amount', 'category_id', 'account_id', 'card_id',
    'type', 'currency', 'source', 'external_id', 'tags', 'created_at', 'updated_at'
]

