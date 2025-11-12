"""Demo mode router for FIN-DASH.

Provides endpoints for demo mode functionality:
- Get demo data
- Reset demo data
- Check demo status
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import json
from pathlib import Path

from services.demo_data_generator import demo_generator
from config import config

router = APIRouter(tags=["demo"])

# Cache for demo data (generated once per session)
_demo_data_cache: Dict[str, Any] = None


def get_demo_data() -> Dict[str, Any]:
    """Get or generate demo data."""
    global _demo_data_cache

    if _demo_data_cache is None:
        _demo_data_cache = demo_generator.generate_complete_dataset()

    return _demo_data_cache


@router.get("/demo/data")
async def get_complete_demo_data():
    """
    Get complete demo dataset.

    Returns all demo data including:
    - Categories
    - Accounts
    - Transactions (6 months)
    - Budgets
    - Investments
    - Recurring transactions
    """
    try:
        data = get_demo_data()

        return {
            "status": "success",
            "data": data,
            "summary": {
                "categories": len(data["categories"]),
                "accounts": len(data["accounts"]),
                "transactions": len(data["transactions"]),
                "budgets": len(data["budgets"]),
                "investments": len(data["investments"]),
                "recurring_transactions": len(data["recurring_transactions"]),
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate demo data: {str(e)}"
        )


@router.post("/demo/reset")
async def reset_demo_data():
    """
    Reset demo data to initial state.

    Clears the cache and regenerates fresh demo data.
    """
    global _demo_data_cache

    try:
        # Clear cache
        _demo_data_cache = None

        # Regenerate
        data = get_demo_data()

        return {
            "status": "success",
            "message": "Demo data has been reset",
            "summary": {
                "categories": len(data["categories"]),
                "accounts": len(data["accounts"]),
                "transactions": len(data["transactions"]),
                "budgets": len(data["budgets"]),
                "investments": len(data["investments"]),
                "recurring_transactions": len(data["recurring_transactions"]),
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to reset demo data: {str(e)}"
        )


@router.get("/demo/status")
async def get_demo_status():
    """
    Get demo mode status.

    Returns information about whether demo data is loaded.
    """
    global _demo_data_cache

    return {
        "demo_mode_available": True,
        "demo_data_loaded": _demo_data_cache is not None,
        "description": "Demo mode provides 6 months of realistic South African financial data",
    }


@router.get("/demo/categories")
async def get_demo_categories():
    """Get demo categories."""
    data = get_demo_data()
    return data["categories"]


@router.get("/demo/accounts")
async def get_demo_accounts():
    """Get demo accounts."""
    data = get_demo_data()
    return data["accounts"]


@router.get("/demo/transactions")
async def get_demo_transactions():
    """Get demo transactions."""
    data = get_demo_data()
    return data["transactions"]


@router.get("/demo/budgets")
async def get_demo_budgets():
    """Get demo budgets."""
    data = get_demo_data()
    return data["budgets"]


@router.get("/demo/investments")
async def get_demo_investments():
    """Get demo investments."""
    data = get_demo_data()
    return data["investments"]


@router.get("/demo/recurring")
async def get_demo_recurring():
    """Get demo recurring transactions."""
    data = get_demo_data()
    return data["recurring_transactions"]
