"""Currency and exchange rate models."""

from datetime import date as date_type
from typing import Optional
from pydantic import BaseModel, Field


class Currency(BaseModel):
    """Currency model."""

    code: str = Field(
        ...,
        min_length=3,
        max_length=3,
        description="ISO 4217 currency code (e.g., ZAR, USD)",
    )
    name: str = Field(..., min_length=1, max_length=100, description="Currency name")
    symbol: str = Field(
        ..., min_length=1, max_length=10, description="Currency symbol (e.g., R, $)"
    )
    is_active: bool = True
    created_at: str
    updated_at: str

    @classmethod
    def from_csv(cls, row: dict) -> "Currency":
        """Create Currency from CSV row."""
        # Handle boolean conversion
        row_copy = row.copy()
        if "is_active" in row_copy:
            row_copy["is_active"] = str(row_copy["is_active"]).lower() == "true"
        return cls(**row_copy)

    def to_csv(self) -> dict:
        """Convert Currency to CSV row."""
        data = self.model_dump()
        # Convert boolean to string for CSV
        data["is_active"] = str(data["is_active"]).lower()
        return data

    class Config:
        from_attributes = True


class CurrencyCreate(BaseModel):
    """Model for creating a currency."""

    code: str = Field(
        ..., min_length=3, max_length=3, description="ISO 4217 currency code"
    )
    name: str = Field(..., min_length=1, max_length=100)
    symbol: str = Field(..., min_length=1, max_length=10)
    is_active: bool = True


class ExchangeRate(BaseModel):
    """Exchange rate model."""

    id: str
    from_currency: str = Field(
        ..., min_length=3, max_length=3, description="Source currency code"
    )
    to_currency: str = Field(
        ..., min_length=3, max_length=3, description="Target currency code"
    )
    rate: float = Field(
        ..., gt=0, description="Exchange rate (1 from_currency = rate to_currency)"
    )
    date: date_type = Field(..., description="Date of the exchange rate")
    source: str = Field(
        default="manual", description="Source of rate: manual, api, etc."
    )
    created_at: str
    updated_at: str

    @classmethod
    def from_csv(cls, row: dict) -> "ExchangeRate":
        """Create ExchangeRate from CSV row."""
        return cls(**row)

    def to_csv(self) -> dict:
        """Convert ExchangeRate to CSV row."""
        data = self.model_dump()
        # Convert date to string for CSV
        if isinstance(data["date"], date_type):
            data["date"] = str(data["date"])
        return data

    class Config:
        from_attributes = True


class ExchangeRateCreate(BaseModel):
    """Model for creating an exchange rate."""

    from_currency: str = Field(..., min_length=3, max_length=3)
    to_currency: str = Field(..., min_length=3, max_length=3)
    rate: float = Field(..., gt=0)
    date: date_type
    source: str = "manual"


class ExchangeRateUpdate(BaseModel):
    """Model for updating an exchange rate."""

    rate: Optional[float] = Field(None, gt=0)
    date: Optional[date_type] = None
    source: Optional[str] = None


class CurrencyConversion(BaseModel):
    """Model for currency conversion request."""

    amount: float
    from_currency: str = Field(..., min_length=3, max_length=3)
    to_currency: str = Field(..., min_length=3, max_length=3)
    date: Optional[date_type] = None  # If None, use latest rate


class CurrencyConversionResult(BaseModel):
    """Model for currency conversion result."""

    original_amount: float
    from_currency: str
    to_currency: str
    exchange_rate: float
    converted_amount: float
    conversion_date: date_type


# Field names for CSV
CURRENCY_FIELDNAMES = [
    "code",
    "name",
    "symbol",
    "is_active",
    "created_at",
    "updated_at",
]

EXCHANGE_RATE_FIELDNAMES = [
    "id",
    "from_currency",
    "to_currency",
    "rate",
    "date",
    "source",
    "created_at",
    "updated_at",
]


# Default supported currencies
DEFAULT_CURRENCIES = [
    {"code": "ZAR", "name": "South African Rand", "symbol": "R"},
    {"code": "USD", "name": "US Dollar", "symbol": "$"},
    {"code": "EUR", "name": "Euro", "symbol": "€"},
    {"code": "GBP", "name": "British Pound", "symbol": "£"},
    {"code": "JPY", "name": "Japanese Yen", "symbol": "¥"},
    {"code": "AUD", "name": "Australian Dollar", "symbol": "A$"},
    {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$"},
    {"code": "CHF", "name": "Swiss Franc", "symbol": "CHF"},
    {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥"},
    {"code": "INR", "name": "Indian Rupee", "symbol": "₹"},
]
