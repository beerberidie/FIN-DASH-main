"""Currency and exchange rate API endpoints."""

from typing import List, Optional
from datetime import date as date_type
from fastapi import APIRouter, HTTPException, Query, status

from models.currency import (
    Currency,
    CurrencyCreate,
    ExchangeRate,
    ExchangeRateCreate,
    ExchangeRateUpdate,
    CurrencyConversion,
    CurrencyConversionResult,
)
from services.currency_service import currency_service

router = APIRouter(prefix="/currencies", tags=["currencies"])


@router.get("", response_model=List[Currency])
def list_currencies(
    active_only: bool = Query(False, description="Only return active currencies")
):
    """
    List all currencies.

    Query Parameters:
    - **active_only**: If true, only return active currencies
    """
    return currency_service.list_currencies(active_only=active_only)


@router.get("/{code}", response_model=Currency)
def get_currency(code: str):
    """
    Get a currency by code.

    Path Parameters:
    - **code**: ISO 4217 currency code (e.g., ZAR, USD, EUR)
    """
    return currency_service.get_currency(code)


@router.post("", response_model=Currency, status_code=status.HTTP_201_CREATED)
def create_currency(currency_data: CurrencyCreate):
    """
    Create a new currency.

    Request Body:
    - **code**: ISO 4217 currency code (3 letters)
    - **name**: Currency name
    - **symbol**: Currency symbol
    - **is_active**: Whether the currency is active (default: true)
    """
    return currency_service.create_currency(currency_data)


# Exchange Rates Endpoints
@router.get("/exchange-rates/list", response_model=List[ExchangeRate])
def list_exchange_rates(
    from_currency: Optional[str] = Query(None, description="Filter by source currency"),
    to_currency: Optional[str] = Query(None, description="Filter by target currency"),
    date_from: Optional[date_type] = Query(None, description="Filter by start date"),
    date_to: Optional[date_type] = Query(None, description="Filter by end date"),
):
    """
    List exchange rates with optional filters.

    Query Parameters:
    - **from_currency**: Filter by source currency code
    - **to_currency**: Filter by target currency code
    - **date_from**: Filter by start date (YYYY-MM-DD)
    - **date_to**: Filter by end date (YYYY-MM-DD)
    """
    return currency_service.list_exchange_rates(
        from_currency=from_currency,
        to_currency=to_currency,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/exchange-rates/{rate_id}", response_model=ExchangeRate)
def get_exchange_rate(rate_id: str):
    """
    Get an exchange rate by ID.

    Path Parameters:
    - **rate_id**: Exchange rate ID
    """
    return currency_service.get_exchange_rate(rate_id)


@router.get(
    "/exchange-rates/latest/{from_currency}/{to_currency}", response_model=ExchangeRate
)
def get_latest_exchange_rate(from_currency: str, to_currency: str):
    """
    Get the latest exchange rate between two currencies.

    Path Parameters:
    - **from_currency**: Source currency code
    - **to_currency**: Target currency code
    """
    rate = currency_service.get_latest_rate(from_currency, to_currency)
    if not rate:
        raise HTTPException(
            status_code=404,
            detail=f"No exchange rate found for {from_currency} to {to_currency}",
        )
    return rate


@router.post(
    "/exchange-rates", response_model=ExchangeRate, status_code=status.HTTP_201_CREATED
)
def create_exchange_rate(rate_data: ExchangeRateCreate):
    """
    Create a new exchange rate.

    Request Body:
    - **from_currency**: Source currency code (3 letters)
    - **to_currency**: Target currency code (3 letters)
    - **rate**: Exchange rate (1 from_currency = rate to_currency)
    - **date**: Date of the exchange rate
    - **source**: Source of the rate (default: "manual")
    """
    return currency_service.create_exchange_rate(rate_data)


@router.put("/exchange-rates/{rate_id}", response_model=ExchangeRate)
def update_exchange_rate(rate_id: str, rate_update: ExchangeRateUpdate):
    """
    Update an exchange rate.

    Path Parameters:
    - **rate_id**: Exchange rate ID

    Request Body:
    - **rate**: New exchange rate (optional)
    - **date**: New date (optional)
    - **source**: New source (optional)
    """
    return currency_service.update_exchange_rate(rate_id, rate_update)


@router.delete("/exchange-rates/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exchange_rate(rate_id: str):
    """
    Delete an exchange rate.

    Path Parameters:
    - **rate_id**: Exchange rate ID
    """
    currency_service.delete_exchange_rate(rate_id)
    return None


@router.post("/convert", response_model=CurrencyConversionResult)
def convert_currency(conversion: CurrencyConversion):
    """
    Convert an amount from one currency to another.

    Request Body:
    - **amount**: Amount to convert
    - **from_currency**: Source currency code
    - **to_currency**: Target currency code
    - **date**: Date for the conversion (optional, uses latest rate if not provided)

    Returns:
    - Conversion result with original amount, exchange rate, and converted amount
    """
    return currency_service.convert_currency(conversion)
