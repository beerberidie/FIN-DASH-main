"""Budget management API endpoints."""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from datetime import datetime

from models.budget import Budget, BudgetCreate, BudgetUpdate, BUDGET_FIELDNAMES
from services.csv_manager import csv_manager
from services.budget_service import budget_service
from utils.ids import generate_id

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("", response_model=List[Budget])
def list_budgets(year: Optional[int] = None, month: Optional[int] = None):
    """
    List all budgets with optional filtering by year and month.

    Args:
        year: Filter by year (optional)
        month: Filter by month 1-12 (optional)
    """
    budgets = csv_manager.read_csv("budgets.csv")

    # Convert to Budget models
    budget_list = []
    for b in budgets:
        try:
            budget_list.append(Budget(**b))
        except Exception as e:
            print(f"Error parsing budget {b.get('id')}: {e}")
            continue

    # Apply filters
    if year is not None:
        budget_list = [b for b in budget_list if b.year == year]
    if month is not None:
        budget_list = [b for b in budget_list if b.month == month]

    # Sort by year and month (most recent first)
    budget_list.sort(key=lambda x: (x.year, x.month), reverse=True)

    return budget_list


@router.get("/current")
def get_current_budget():
    """
    Get the current month's budget with actual vs planned comparison.

    Returns budget status including:
    - Planned amounts for needs/wants/savings
    - Actual spending for needs/wants/savings
    - Utilization percentages
    - Over-budget indicators
    """
    budget_status = budget_service.get_current_month_budget()

    if not budget_status:
        # Return default structure if no budget exists
        now = datetime.now()
        return {
            "year": now.year,
            "month": now.month,
            "needs_planned": 0.0,
            "needs_actual": 0.0,
            "wants_planned": 0.0,
            "wants_actual": 0.0,
            "savings_planned": 0.0,
            "savings_actual": 0.0,
            "total_planned": 0.0,
            "total_actual": 0.0,
            "needs_utilization": 0.0,
            "wants_utilization": 0.0,
            "savings_utilization": 0.0,
            "total_utilization": 0.0,
            "over_budget": {
                "needs": False,
                "wants": False,
                "savings": False,
            },
            "exists": False,
        }

    budget_status["exists"] = True
    return budget_status


@router.get("/{budget_id}")
def get_budget(budget_id: str):
    """Get a specific budget by ID with status calculation."""
    budgets = csv_manager.read_csv("budgets.csv")
    budget = next((b for b in budgets if b["id"] == budget_id), None)

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget {budget_id} not found",
        )

    # Get budget status with calculations
    budget_status = budget_service.calculate_budget_status(budget_id)

    return budget_status


@router.get("/{budget_id}/breakdown")
def get_budget_breakdown(budget_id: str):
    """
    Get detailed category breakdown for a budget.

    Returns spending by category with budget allocation.
    """
    budgets = csv_manager.read_csv("budgets.csv")
    budget = next((b for b in budgets if b["id"] == budget_id), None)

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget {budget_id} not found",
        )

    year = int(budget["year"])
    month = int(budget["month"])

    breakdown = budget_service.get_category_breakdown(year, month)

    return {
        "budget_id": budget_id,
        "year": year,
        "month": month,
        "categories": breakdown,
    }


@router.post("", response_model=Budget, status_code=status.HTTP_201_CREATED)
def create_budget(budget: BudgetCreate):
    """
    Create a new budget.

    Validates that a budget doesn't already exist for the same year/month.
    """
    budgets = csv_manager.read_csv("budgets.csv")

    # Check if budget already exists for this year/month
    existing = next(
        (
            b
            for b in budgets
            if int(b["year"]) == budget.year and int(b["month"]) == budget.month
        ),
        None,
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Budget already exists for {budget.year}-{budget.month:02d}",
        )

    # Validate month
    if budget.month < 1 or budget.month > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Month must be between 1 and 12",
        )

    # Generate ID
    budget_id = generate_id("bud", f"{budget.year}-{budget.month:02d}")

    # Create budget record
    now = datetime.now().isoformat()
    new_budget = {
        "id": budget_id,
        "year": str(budget.year),
        "month": str(budget.month),
        "needs_planned": str(budget.needs_planned),
        "wants_planned": str(budget.wants_planned),
        "savings_planned": str(budget.savings_planned),
        "notes": budget.notes or "",
        "created_at": now,
        "updated_at": now,
    }

    # Append to CSV
    csv_manager.append_csv("budgets.csv", new_budget, BUDGET_FIELDNAMES)

    return Budget(**new_budget)


@router.put("/{budget_id}", response_model=Budget)
def update_budget(budget_id: str, budget_update: BudgetUpdate):
    """Update an existing budget."""
    budgets = csv_manager.read_csv("budgets.csv")
    budget = next((b for b in budgets if b["id"] == budget_id), None)

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget {budget_id} not found",
        )

    # Update fields
    update_data = budget_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            budget[key] = str(value)

    budget["updated_at"] = datetime.now().isoformat()

    # Write back to CSV
    csv_manager.update_csv_row("budgets.csv", budget_id, budget, BUDGET_FIELDNAMES)

    return Budget(**budget)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(budget_id: str):
    """Delete a budget."""
    budgets = csv_manager.read_csv("budgets.csv")
    budget = next((b for b in budgets if b["id"] == budget_id), None)

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget {budget_id} not found",
        )

    # Delete from CSV
    csv_manager.delete_csv_row("budgets.csv", budget_id, BUDGET_FIELDNAMES)

    return None
