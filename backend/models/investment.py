"""Investment and portfolio models."""

from datetime import date as date_type
from typing import Optional, Literal
from pydantic import BaseModel, Field


# Investment Types
InvestmentType = Literal["stock", "etf", "crypto", "bond", "mutual_fund", "other"]

# CSV Field Names
INVESTMENT_FIELDNAMES = [
    "id",
    "symbol",
    "name",
    "type",
    "currency",
    "quantity",
    "average_cost",
    "current_price",
    "last_updated",
    "notes",
    "created_at",
    "updated_at",
]

INVESTMENT_TRANSACTION_FIELDNAMES = [
    "id",
    "investment_id",
    "date",
    "type",
    "quantity",
    "price",
    "fees",
    "total_amount",
    "notes",
    "created_at",
    "updated_at",
]


class InvestmentBase(BaseModel):
    """Base investment model."""

    symbol: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Stock/crypto symbol (e.g., AAPL, BTC)",
    )
    name: str = Field(..., min_length=1, max_length=200, description="Investment name")
    type: InvestmentType = Field(..., description="Type of investment")
    currency: str = Field(
        default="USD", min_length=3, max_length=3, description="Currency code"
    )
    quantity: float = Field(default=0.0, ge=0, description="Current quantity held")
    average_cost: float = Field(default=0.0, ge=0, description="Average cost per unit")
    current_price: float = Field(
        default=0.0, ge=0, description="Current market price per unit"
    )
    last_updated: str = Field(..., description="Last price update date (YYYY-MM-DD)")
    notes: Optional[str] = Field(default="", description="Additional notes")


class Investment(InvestmentBase):
    """Investment model with ID and timestamps."""

    id: str
    created_at: str
    updated_at: str

    @classmethod
    def from_csv(cls, row: dict) -> "Investment":
        """Create Investment from CSV row."""
        row_copy = row.copy()
        # Convert numeric fields
        row_copy["quantity"] = float(row_copy.get("quantity", 0))
        row_copy["average_cost"] = float(row_copy.get("average_cost", 0))
        row_copy["current_price"] = float(row_copy.get("current_price", 0))
        return cls(**row_copy)

    def to_csv(self) -> dict:
        """Convert Investment to CSV row."""
        data = self.model_dump()
        # Convert all values to strings for CSV
        return {k: str(v) for k, v in data.items()}

    class Config:
        from_attributes = True


class InvestmentCreate(InvestmentBase):
    """Model for creating an investment."""

    pass


class InvestmentUpdate(BaseModel):
    """Model for updating an investment."""

    name: Optional[str] = None
    type: Optional[InvestmentType] = None
    currency: Optional[str] = None
    quantity: Optional[float] = Field(None, ge=0)
    average_cost: Optional[float] = Field(None, ge=0)
    current_price: Optional[float] = Field(None, ge=0)
    last_updated: Optional[str] = None
    notes: Optional[str] = None


class InvestmentTransactionBase(BaseModel):
    """Base investment transaction model."""

    investment_id: str = Field(..., description="ID of the investment")
    date: date_type = Field(..., description="Transaction date")
    type: Literal["buy", "sell"] = Field(..., description="Transaction type")
    quantity: float = Field(..., gt=0, description="Quantity bought/sold")
    price: float = Field(..., gt=0, description="Price per unit")
    fees: float = Field(default=0.0, ge=0, description="Transaction fees")
    total_amount: float = Field(
        ...,
        description="Total amount (quantity * price + fees for buy, quantity * price - fees for sell)",
    )
    notes: Optional[str] = Field(default="", description="Transaction notes")


class InvestmentTransaction(InvestmentTransactionBase):
    """Investment transaction model with ID and timestamps."""

    id: str
    created_at: str
    updated_at: str

    @classmethod
    def from_csv(cls, row: dict) -> "InvestmentTransaction":
        """Create InvestmentTransaction from CSV row."""
        row_copy = row.copy()
        # Convert numeric fields
        row_copy["quantity"] = float(row_copy.get("quantity", 0))
        row_copy["price"] = float(row_copy.get("price", 0))
        row_copy["fees"] = float(row_copy.get("fees", 0))
        row_copy["total_amount"] = float(row_copy.get("total_amount", 0))
        return cls(**row_copy)

    def to_csv(self) -> dict:
        """Convert InvestmentTransaction to CSV row."""
        data = self.model_dump()
        # Convert date to string
        if isinstance(data["date"], date_type):
            data["date"] = str(data["date"])
        # Convert all values to strings for CSV
        return {k: str(v) for k, v in data.items()}

    class Config:
        from_attributes = True


class InvestmentTransactionCreate(InvestmentTransactionBase):
    """Model for creating an investment transaction."""

    pass


class PortfolioSummary(BaseModel):
    """Portfolio summary with performance metrics."""

    total_investments: int
    total_value: float
    total_cost: float
    total_profit_loss: float
    total_profit_loss_percentage: float
    currency: str
    by_type: dict[str, dict]  # Asset allocation by type
    top_performers: list[dict]  # Top 5 performing investments
    worst_performers: list[dict]  # Bottom 5 performing investments


class InvestmentPerformance(BaseModel):
    """Individual investment performance metrics."""

    investment_id: str
    symbol: str
    name: str
    type: str
    quantity: float
    average_cost: float
    current_price: float
    total_cost: float
    current_value: float
    profit_loss: float
    profit_loss_percentage: float
    currency: str


class PriceUpdate(BaseModel):
    """Model for updating investment price."""

    current_price: float = Field(..., gt=0, description="New current price")
    last_updated: Optional[str] = Field(
        None, description="Update date (defaults to today)"
    )
