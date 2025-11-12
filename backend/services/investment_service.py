"""Investment management service."""

from typing import List, Optional
from datetime import date as date_type
from fastapi import HTTPException

from models.investment import (
    Investment,
    InvestmentCreate,
    InvestmentUpdate,
    InvestmentTransaction,
    InvestmentTransactionCreate,
    InvestmentPerformance,
    PriceUpdate,
    INVESTMENT_FIELDNAMES,
    INVESTMENT_TRANSACTION_FIELDNAMES,
)
from services.csv_manager import csv_manager
from utils.ids import generate_uuid
from utils.dates import now_iso


class InvestmentService:
    """Service for managing investments and transactions."""

    def __init__(self):
        """Initialize investment service and ensure CSV files exist."""
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Ensure investment CSV files exist."""
        # Check if investments.csv exists
        try:
            csv_manager.read_csv("investments.csv")
        except FileNotFoundError:
            csv_manager.write_csv("investments.csv", [], INVESTMENT_FIELDNAMES)

        # Check if investment_transactions.csv exists
        try:
            csv_manager.read_csv("investment_transactions.csv")
        except FileNotFoundError:
            csv_manager.write_csv(
                "investment_transactions.csv", [], INVESTMENT_TRANSACTION_FIELDNAMES
            )

    # Investment CRUD Operations

    def list_investments(
        self, type_filter: Optional[str] = None, symbol_filter: Optional[str] = None
    ) -> List[Investment]:
        """
        List all investments with optional filters.

        Args:
            type_filter: Filter by investment type
            symbol_filter: Filter by symbol (partial match)

        Returns:
            List of Investment objects
        """
        investments = csv_manager.read_csv("investments.csv")

        filtered = []
        for inv in investments:
            # Type filter
            if type_filter and inv.get("type") != type_filter:
                continue

            # Symbol filter (case-insensitive partial match)
            if symbol_filter:
                symbol = inv.get("symbol", "").upper()
                if symbol_filter.upper() not in symbol:
                    continue

            filtered.append(inv)

        return [Investment.from_csv(inv) for inv in filtered]

    def get_investment(self, investment_id: str) -> Investment:
        """
        Get an investment by ID.

        Args:
            investment_id: Investment ID

        Returns:
            Investment object

        Raises:
            HTTPException: If investment not found
        """
        investments = csv_manager.read_csv("investments.csv")

        for inv in investments:
            if inv.get("id") == investment_id:
                return Investment.from_csv(inv)

        raise HTTPException(
            status_code=404, detail=f"Investment {investment_id} not found"
        )

    def get_investment_by_symbol(self, symbol: str) -> Optional[Investment]:
        """
        Get an investment by symbol.

        Args:
            symbol: Investment symbol

        Returns:
            Investment object or None if not found
        """
        investments = csv_manager.read_csv("investments.csv")

        for inv in investments:
            if inv.get("symbol", "").upper() == symbol.upper():
                return Investment.from_csv(inv)

        return None

    def create_investment(self, investment_data: InvestmentCreate) -> Investment:
        """
        Create a new investment.

        Args:
            investment_data: Investment creation data

        Returns:
            Created Investment object
        """
        # Generate ID and timestamps
        investment_id = f"inv_{generate_uuid()[:8]}"
        timestamp = now_iso()

        investment_row = {
            "id": investment_id,
            "symbol": investment_data.symbol.upper(),
            "name": investment_data.name,
            "type": investment_data.type,
            "currency": investment_data.currency.upper(),
            "quantity": str(investment_data.quantity),
            "average_cost": str(investment_data.average_cost),
            "current_price": str(investment_data.current_price),
            "last_updated": investment_data.last_updated,
            "notes": investment_data.notes or "",
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        csv_manager.append_csv("investments.csv", investment_row, INVESTMENT_FIELDNAMES)

        return Investment.from_csv(investment_row)

    def update_investment(
        self, investment_id: str, investment_update: InvestmentUpdate
    ) -> Investment:
        """
        Update an investment.

        Args:
            investment_id: Investment ID
            investment_update: Update data

        Returns:
            Updated Investment object

        Raises:
            HTTPException: If investment not found
        """
        investments = csv_manager.read_csv("investments.csv")
        updated = False

        for inv in investments:
            if inv.get("id") == investment_id:
                # Update fields
                if investment_update.name is not None:
                    inv["name"] = investment_update.name
                if investment_update.type is not None:
                    inv["type"] = investment_update.type
                if investment_update.currency is not None:
                    inv["currency"] = investment_update.currency.upper()
                if investment_update.quantity is not None:
                    inv["quantity"] = str(investment_update.quantity)
                if investment_update.average_cost is not None:
                    inv["average_cost"] = str(investment_update.average_cost)
                if investment_update.current_price is not None:
                    inv["current_price"] = str(investment_update.current_price)
                if investment_update.last_updated is not None:
                    inv["last_updated"] = investment_update.last_updated
                if investment_update.notes is not None:
                    inv["notes"] = investment_update.notes

                inv["updated_at"] = now_iso()
                updated = True
                break

        if not updated:
            raise HTTPException(
                status_code=404, detail=f"Investment {investment_id} not found"
            )

        csv_manager.write_csv("investments.csv", investments, INVESTMENT_FIELDNAMES)

        return self.get_investment(investment_id)

    def update_price(self, investment_id: str, price_update: PriceUpdate) -> Investment:
        """
        Update investment price.

        Args:
            investment_id: Investment ID
            price_update: Price update data

        Returns:
            Updated Investment object
        """
        last_updated = price_update.last_updated or str(date_type.today())

        update_data = InvestmentUpdate(
            current_price=price_update.current_price, last_updated=last_updated
        )

        return self.update_investment(investment_id, update_data)

    def delete_investment(self, investment_id: str) -> dict:
        """
        Delete an investment and all its transactions.

        Args:
            investment_id: Investment ID

        Returns:
            Success message

        Raises:
            HTTPException: If investment not found
        """
        investments = csv_manager.read_csv("investments.csv")

        # Find and remove investment
        found = False
        filtered_investments = []
        for inv in investments:
            if inv.get("id") == investment_id:
                found = True
            else:
                filtered_investments.append(inv)

        if not found:
            raise HTTPException(
                status_code=404, detail=f"Investment {investment_id} not found"
            )

        csv_manager.write_csv(
            "investments.csv", filtered_investments, INVESTMENT_FIELDNAMES
        )

        # Delete associated transactions
        transactions = csv_manager.read_csv("investment_transactions.csv")
        filtered_transactions = [
            txn for txn in transactions if txn.get("investment_id") != investment_id
        ]
        csv_manager.write_csv(
            "investment_transactions.csv",
            filtered_transactions,
            INVESTMENT_TRANSACTION_FIELDNAMES,
        )

        return {"message": f"Investment {investment_id} deleted successfully"}

    # Investment Transaction Operations

    def list_transactions(
        self, investment_id: Optional[str] = None
    ) -> List[InvestmentTransaction]:
        """
        List investment transactions.

        Args:
            investment_id: Optional filter by investment ID

        Returns:
            List of InvestmentTransaction objects
        """
        transactions = csv_manager.read_csv("investment_transactions.csv")

        if investment_id:
            transactions = [
                txn for txn in transactions if txn.get("investment_id") == investment_id
            ]

        # Sort by date descending
        transactions.sort(key=lambda x: x.get("date", ""), reverse=True)

        return [InvestmentTransaction.from_csv(txn) for txn in transactions]

    def get_transaction(self, transaction_id: str) -> InvestmentTransaction:
        """
        Get a transaction by ID.

        Args:
            transaction_id: Transaction ID

        Returns:
            InvestmentTransaction object

        Raises:
            HTTPException: If transaction not found
        """
        transactions = csv_manager.read_csv("investment_transactions.csv")

        for txn in transactions:
            if txn.get("id") == transaction_id:
                return InvestmentTransaction.from_csv(txn)

        raise HTTPException(
            status_code=404, detail=f"Transaction {transaction_id} not found"
        )

    def create_transaction(
        self, transaction_data: InvestmentTransactionCreate
    ) -> InvestmentTransaction:
        """
        Create a new investment transaction and update investment quantity/average cost.

        Args:
            transaction_data: Transaction creation data

        Returns:
            Created InvestmentTransaction object
        """
        # Verify investment exists
        investment = self.get_investment(transaction_data.investment_id)

        # Generate ID and timestamps
        transaction_id = f"invtxn_{generate_uuid()[:8]}"
        timestamp = now_iso()

        transaction_row = {
            "id": transaction_id,
            "investment_id": transaction_data.investment_id,
            "date": str(transaction_data.date),
            "type": transaction_data.type,
            "quantity": str(transaction_data.quantity),
            "price": str(transaction_data.price),
            "fees": str(transaction_data.fees),
            "total_amount": str(transaction_data.total_amount),
            "notes": transaction_data.notes or "",
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        csv_manager.append_csv(
            "investment_transactions.csv",
            transaction_row,
            INVESTMENT_TRANSACTION_FIELDNAMES,
        )

        # Update investment quantity and average cost
        self._update_investment_from_transaction(investment, transaction_data)

        return InvestmentTransaction.from_csv(transaction_row)

    def _update_investment_from_transaction(
        self, investment: Investment, transaction: InvestmentTransactionCreate
    ):
        """
        Update investment quantity and average cost based on transaction.

        Args:
            investment: Investment object
            transaction: Transaction data
        """
        current_quantity = investment.quantity
        current_avg_cost = investment.average_cost

        if transaction.type == "buy":
            # Calculate new average cost
            total_cost = (
                current_quantity * current_avg_cost
            ) + transaction.total_amount
            new_quantity = current_quantity + transaction.quantity
            new_avg_cost = total_cost / new_quantity if new_quantity > 0 else 0

            update_data = InvestmentUpdate(
                quantity=new_quantity, average_cost=new_avg_cost
            )
        else:  # sell
            # Reduce quantity, keep average cost the same
            new_quantity = max(0, current_quantity - transaction.quantity)

            update_data = InvestmentUpdate(quantity=new_quantity)

        self.update_investment(investment.id, update_data)

    def delete_transaction(self, transaction_id: str) -> dict:
        """
        Delete an investment transaction.
        Note: This does NOT reverse the quantity/cost changes.

        Args:
            transaction_id: Transaction ID

        Returns:
            Success message

        Raises:
            HTTPException: If transaction not found
        """
        transactions = csv_manager.read_csv("investment_transactions.csv")

        # Find and remove transaction
        found = False
        filtered_transactions = []
        for txn in transactions:
            if txn.get("id") == transaction_id:
                found = True
            else:
                filtered_transactions.append(txn)

        if not found:
            raise HTTPException(
                status_code=404, detail=f"Transaction {transaction_id} not found"
            )

        csv_manager.write_csv(
            "investment_transactions.csv",
            filtered_transactions,
            INVESTMENT_TRANSACTION_FIELDNAMES,
        )

        return {"message": f"Transaction {transaction_id} deleted successfully"}

    # Performance Calculations

    def get_investment_performance(self, investment_id: str) -> InvestmentPerformance:
        """
        Calculate performance metrics for an investment.

        Args:
            investment_id: Investment ID

        Returns:
            InvestmentPerformance object
        """
        investment = self.get_investment(investment_id)

        total_cost = investment.quantity * investment.average_cost
        current_value = investment.quantity * investment.current_price
        profit_loss = current_value - total_cost
        profit_loss_percentage = (
            (profit_loss / total_cost * 100) if total_cost > 0 else 0
        )

        return InvestmentPerformance(
            investment_id=investment.id,
            symbol=investment.symbol,
            name=investment.name,
            type=investment.type,
            quantity=investment.quantity,
            average_cost=investment.average_cost,
            current_price=investment.current_price,
            total_cost=total_cost,
            current_value=current_value,
            profit_loss=profit_loss,
            profit_loss_percentage=profit_loss_percentage,
            currency=investment.currency,
        )


# Singleton instance
investment_service = InvestmentService()
