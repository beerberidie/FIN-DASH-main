"""Transaction API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import date

from models.transaction import (
    Transaction,
    TransactionCreate,
    TransactionUpdate,
    TRANSACTION_FIELDNAMES,
)
from services.csv_manager import csv_manager
from utils.ids import generate_transaction_id
from utils.dates import now_iso

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=List[Transaction])
def list_transactions(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    category_id: Optional[str] = None,
    account_id: Optional[str] = None,
):
    """List transactions with optional filters."""
    transactions = csv_manager.read_csv("transactions.csv")

    # Apply filters
    filtered = []
    for tx_data in transactions:
        # Date filter
        if from_date and tx_data.get("date", "") < str(from_date):
            continue
        if to_date and tx_data.get("date", "") > str(to_date):
            continue

        # Category filter
        if category_id and tx_data.get("category_id") != category_id:
            continue

        # Account filter
        if account_id and tx_data.get("account_id") != account_id:
            continue

        filtered.append(Transaction.from_csv(tx_data))

    # Sort by date descending
    filtered.sort(key=lambda x: x.date, reverse=True)

    return filtered


@router.get("/{transaction_id}", response_model=Transaction)
def get_transaction(transaction_id: str):
    """Get a single transaction by ID."""
    transactions = csv_manager.read_csv("transactions.csv")

    for tx_data in transactions:
        if tx_data.get("id") == transaction_id:
            return Transaction.from_csv(tx_data)

    raise HTTPException(status_code=404, detail="Transaction not found")


@router.post("", response_model=Transaction, status_code=201)
def create_transaction(transaction: TransactionCreate):
    """Create a new transaction."""
    # Generate ID and timestamps
    tx_id = generate_transaction_id()
    timestamp = now_iso()

    # Create transaction object
    tx_data = transaction.model_dump()
    tx_data["id"] = tx_id
    tx_data["created_at"] = timestamp
    tx_data["updated_at"] = timestamp

    # Convert date to string
    tx_data["date"] = str(tx_data["date"])

    # Append to CSV
    csv_manager.append_csv("transactions.csv", tx_data, TRANSACTION_FIELDNAMES)

    return Transaction(**tx_data)


@router.put("/{transaction_id}", response_model=Transaction)
def update_transaction(transaction_id: str, transaction: TransactionUpdate):
    """Update an existing transaction."""
    transactions = csv_manager.read_csv("transactions.csv")

    # Find transaction
    found = False
    for i, tx_data in enumerate(transactions):
        if tx_data.get("id") == transaction_id:
            # Update fields
            update_data = transaction.model_dump(exclude_unset=True)

            # Convert date to string if present
            if "date" in update_data:
                update_data["date"] = str(update_data["date"])

            tx_data.update(update_data)
            tx_data["updated_at"] = now_iso()

            transactions[i] = tx_data
            found = True
            break

    if not found:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Write back to CSV
    csv_manager.write_csv("transactions.csv", transactions, TRANSACTION_FIELDNAMES)

    return Transaction.from_csv(transactions[i])


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: str):
    """Delete a transaction."""
    success = csv_manager.delete_csv_row(
        "transactions.csv", transaction_id, TRANSACTION_FIELDNAMES
    )

    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return None
