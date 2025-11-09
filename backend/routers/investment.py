"""Investment and portfolio API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from models.investment import (
    Investment, InvestmentCreate, InvestmentUpdate,
    InvestmentTransaction, InvestmentTransactionCreate,
    InvestmentPerformance, PortfolioSummary, PriceUpdate
)
from services.investment_service import investment_service
from services.portfolio_service import portfolio_service

router = APIRouter(prefix="/investments", tags=["investments"])


# Investment Endpoints

@router.get("", response_model=List[Investment])
def list_investments(
    type: Optional[str] = Query(None, description="Filter by investment type"),
    symbol: Optional[str] = Query(None, description="Filter by symbol (partial match)")
):
    """
    List all investments with optional filters.
    
    Query Parameters:
    - **type**: Filter by investment type (stock, etf, crypto, bond, mutual_fund, other)
    - **symbol**: Filter by symbol (case-insensitive partial match)
    """
    return investment_service.list_investments(type_filter=type, symbol_filter=symbol)


@router.get("/{investment_id}", response_model=Investment)
def get_investment(investment_id: str):
    """
    Get a specific investment by ID.
    
    Path Parameters:
    - **investment_id**: Investment ID
    """
    return investment_service.get_investment(investment_id)


@router.post("", response_model=Investment, status_code=status.HTTP_201_CREATED)
def create_investment(investment_data: InvestmentCreate):
    """
    Create a new investment.
    
    Request Body:
    - **symbol**: Stock/crypto symbol (e.g., AAPL, BTC)
    - **name**: Investment name
    - **type**: Type of investment (stock, etf, crypto, bond, mutual_fund, other)
    - **currency**: Currency code (default: USD)
    - **quantity**: Initial quantity (default: 0)
    - **average_cost**: Average cost per unit (default: 0)
    - **current_price**: Current market price (default: 0)
    - **last_updated**: Last price update date
    - **notes**: Additional notes (optional)
    """
    return investment_service.create_investment(investment_data)


@router.put("/{investment_id}", response_model=Investment)
def update_investment(investment_id: str, investment_update: InvestmentUpdate):
    """
    Update an investment.
    
    Path Parameters:
    - **investment_id**: Investment ID
    
    Request Body: Any fields to update
    """
    return investment_service.update_investment(investment_id, investment_update)


@router.patch("/{investment_id}/price", response_model=Investment)
def update_price(investment_id: str, price_update: PriceUpdate):
    """
    Update investment price.
    
    Path Parameters:
    - **investment_id**: Investment ID
    
    Request Body:
    - **current_price**: New current price
    - **last_updated**: Update date (optional, defaults to today)
    """
    return investment_service.update_price(investment_id, price_update)


@router.delete("/{investment_id}")
def delete_investment(investment_id: str):
    """
    Delete an investment and all its transactions.
    
    Path Parameters:
    - **investment_id**: Investment ID
    """
    return investment_service.delete_investment(investment_id)


# Investment Transaction Endpoints

@router.get("/transactions/list", response_model=List[InvestmentTransaction])
def list_transactions(
    investment_id: Optional[str] = Query(None, description="Filter by investment ID")
):
    """
    List investment transactions.
    
    Query Parameters:
    - **investment_id**: Filter by investment ID (optional)
    """
    return investment_service.list_transactions(investment_id=investment_id)


@router.get("/transactions/{transaction_id}", response_model=InvestmentTransaction)
def get_transaction(transaction_id: str):
    """
    Get a specific transaction by ID.
    
    Path Parameters:
    - **transaction_id**: Transaction ID
    """
    return investment_service.get_transaction(transaction_id)


@router.post("/transactions", response_model=InvestmentTransaction, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_data: InvestmentTransactionCreate):
    """
    Create a new investment transaction (buy or sell).
    This will automatically update the investment's quantity and average cost.
    
    Request Body:
    - **investment_id**: ID of the investment
    - **date**: Transaction date
    - **type**: Transaction type (buy or sell)
    - **quantity**: Quantity bought/sold
    - **price**: Price per unit
    - **fees**: Transaction fees (default: 0)
    - **total_amount**: Total amount (quantity * price ± fees)
    - **notes**: Transaction notes (optional)
    """
    return investment_service.create_transaction(transaction_data)


@router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: str):
    """
    Delete an investment transaction.
    Note: This does NOT reverse the quantity/cost changes.
    
    Path Parameters:
    - **transaction_id**: Transaction ID
    """
    return investment_service.delete_transaction(transaction_id)


# Performance and Analytics Endpoints

@router.get("/{investment_id}/performance", response_model=InvestmentPerformance)
def get_investment_performance(investment_id: str):
    """
    Get performance metrics for a specific investment.
    
    Path Parameters:
    - **investment_id**: Investment ID
    
    Returns:
    - Quantity, costs, current value, profit/loss, and percentage returns
    """
    return investment_service.get_investment_performance(investment_id)


@router.get("/portfolio/summary", response_model=PortfolioSummary)
def get_portfolio_summary(
    base_currency: str = Query("USD", description="Base currency for reporting")
):
    """
    Get comprehensive portfolio summary with performance metrics.
    
    Query Parameters:
    - **base_currency**: Base currency for reporting (default: USD)
    
    Returns:
    - Total investments, value, cost, profit/loss
    - Asset allocation by type
    - Top and worst performers
    """
    return portfolio_service.get_portfolio_summary(base_currency)


@router.get("/portfolio/allocation")
def get_asset_allocation():
    """
    Get asset allocation percentages by investment type.
    
    Returns:
    - Dictionary mapping investment type to percentage of portfolio
    """
    return portfolio_service.get_asset_allocation()


@router.get("/portfolio/value")
def get_portfolio_value(
    base_currency: str = Query("USD", description="Base currency for reporting")
):
    """
    Get total portfolio value.
    
    Query Parameters:
    - **base_currency**: Base currency for reporting (default: USD)
    
    Returns:
    - Total portfolio value in specified currency
    """
    return {
        "total_value": portfolio_service.get_total_portfolio_value(base_currency),
        "currency": base_currency
    }


@router.get("/portfolio/profit-loss")
def get_portfolio_profit_loss(
    base_currency: str = Query("USD", description="Base currency for reporting")
):
    """
    Get portfolio profit/loss metrics.
    
    Query Parameters:
    - **base_currency**: Base currency for reporting (default: USD)
    
    Returns:
    - Total cost, value, profit/loss amount and percentage
    """
    return portfolio_service.get_portfolio_profit_loss(base_currency)


@router.get("/by-type/{investment_type}", response_model=List[InvestmentPerformance])
def get_investments_by_type(investment_type: str):
    """
    Get all investments of a specific type with performance metrics.
    
    Path Parameters:
    - **investment_type**: Type of investment (stock, etf, crypto, bond, mutual_fund, other)
    
    Returns:
    - List of investments with performance metrics, sorted by value
    """
    return portfolio_service.get_investments_by_type(investment_type)

