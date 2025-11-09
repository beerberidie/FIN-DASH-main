"""Debt management router."""
from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from models.debt import Debt, DebtCreate, DebtUpdate, DEBT_FIELDNAMES
from services.csv_manager import csv_manager
from services.debt_service import debt_service
from utils.ids import generate_id


router = APIRouter(tags=["debts"])


class DebtPayment(BaseModel):
    """Model for recording a debt payment."""
    amount: float = Field(..., gt=0)
    payment_date: Optional[str] = None
    notes: Optional[str] = None


class PayoffPlanRequest(BaseModel):
    """Model for payoff plan request."""
    extra_payment: float = Field(default=0, ge=0)
    strategy: Optional[str] = Field(default="both", pattern="^(avalanche|snowball|both)$")


@router.get("/debts", response_model=list[Debt])
async def get_debts():
    """
    Get all debts.

    Returns:
        List of all debts
    """
    try:
        rows = csv_manager.read_csv('debts.csv')
        return [Debt.from_csv(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch debts: {str(e)}")


@router.get("/debts/{debt_id}", response_model=Debt)
async def get_debt(debt_id: str):
    """
    Get specific debt by ID.
    
    Args:
        debt_id: Debt ID
        
    Returns:
        Debt details
    """
    try:
        row = csv_manager.read_by_id('debts.csv', debt_id)
        if not row:
            raise HTTPException(status_code=404, detail="Debt not found")
        return Debt.from_csv(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch debt: {str(e)}")


@router.post("/debts", response_model=Debt, status_code=201)
async def create_debt(debt: DebtCreate):
    """
    Create a new debt.
    
    Args:
        debt: Debt creation data
        
    Returns:
        Created debt
    """
    try:
        # Generate ID
        debt_id = generate_id('debt', debt.name)
        
        # Create debt record
        now = datetime.now().isoformat()
        debt_data = {
            'id': debt_id,
            **debt.model_dump(),
            'created_at': now,
            'updated_at': now,
        }
        
        # Convert None to empty string for CSV
        if debt_data.get('linked_account_id') is None:
            debt_data['linked_account_id'] = ''
        if debt_data.get('notes') is None:
            debt_data['notes'] = ''
        
        # Save to CSV
        csv_manager.append('debts.csv', debt_data)
        
        return Debt.from_csv(debt_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create debt: {str(e)}")


@router.put("/debts/{debt_id}", response_model=Debt)
async def update_debt(debt_id: str, debt: DebtUpdate):
    """
    Update an existing debt.
    
    Args:
        debt_id: Debt ID
        debt: Debt update data
        
    Returns:
        Updated debt
    """
    try:
        # Get existing debt
        existing = csv_manager.read_by_id('debts.csv', debt_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Debt not found")
        
        # Update fields
        update_data = debt.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                existing[key] = value
        
        existing['updated_at'] = datetime.now().isoformat()
        
        # Convert None to empty string for CSV
        if existing.get('linked_account_id') is None:
            existing['linked_account_id'] = ''
        if existing.get('notes') is None:
            existing['notes'] = ''
        
        # Save to CSV
        csv_manager.update('debts.csv', debt_id, existing)
        
        return Debt.from_csv(existing)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update debt: {str(e)}")


@router.delete("/debts/{debt_id}")
async def delete_debt(debt_id: str):
    """
    Delete a debt.
    
    Args:
        debt_id: Debt ID
        
    Returns:
        Success message
    """
    try:
        # Check if debt exists
        existing = csv_manager.read_by_id('debts.csv', debt_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Debt not found")
        
        # Delete from CSV
        csv_manager.delete('debts.csv', debt_id)
        
        return {"message": "Debt deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete debt: {str(e)}")


@router.post("/debts/{debt_id}/payment", response_model=Debt)
async def record_payment(debt_id: str, payment: DebtPayment):
    """
    Record a payment towards a debt.
    
    Args:
        debt_id: Debt ID
        payment: Payment details
        
    Returns:
        Updated debt
    """
    try:
        # Get existing debt
        existing = csv_manager.read_by_id('debts.csv', debt_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Debt not found")
        
        # Update balance
        current_balance = float(existing['current_balance'])
        new_balance = max(0, current_balance - payment.amount)
        
        existing['current_balance'] = str(new_balance)
        existing['updated_at'] = datetime.now().isoformat()
        
        # Save to CSV
        csv_manager.update('debts.csv', debt_id, existing)
        
        # TODO: Record payment in payment history (future enhancement)
        
        return Debt.from_csv(existing)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record payment: {str(e)}")


@router.post("/debts/payoff-plan")
async def get_payoff_plan(request: PayoffPlanRequest):
    """
    Calculate debt payoff plan.
    
    Args:
        request: Payoff plan request with extra payment and strategy
        
    Returns:
        Payoff plan(s) based on selected strategy
    """
    try:
        if request.strategy == "avalanche":
            return debt_service.calculate_avalanche_plan(request.extra_payment)
        elif request.strategy == "snowball":
            return debt_service.calculate_snowball_plan(request.extra_payment)
        else:  # both
            return debt_service.compare_strategies(request.extra_payment)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate payoff plan: {str(e)}")


@router.get("/debts/summary/total")
async def get_debt_summary():
    """
    Get debt summary statistics.

    Returns:
        Total debt, minimum payment, and debt count
    """
    try:
        total_debt = debt_service.get_total_debt()
        minimum_payment = debt_service.get_minimum_payment()

        debts = csv_manager.read_csv('debts.csv')
        active_debts = [d for d in debts if float(d.get('current_balance', 0)) > 0]

        return {
            'total_debt': round(total_debt, 2),
            'minimum_payment': round(minimum_payment, 2),
            'debt_count': len(debts),
            'active_debt_count': len(active_debts)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get debt summary: {str(e)}")

