"""ID generation utilities."""

import uuid
from datetime import datetime
import hashlib


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


def generate_id(prefix: str, identifier: str) -> str:
    """
    Generate a unique ID with a prefix and identifier.

    Args:
        prefix: Prefix for the ID (e.g., 'bud', 'goal')
        identifier: Unique identifier (e.g., name, date)

    Returns:
        Generated ID string
    """
    slug = identifier.lower().replace(" ", "-").replace("/", "-")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}_{slug}_{timestamp}"


def generate_transaction_id() -> str:
    """Generate a transaction ID with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = str(uuid.uuid4())[:8]
    return f"tx_{timestamp}_{random_suffix}"


def generate_category_id(group: str, name: str) -> str:
    """Generate a category ID from group and name."""
    slug = name.lower().replace(" ", "_").replace("/", "_")
    return f"cat_{group}_{slug}"


def generate_account_id(name: str) -> str:
    """Generate an account ID from name."""
    slug = name.lower().replace(" ", "_")
    return f"acc_{slug}"


def generate_budget_id(month: str, category_id: str) -> str:
    """Generate a budget ID from month and category."""
    month_str = month.replace("-", "")
    return f"bud_{month_str}_{category_id}"


def generate_goal_id(name: str) -> str:
    """Generate a goal ID from name."""
    slug = name.lower().replace(" ", "_")
    return f"goal_{slug}"


def generate_debt_id(name: str) -> str:
    """Generate a debt ID from name."""
    slug = name.lower().replace(" ", "_")
    return f"debt_{slug}"


def generate_hash(*args) -> str:
    """Generate a hash from multiple arguments for deduplication."""
    combined = "|".join(str(arg) for arg in args)
    return hashlib.md5(combined.encode()).hexdigest()
