"""Data validation utilities."""
from typing import Any, Dict, List


def validate_foreign_key(value: str, valid_ids: List[str], field_name: str) -> None:
    """Validate that a foreign key exists in the referenced data."""
    if value and value not in valid_ids:
        raise ValueError(f"Invalid {field_name}: {value} does not exist")


def validate_group(group: str) -> None:
    """Validate that a category group is valid."""
    valid_groups = ["needs", "wants", "savings", "debt", "income"]
    if group not in valid_groups:
        raise ValueError(f"Invalid group: {group}. Must be one of {valid_groups}")


def validate_transaction_type(transaction_type: str) -> None:
    """Validate that a transaction type is valid."""
    valid_types = ["income", "expense"]
    if transaction_type not in valid_types:
        raise ValueError(f"Invalid type: {transaction_type}. Must be one of {valid_types}")


def validate_account_type(account_type: str) -> None:
    """Validate that an account type is valid."""
    valid_types = ["bank", "cash", "investment", "virtual"]
    if account_type not in valid_types:
        raise ValueError(f"Invalid account type: {account_type}. Must be one of {valid_types}")

