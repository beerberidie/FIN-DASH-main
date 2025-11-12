"""Goals management API endpoints."""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from models.goal import Goal, GoalCreate, GoalUpdate, GOAL_FIELDNAMES
from services.csv_manager import csv_manager
from utils.ids import generate_id

router = APIRouter(prefix="/goals", tags=["goals"])


class GoalContribution(BaseModel):
    """Model for goal contribution."""

    amount: float
    note: Optional[str] = None


@router.get("", response_model=List[Goal])
def list_goals(active_only: bool = False):
    """
    List all goals.

    Args:
        active_only: If True, only return goals that haven't been completed
    """
    goals = csv_manager.read_csv("goals.csv")

    # Convert to Goal models
    goal_list = []
    for g in goals:
        try:
            goal = Goal(**g)

            # Filter by active status if requested
            if active_only and goal.current_amount >= goal.target_amount:
                continue

            goal_list.append(goal)
        except Exception as e:
            print(f"Error parsing goal {g.get('id')}: {e}")
            continue

    # Sort by target date (soonest first), then by name
    goal_list.sort(key=lambda x: (x.target_date or "9999-12-31", x.name))

    return goal_list


@router.get("/{goal_id}", response_model=Goal)
def get_goal(goal_id: str):
    """Get a specific goal by ID."""
    goals = csv_manager.read_csv("goals.csv")
    goal = next((g for g in goals if g["id"] == goal_id), None)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Goal {goal_id} not found"
        )

    return Goal(**goal)


@router.post("", response_model=Goal, status_code=status.HTTP_201_CREATED)
def create_goal(goal: GoalCreate):
    """
    Create a new savings goal.

    Validates that target_amount is positive and current_amount doesn't exceed target.
    """
    # Validate amounts
    if goal.target_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target amount must be positive",
        )

    if goal.current_amount < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current amount cannot be negative",
        )

    if goal.current_amount > goal.target_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current amount cannot exceed target amount",
        )

    # Validate target date if provided
    if goal.target_date:
        try:
            target_date = datetime.fromisoformat(goal.target_date)
            if target_date < datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Target date cannot be in the past",
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid target date format. Use YYYY-MM-DD",
            )

    # Generate ID
    goal_id = generate_id("goal", goal.name)

    # Create goal record
    now = datetime.now().isoformat()
    new_goal = {
        "id": goal_id,
        "name": goal.name,
        "target_amount": str(goal.target_amount),
        "current_amount": str(goal.current_amount),
        "target_date": goal.target_date or "",
        "linked_account_id": goal.linked_account_id or "",
        "color": goal.color or "blue",
        "icon": goal.icon or "Target",
        "created_at": now,
        "updated_at": now,
    }

    # Append to CSV
    csv_manager.append_csv("goals.csv", new_goal, GOAL_FIELDNAMES)

    return Goal(**new_goal)


@router.put("/{goal_id}", response_model=Goal)
def update_goal(goal_id: str, goal_update: GoalUpdate):
    """Update an existing goal."""
    goals = csv_manager.read_csv("goals.csv")
    goal = next((g for g in goals if g["id"] == goal_id), None)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Goal {goal_id} not found"
        )

    # Update fields
    update_data = goal_update.model_dump(exclude_unset=True)

    # Validate amounts if being updated
    current_amount = float(goal["current_amount"])
    target_amount = float(goal["target_amount"])

    if "current_amount" in update_data:
        current_amount = update_data["current_amount"]
    if "target_amount" in update_data:
        target_amount = update_data["target_amount"]

    if current_amount < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current amount cannot be negative",
        )

    if target_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target amount must be positive",
        )

    # Apply updates
    for key, value in update_data.items():
        if value is not None:
            goal[key] = str(value) if not isinstance(value, str) else value

    goal["updated_at"] = datetime.now().isoformat()

    # Write back to CSV
    csv_manager.update_csv_row("goals.csv", goal_id, goal, GOAL_FIELDNAMES)

    return Goal(**goal)


@router.post("/{goal_id}/contribute", response_model=Goal)
def contribute_to_goal(goal_id: str, contribution: GoalContribution):
    """
    Add a contribution to a goal.

    This increases the current_amount by the contribution amount.
    """
    goals = csv_manager.read_csv("goals.csv")
    goal = next((g for g in goals if g["id"] == goal_id), None)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Goal {goal_id} not found"
        )

    # Validate contribution amount
    if contribution.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contribution amount must be positive",
        )

    # Update current amount
    current_amount = float(goal["current_amount"])
    target_amount = float(goal["target_amount"])
    new_amount = current_amount + contribution.amount

    # Cap at target amount
    if new_amount > target_amount:
        new_amount = target_amount

    goal["current_amount"] = str(new_amount)
    goal["updated_at"] = datetime.now().isoformat()

    # Write back to CSV
    csv_manager.update_csv_row("goals.csv", goal_id, goal, GOAL_FIELDNAMES)

    return Goal(**goal)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: str):
    """Delete a goal."""
    goals = csv_manager.read_csv("goals.csv")
    goal = next((g for g in goals if g["id"] == goal_id), None)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Goal {goal_id} not found"
        )

    # Delete from CSV
    csv_manager.delete_csv_row("goals.csv", goal_id, GOAL_FIELDNAMES)

    return None
