"""Currency and exchange rate management service."""
from typing import List, Dict, Optional
from datetime import date as date_type, datetime
from fastapi import HTTPException

from models.currency import (
    Currency, CurrencyCreate, ExchangeRate, ExchangeRateCreate, ExchangeRateUpdate,
    CurrencyConversion, CurrencyConversionResult, CURRENCY_FIELDNAMES, 
    EXCHANGE_RATE_FIELDNAMES, DEFAULT_CURRENCIES
)
from services.csv_manager import csv_manager
from utils.ids import generate_uuid
from utils.dates import now_iso


class CurrencyService:
    """Service for managing currencies and exchange rates."""
    
    def __init__(self):
        """Initialize currency service and ensure default currencies exist."""
        self._ensure_default_currencies()
    
    def _ensure_default_currencies(self):
        """Ensure default currencies are initialized in the CSV file."""
        currencies = csv_manager.read_csv("currencies.csv")
        
        if not currencies:
            # Initialize with default currencies
            timestamp = now_iso()
            for curr_data in DEFAULT_CURRENCIES:
                currency_row = {
                    'code': curr_data['code'],
                    'name': curr_data['name'],
                    'symbol': curr_data['symbol'],
                    'is_active': 'true',
                    'created_at': timestamp,
                    'updated_at': timestamp
                }
                csv_manager.append_csv("currencies.csv", currency_row, CURRENCY_FIELDNAMES)
    
    def list_currencies(self, active_only: bool = False) -> List[Currency]:
        """
        List all currencies.
        
        Args:
            active_only: If True, only return active currencies
            
        Returns:
            List of Currency objects
        """
        currencies = csv_manager.read_csv("currencies.csv")
        
        if active_only:
            currencies = [c for c in currencies if c.get('is_active', 'true').lower() == 'true']
        
        return [Currency.from_csv(c) for c in currencies]
    
    def get_currency(self, code: str) -> Currency:
        """
        Get a currency by code.
        
        Args:
            code: Currency code (e.g., 'ZAR', 'USD')
            
        Returns:
            Currency object
            
        Raises:
            HTTPException: If currency not found
        """
        currencies = csv_manager.read_csv("currencies.csv")
        
        for curr in currencies:
            if curr.get('code', '').upper() == code.upper():
                return Currency.from_csv(curr)
        
        raise HTTPException(status_code=404, detail=f"Currency {code} not found")
    
    def create_currency(self, currency_data: CurrencyCreate) -> Currency:
        """
        Create a new currency.
        
        Args:
            currency_data: Currency creation data
            
        Returns:
            Created Currency object
            
        Raises:
            HTTPException: If currency already exists
        """
        # Check if currency already exists
        currencies = csv_manager.read_csv("currencies.csv")
        for curr in currencies:
            if curr.get('code', '').upper() == currency_data.code.upper():
                raise HTTPException(
                    status_code=400, 
                    detail=f"Currency {currency_data.code} already exists"
                )
        
        # Create currency
        timestamp = now_iso()
        currency_row = {
            'code': currency_data.code.upper(),
            'name': currency_data.name,
            'symbol': currency_data.symbol,
            'is_active': str(currency_data.is_active).lower(),
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        csv_manager.append_csv("currencies.csv", currency_row, CURRENCY_FIELDNAMES)
        
        return Currency.from_csv(currency_row)
    
    def list_exchange_rates(
        self,
        from_currency: Optional[str] = None,
        to_currency: Optional[str] = None,
        date_from: Optional[date_type] = None,
        date_to: Optional[date_type] = None
    ) -> List[ExchangeRate]:
        """
        List exchange rates with optional filters.
        
        Args:
            from_currency: Filter by source currency
            to_currency: Filter by target currency
            date_from: Filter by start date
            date_to: Filter by end date
            
        Returns:
            List of ExchangeRate objects
        """
        rates = csv_manager.read_csv("exchange_rates.csv")
        
        # Apply filters
        filtered_rates = []
        for rate in rates:
            # Currency filters
            if from_currency and rate.get('from_currency', '').upper() != from_currency.upper():
                continue
            if to_currency and rate.get('to_currency', '').upper() != to_currency.upper():
                continue
            
            # Date filters
            rate_date = rate.get('date', '')
            if date_from and rate_date < str(date_from):
                continue
            if date_to and rate_date > str(date_to):
                continue
            
            filtered_rates.append(rate)
        
        return [ExchangeRate.from_csv(r) for r in filtered_rates]
    
    def get_exchange_rate(self, rate_id: str) -> ExchangeRate:
        """
        Get an exchange rate by ID.
        
        Args:
            rate_id: Exchange rate ID
            
        Returns:
            ExchangeRate object
            
        Raises:
            HTTPException: If rate not found
        """
        rates = csv_manager.read_csv("exchange_rates.csv")
        
        for rate in rates:
            if rate.get('id') == rate_id:
                return ExchangeRate.from_csv(rate)
        
        raise HTTPException(status_code=404, detail="Exchange rate not found")
    
    def get_latest_rate(self, from_currency: str, to_currency: str) -> Optional[ExchangeRate]:
        """
        Get the latest exchange rate between two currencies.
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Latest ExchangeRate object or None if not found
        """
        rates = self.list_exchange_rates(
            from_currency=from_currency,
            to_currency=to_currency
        )
        
        if not rates:
            return None
        
        # Sort by date descending and return the latest
        rates.sort(key=lambda r: r.date, reverse=True)
        return rates[0]
    
    def create_exchange_rate(self, rate_data: ExchangeRateCreate) -> ExchangeRate:
        """
        Create a new exchange rate.
        
        Args:
            rate_data: Exchange rate creation data
            
        Returns:
            Created ExchangeRate object
        """
        # Validate currencies exist
        self.get_currency(rate_data.from_currency)
        self.get_currency(rate_data.to_currency)

        # Generate ID and timestamps
        rate_id = f"exrate_{generate_uuid()[:8]}"
        timestamp = now_iso()
        
        rate_row = {
            'id': rate_id,
            'from_currency': rate_data.from_currency.upper(),
            'to_currency': rate_data.to_currency.upper(),
            'rate': str(rate_data.rate),
            'date': str(rate_data.date),
            'source': rate_data.source,
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        csv_manager.append_csv("exchange_rates.csv", rate_row, EXCHANGE_RATE_FIELDNAMES)
        
        return ExchangeRate.from_csv(rate_row)
    
    def update_exchange_rate(self, rate_id: str, rate_update: ExchangeRateUpdate) -> ExchangeRate:
        """
        Update an exchange rate.
        
        Args:
            rate_id: Exchange rate ID
            rate_update: Update data
            
        Returns:
            Updated ExchangeRate object
        """
        rates = csv_manager.read_csv("exchange_rates.csv")
        
        updated = False
        for i, rate in enumerate(rates):
            if rate.get('id') == rate_id:
                # Update fields
                if rate_update.rate is not None:
                    rate['rate'] = str(rate_update.rate)
                if rate_update.date is not None:
                    rate['date'] = str(rate_update.date)
                if rate_update.source is not None:
                    rate['source'] = rate_update.source
                
                rate['updated_at'] = now_iso()
                rates[i] = rate
                updated = True
                break
        
        if not updated:
            raise HTTPException(status_code=404, detail="Exchange rate not found")
        
        csv_manager.write_csv("exchange_rates.csv", rates, EXCHANGE_RATE_FIELDNAMES)
        
        return ExchangeRate.from_csv(rates[i])
    
    def delete_exchange_rate(self, rate_id: str) -> None:
        """
        Delete an exchange rate.
        
        Args:
            rate_id: Exchange rate ID
            
        Raises:
            HTTPException: If rate not found
        """
        rates = csv_manager.read_csv("exchange_rates.csv")
        
        filtered_rates = [r for r in rates if r.get('id') != rate_id]
        
        if len(filtered_rates) == len(rates):
            raise HTTPException(status_code=404, detail="Exchange rate not found")
        
        csv_manager.write_csv("exchange_rates.csv", filtered_rates, EXCHANGE_RATE_FIELDNAMES)
    
    def convert_currency(self, conversion: CurrencyConversion) -> CurrencyConversionResult:
        """
        Convert an amount from one currency to another.
        
        Args:
            conversion: Conversion request
            
        Returns:
            CurrencyConversionResult with converted amount
            
        Raises:
            HTTPException: If exchange rate not found
        """
        # If same currency, return as-is
        if conversion.from_currency.upper() == conversion.to_currency.upper():
            return CurrencyConversionResult(
                original_amount=conversion.amount,
                from_currency=conversion.from_currency.upper(),
                to_currency=conversion.to_currency.upper(),
                exchange_rate=1.0,
                converted_amount=conversion.amount,
                conversion_date=conversion.date or date_type.today()
            )
        
        # Get exchange rate
        if conversion.date:
            # Find rate for specific date
            rates = self.list_exchange_rates(
                from_currency=conversion.from_currency,
                to_currency=conversion.to_currency,
                date_from=conversion.date,
                date_to=conversion.date
            )
            if not rates:
                raise HTTPException(
                    status_code=404,
                    detail=f"No exchange rate found for {conversion.from_currency} to {conversion.to_currency} on {conversion.date}"
                )
            rate = rates[0]
        else:
            # Use latest rate
            rate = self.get_latest_rate(conversion.from_currency, conversion.to_currency)
            if not rate:
                raise HTTPException(
                    status_code=404,
                    detail=f"No exchange rate found for {conversion.from_currency} to {conversion.to_currency}"
                )
        
        # Calculate converted amount
        converted_amount = conversion.amount * rate.rate
        
        return CurrencyConversionResult(
            original_amount=conversion.amount,
            from_currency=conversion.from_currency.upper(),
            to_currency=conversion.to_currency.upper(),
            exchange_rate=rate.rate,
            converted_amount=converted_amount,
            conversion_date=rate.date
        )


# Singleton instance
currency_service = CurrencyService()

