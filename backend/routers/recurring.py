"""Recurring transactions API router."""
from fastapi import APIRouter, HTTPException, status
from typing import List

from models.recurring_transaction import (
    RecurringTransaction, 
    RecurringTransactionCreate, 
    RecurringTransactionUpdate
)
from services.recurring_service import recurring_service

router = APIRouter(tags=["recurring"])


@router.get("/recurring", response_model=List[RecurringTransaction])
def get_recurring_transactions(active_only: bool = False):
    """
    Get all recurring transactions.
    
    - **active_only**: If True, only return active recurring transactions
    """
    if active_only:
        return recurring_service.get_active()
    return recurring_service.get_all()


@router.get("/recurring/{recurring_id}", response_model=RecurringTransaction)
def get_recurring_transaction(recurring_id: str):
    """Get a specific recurring transaction by ID."""
    recurring = recurring_service.get_by_id(recurring_id)
    if not recurring:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recurring transaction {recurring_id} not found"
        )
    return recurring


@router.post("/recurring", response_model=RecurringTransaction, status_code=status.HTTP_201_CREATED)
def create_recurring_transaction(recurring_data: RecurringTransactionCreate):
    """
    Create a new recurring transaction.
    
    Frequency options:
    - **daily**: Every day
    - **weekly**: Every week (specify day_of_week: 0=Monday, 6=Sunday)
    - **biweekly**: Every 2 weeks (specify day_of_week)
    - **monthly**: Every month (specify day_of_month: 1-31)
    - **quarterly**: Every 3 months (specify day_of_month)
    - **yearly**: Every year (specify day_of_month)
    """
    try:
        return recurring_service.create(recurring_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/recurring/{recurring_id}", response_model=RecurringTransaction)
def update_recurring_transaction(recurring_id: str, update_data: RecurringTransactionUpdate):
    """Update a recurring transaction."""
    recurring = recurring_service.update(recurring_id, update_data)
    if not recurring:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recurring transaction {recurring_id} not found"
        )
    return recurring


@router.delete("/recurring/{recurring_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring_transaction(recurring_id: str):
    """Delete a recurring transaction."""
    success = recurring_service.delete(recurring_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recurring transaction {recurring_id} not found"
        )
    return None


@router.post("/recurring/{recurring_id}/toggle", response_model=RecurringTransaction)
def toggle_recurring_transaction(recurring_id: str):
    """Toggle the active status of a recurring transaction."""
    recurring = recurring_service.toggle_active(recurring_id)
    if not recurring:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recurring transaction {recurring_id} not found"
        )
    return recurring


@router.get("/recurring/due/check", response_model=List[RecurringTransaction])
def get_due_recurring_transactions():
    """Get all recurring transactions that are due for generation."""
    return recurring_service.get_due_transactions()


@router.post("/recurring/process/generate")
def process_recurring_transactions():
    """
    Process all due recurring transactions and generate actual transactions.
    
    This endpoint should be called periodically (e.g., daily) to generate
    transactions from recurring rules.
    
    Returns the list of generated transactions.
    """
    try:
        generated = recurring_service.process_due_transactions()
        return {
            "success": True,
            "count": len(generated),
            "transactions": generated
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing recurring transactions: {str(e)}"
        )

