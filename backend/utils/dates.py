"""Date utilities."""

from datetime import datetime, date
from typing import Optional


def now_iso() -> str:
    """Get current timestamp in ISO 8601 format."""
    return datetime.now().isoformat() + "Z"


def parse_date(date_str: str) -> date:
    """Parse date string in YYYY-MM-DD format."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def format_date(d: date) -> str:
    """Format date as YYYY-MM-DD."""
    return d.strftime("%Y-%m-%d")


def get_current_month() -> str:
    """Get current month in YYYY-MM format."""
    return datetime.now().strftime("%Y-%m")


def parse_month(month_str: str) -> tuple[int, int]:
    """Parse month string (YYYY-MM) to year and month integers."""
    year, month = month_str.split("-")
    return int(year), int(month)
