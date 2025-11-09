"""Card models for payment method tracking."""
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


class CardBase(BaseModel):
    """Base card model."""
    name: str = Field(..., min_length=1, max_length=100, description="Card name (e.g., 'Visa Gold Card')")
    card_type: Literal["credit", "debit", "prepaid", "virtual"] = Field(..., description="Type of card")
    last_four_digits: str = Field(..., min_length=4, max_length=4, description="Last 4 digits of card number")
    account_id: str = Field(..., description="Linked account ID")
    issuer: str = Field(..., min_length=1, max_length=100, description="Card issuer (e.g., 'Standard Bank')")
    available_balance: float = Field(default=0.0, description="Available balance/credit")
    current_balance: float = Field(default=0.0, description="Current balance (negative for credit cards)")
    credit_limit: Optional[float] = Field(default=None, ge=0, description="Credit limit for credit cards")
    expiry_month: Optional[int] = Field(default=None, ge=1, le=12, description="Expiry month (1-12)")
    expiry_year: Optional[int] = Field(default=None, ge=2000, le=2100, description="Expiry year")
    is_active: bool = Field(default=True, description="Whether card is active")
    color: str = Field(default="#3b82f6", pattern=r'^#[0-9A-Fa-f]{6}$', description="Card color (hex)")
    icon: str = Field(default="CreditCard", max_length=50, description="Icon name")
    
    @field_validator('last_four_digits')
    @classmethod
    def validate_last_four_digits(cls, v):
        """Validate last four digits are numeric."""
        if not v.isdigit():
            raise ValueError('Last four digits must be numeric')
        return v


class CardCreate(CardBase):
    """Model for creating a card."""
    pass


class CardUpdate(BaseModel):
    """Model for updating a card."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    card_type: Optional[Literal["credit", "debit", "prepaid", "virtual"]] = None
    last_four_digits: Optional[str] = Field(None, min_length=4, max_length=4)
    account_id: Optional[str] = None
    issuer: Optional[str] = Field(None, min_length=1, max_length=100)
    available_balance: Optional[float] = None
    current_balance: Optional[float] = None
    credit_limit: Optional[float] = Field(None, ge=0)
    expiry_month: Optional[int] = Field(None, ge=1, le=12)
    expiry_year: Optional[int] = Field(None, ge=2000, le=2100)
    is_active: Optional[bool] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=50)


class Card(CardBase):
    """Full card model with ID and timestamps."""
    id: str
    created_at: str
    updated_at: str
    
    @classmethod
    def from_csv(cls, row: dict) -> "Card":
        """Create Card from CSV row."""
        row_copy = row.copy()
        
        # Convert boolean
        row_copy['is_active'] = str(row_copy.get('is_active', 'true')).lower() == 'true'
        
        # Convert numeric fields
        row_copy['available_balance'] = float(row_copy.get('available_balance', 0))
        row_copy['current_balance'] = float(row_copy.get('current_balance', 0))
        
        # Handle optional credit_limit
        credit_limit = row_copy.get('credit_limit', '')
        row_copy['credit_limit'] = float(credit_limit) if credit_limit and credit_limit != '' else None
        
        # Handle optional expiry fields
        expiry_month = row_copy.get('expiry_month', '')
        row_copy['expiry_month'] = int(expiry_month) if expiry_month and expiry_month != '' else None
        
        expiry_year = row_copy.get('expiry_year', '')
        row_copy['expiry_year'] = int(expiry_year) if expiry_year and expiry_year != '' else None
        
        return cls(**row_copy)
    
    def to_csv(self) -> dict:
        """Convert Card to CSV row."""
        data = self.model_dump()
        
        # Convert boolean to string
        data['is_active'] = 'true' if data['is_active'] else 'false'
        
        # Convert None to empty string for CSV
        data['credit_limit'] = str(data['credit_limit']) if data['credit_limit'] is not None else ''
        data['expiry_month'] = str(data['expiry_month']) if data['expiry_month'] is not None else ''
        data['expiry_year'] = str(data['expiry_year']) if data['expiry_year'] is not None else ''
        
        return data
    
    class Config:
        from_attributes = True


# Field names for CSV
CARD_FIELDNAMES = [
    'id', 'name', 'card_type', 'last_four_digits', 'account_id', 'issuer',
    'available_balance', 'current_balance', 'credit_limit', 'expiry_month', 'expiry_year',
    'is_active', 'color', 'icon', 'created_at', 'updated_at'
]

