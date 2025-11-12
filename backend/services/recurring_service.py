"""Recurring transaction service for FIN-DASH."""

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from typing import List, Optional, Dict, Any
import uuid

from services.csv_manager import csv_manager
from models.recurring_transaction import (
    RecurringTransaction,
    RecurringTransactionCreate,
    RecurringTransactionUpdate,
)
from models.transaction import TransactionCreate


class RecurringTransactionService:
    """Service for managing recurring transactions."""

    def __init__(self):
        self.filename = "recurring_transactions.csv"

    def _clean_row(self, row: dict) -> dict:
        """Clean CSV row data for Pydantic validation."""
        cleaned = row.copy()

        # Convert empty strings to None for optional fields
        for field in [
            "end_date",
            "day_of_month",
            "day_of_week",
            "last_generated",
            "next_due",
        ]:
            if field in cleaned and cleaned[field] == "":
                cleaned[field] = None

        # Convert string numbers to actual numbers
        if "amount" in cleaned and isinstance(cleaned["amount"], str):
            cleaned["amount"] = float(cleaned["amount"])

        if (
            "day_of_month" in cleaned
            and cleaned["day_of_month"] is not None
            and isinstance(cleaned["day_of_month"], str)
        ):
            cleaned["day_of_month"] = int(cleaned["day_of_month"])

        if (
            "day_of_week" in cleaned
            and cleaned["day_of_week"] is not None
            and isinstance(cleaned["day_of_week"], str)
        ):
            cleaned["day_of_week"] = int(cleaned["day_of_week"])

        # Convert string booleans to actual booleans
        if "is_active" in cleaned and isinstance(cleaned["is_active"], str):
            cleaned["is_active"] = cleaned["is_active"].lower() in ("true", "1", "yes")

        return cleaned

    def get_all(self) -> List[RecurringTransaction]:
        """Get all recurring transactions."""
        rows = csv_manager.read_csv(self.filename)
        return [RecurringTransaction(**self._clean_row(row)) for row in rows]

    def get_by_id(self, recurring_id: str) -> Optional[RecurringTransaction]:
        """Get a recurring transaction by ID."""
        row = csv_manager.read_by_id(self.filename, recurring_id)
        if row:
            return RecurringTransaction(**self._clean_row(row))
        return None

    def get_active(self) -> List[RecurringTransaction]:
        """Get all active recurring transactions."""
        all_recurring = self.get_all()
        return [r for r in all_recurring if r.is_active]

    def create(
        self, recurring_data: RecurringTransactionCreate
    ) -> RecurringTransaction:
        """Create a new recurring transaction."""
        now = datetime.utcnow().isoformat() + "Z"
        recurring_id = f"rec_{recurring_data.name.lower().replace(' ', '-')}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # Calculate next due date
        next_due = self._calculate_next_due(
            recurring_data.start_date,
            recurring_data.frequency,
            recurring_data.day_of_month,
            recurring_data.day_of_week,
        )

        recurring = RecurringTransaction(
            id=recurring_id,
            name=recurring_data.name,
            amount=recurring_data.amount,
            category_id=recurring_data.category_id,
            account_id=recurring_data.account_id,
            type=recurring_data.type,
            frequency=recurring_data.frequency,
            start_date=recurring_data.start_date,
            end_date=recurring_data.end_date,
            day_of_month=recurring_data.day_of_month,
            day_of_week=recurring_data.day_of_week,
            is_active=recurring_data.is_active,
            last_generated=None,
            next_due=next_due,
            tags=recurring_data.tags or "",
            notes=recurring_data.notes or "",
            created_at=now,
            updated_at=now,
        )

        csv_manager.append(self.filename, recurring.model_dump())
        return recurring

    def update(
        self, recurring_id: str, update_data: RecurringTransactionUpdate
    ) -> Optional[RecurringTransaction]:
        """Update a recurring transaction."""
        existing = self.get_by_id(recurring_id)
        if not existing:
            return None

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        updated_data = existing.model_dump()
        updated_data.update(update_dict)
        updated_data["updated_at"] = datetime.utcnow().isoformat() + "Z"

        # Recalculate next_due if frequency or dates changed
        if any(
            k in update_dict
            for k in ["frequency", "start_date", "day_of_month", "day_of_week"]
        ):
            updated_data["next_due"] = self._calculate_next_due(
                updated_data["start_date"],
                updated_data["frequency"],
                updated_data.get("day_of_month"),
                updated_data.get("day_of_week"),
                updated_data.get("last_generated"),
            )

        csv_manager.update(self.filename, recurring_id, updated_data)
        return RecurringTransaction(**updated_data)

    def delete(self, recurring_id: str) -> bool:
        """Delete a recurring transaction."""
        return csv_manager.delete(self.filename, recurring_id)

    def toggle_active(self, recurring_id: str) -> Optional[RecurringTransaction]:
        """Toggle the active status of a recurring transaction."""
        existing = self.get_by_id(recurring_id)
        if not existing:
            return None

        update_data = RecurringTransactionUpdate(is_active=not existing.is_active)
        return self.update(recurring_id, update_data)

    def _calculate_next_due(
        self,
        start_date: str,
        frequency: str,
        day_of_month: Optional[int] = None,
        day_of_week: Optional[int] = None,
        last_generated: Optional[str] = None,
    ) -> str:
        """Calculate the next due date for a recurring transaction."""
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        today = date.today()

        # If we have a last_generated date, start from there
        if last_generated:
            reference_date = datetime.strptime(last_generated, "%Y-%m-%d").date()
        else:
            reference_date = start if start > today else today

        # Calculate next occurrence based on frequency
        if frequency == "daily":
            next_date = reference_date + timedelta(days=1)

        elif frequency == "weekly":
            # Find next occurrence of the specified day of week
            if day_of_week is not None:
                days_ahead = day_of_week - reference_date.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                next_date = reference_date + timedelta(days=days_ahead)
            else:
                next_date = reference_date + timedelta(weeks=1)

        elif frequency == "biweekly":
            if day_of_week is not None:
                days_ahead = day_of_week - reference_date.weekday()
                if days_ahead <= 0:
                    days_ahead += 14
                next_date = reference_date + timedelta(days=days_ahead)
            else:
                next_date = reference_date + timedelta(weeks=2)

        elif frequency == "monthly":
            # Add one month
            next_date = reference_date + relativedelta(months=1)
            # Adjust to specific day of month if specified
            if day_of_month:
                try:
                    next_date = next_date.replace(day=day_of_month)
                except ValueError:
                    # Handle invalid day (e.g., Feb 30) - use last day of month
                    next_date = next_date + relativedelta(day=31)

        elif frequency == "quarterly":
            next_date = reference_date + relativedelta(months=3)
            if day_of_month:
                try:
                    next_date = next_date.replace(day=day_of_month)
                except ValueError:
                    next_date = next_date + relativedelta(day=31)

        elif frequency == "yearly":
            next_date = reference_date + relativedelta(years=1)
            if day_of_month:
                try:
                    next_date = next_date.replace(day=day_of_month)
                except ValueError:
                    next_date = next_date + relativedelta(day=31)

        else:
            next_date = reference_date + timedelta(days=1)

        return next_date.strftime("%Y-%m-%d")

    def get_due_transactions(
        self, check_date: Optional[date] = None
    ) -> List[RecurringTransaction]:
        """Get all recurring transactions that are due for generation."""
        if check_date is None:
            check_date = date.today()

        active_recurring = self.get_active()
        due_transactions = []

        for recurring in active_recurring:
            # Skip if no next_due date
            if not recurring.next_due:
                continue

            # Parse next_due date
            next_due = datetime.strptime(recurring.next_due, "%Y-%m-%d").date()

            # Check if due
            if next_due <= check_date:
                # Check if end_date has passed
                if recurring.end_date:
                    end_date = datetime.strptime(recurring.end_date, "%Y-%m-%d").date()
                    if check_date > end_date:
                        continue

                due_transactions.append(recurring)

        return due_transactions

    def generate_transaction(self, recurring: RecurringTransaction) -> Dict[str, Any]:
        """Generate a transaction from a recurring transaction rule."""
        now = datetime.utcnow().isoformat() + "Z"
        transaction_date = recurring.next_due or date.today().strftime("%Y-%m-%d")

        transaction = {
            "id": f"tx_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
            "date": transaction_date,
            "description": recurring.name,
            "amount": recurring.amount,
            "category_id": recurring.category_id,
            "account_id": recurring.account_id,
            "type": recurring.type,
            "source": "recurring",
            "external_id": recurring.id,  # Link back to recurring transaction
            "tags": recurring.tags or "",
            "created_at": now,
            "updated_at": now,
        }

        # Update recurring transaction's last_generated and next_due
        update_data = RecurringTransactionUpdate(
            last_generated=transaction_date,
        )
        self.update(recurring.id, update_data)

        return transaction

    def process_due_transactions(self) -> List[Dict[str, Any]]:
        """Process all due recurring transactions and generate actual transactions."""
        due_transactions = self.get_due_transactions()
        generated = []

        for recurring in due_transactions:
            transaction = self.generate_transaction(recurring)

            # Save transaction to transactions.csv
            csv_manager.append("transactions.csv", transaction)
            generated.append(transaction)

        return generated


# Singleton instance
recurring_service = RecurringTransactionService()
