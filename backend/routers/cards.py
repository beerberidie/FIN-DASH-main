"""Card API endpoints."""

from typing import List
from fastapi import APIRouter, HTTPException, status

from models.card import Card, CardCreate, CardUpdate, CARD_FIELDNAMES
from services.csv_manager import csv_manager
from services.card_service import card_service
from utils.ids import generate_id
from utils.dates import now_iso

router = APIRouter(prefix="/cards", tags=["cards"])


@router.get("", response_model=List[Card])
def list_cards():
    """List all cards."""
    cards = csv_manager.read_csv("cards.csv")
    return [Card.from_csv(card) for card in cards]


@router.get("/{card_id}", response_model=Card)
def get_card(card_id: str):
    """Get a specific card by ID."""
    cards = csv_manager.read_csv("cards.csv")
    card = next((c for c in cards if c.get("id") == card_id), None)

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    return Card.from_csv(card)


@router.get("/{card_id}/balance")
def get_card_balance(card_id: str):
    """
    Get current balance for a card.

    Returns available balance and current balance based on transactions.
    """
    cards = csv_manager.read_csv("cards.csv")
    card = next((c for c in cards if c.get("id") == card_id), None)

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # Calculate balance
    balances = card_service.calculate_card_balance(card_id)

    return {
        "card_id": card_id,
        "card_name": card.get("name"),
        "card_type": card.get("card_type"),
        "available_balance": balances["available_balance"],
        "current_balance": balances["current_balance"],
        "credit_limit": (
            float(card.get("credit_limit", 0)) if card.get("credit_limit") else None
        ),
    }


@router.get("/{card_id}/transactions")
def get_card_transactions(card_id: str):
    """Get all transactions for a specific card."""
    cards = csv_manager.read_csv("cards.csv")
    card = next((c for c in cards if c.get("id") == card_id), None)

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # Get transactions
    transactions = csv_manager.read_csv("transactions.csv")
    card_transactions = [tx for tx in transactions if tx.get("card_id") == card_id]

    return card_transactions


@router.get("/{card_id}/analytics")
def get_card_analytics(card_id: str):
    """
    Get spending analytics for a card.

    Returns:
    - Total transactions
    - Total spent
    - Average transaction
    - Spending by category
    - Monthly spending
    - Credit utilization (for credit cards)
    """
    cards = csv_manager.read_csv("cards.csv")
    card = next((c for c in cards if c.get("id") == card_id), None)

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    analytics = card_service.get_card_analytics(card_id)
    return analytics


@router.post("", response_model=Card, status_code=status.HTTP_201_CREATED)
def create_card(card: CardCreate):
    """Create a new card."""
    # Verify account exists
    accounts = csv_manager.read_csv("accounts.csv")
    account = next((a for a in accounts if a.get("id") == card.account_id), None)

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Generate ID and timestamps
    card_id = generate_id("card", card.name)
    timestamp = now_iso()

    # Check if card already exists
    cards = csv_manager.read_csv("cards.csv")
    for c in cards:
        if c.get("id") == card_id:
            raise HTTPException(status_code=400, detail="Card already exists")

    # Create card object
    card_data = card.model_dump()
    card_data["id"] = card_id
    card_data["created_at"] = timestamp
    card_data["updated_at"] = timestamp

    # Convert to CSV format
    card_obj = Card(**card_data)

    # Append to CSV
    csv_manager.append_csv("cards.csv", card_obj.to_csv(), CARD_FIELDNAMES)

    return card_obj


@router.put("/{card_id}", response_model=Card)
def update_card(card_id: str, card: CardUpdate):
    """Update an existing card."""
    cards = csv_manager.read_csv("cards.csv")

    # Find card
    found = False
    for i, card_data in enumerate(cards):
        if card_data.get("id") == card_id:
            # Update fields
            update_data = card.model_dump(exclude_unset=True)

            # If account_id is being updated, verify it exists
            if "account_id" in update_data:
                accounts = csv_manager.read_csv("accounts.csv")
                account = next(
                    (a for a in accounts if a.get("id") == update_data["account_id"]),
                    None,
                )
                if not account:
                    raise HTTPException(status_code=404, detail="Account not found")

            # Update card data
            for key, value in update_data.items():
                if value is not None:
                    card_data[key] = value

            card_data["updated_at"] = now_iso()
            cards[i] = card_data
            found = True
            break

    if not found:
        raise HTTPException(status_code=404, detail="Card not found")

    # Write back to CSV
    csv_manager.write_csv("cards.csv", cards, CARD_FIELDNAMES)

    return Card.from_csv(cards[i])


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(card_id: str):
    """Delete a card."""
    cards = csv_manager.read_csv("cards.csv")

    # Find and remove card
    found = False
    for i, card in enumerate(cards):
        if card.get("id") == card_id:
            cards.pop(i)
            found = True
            break

    if not found:
        raise HTTPException(status_code=404, detail="Card not found")

    # Write back to CSV
    csv_manager.write_csv("cards.csv", cards, CARD_FIELDNAMES)

    return None


@router.post("/{card_id}/update-balances")
def update_card_balances(card_id: str):
    """
    Update card balances based on transactions.

    Recalculates available_balance and current_balance from all transactions.
    """
    cards = csv_manager.read_csv("cards.csv")
    card = next((c for c in cards if c.get("id") == card_id), None)

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    balances = card_service.update_card_balances(card_id)

    return {
        "card_id": card_id,
        "available_balance": balances["available_balance"],
        "current_balance": balances["current_balance"],
        "message": "Balances updated successfully",
    }
