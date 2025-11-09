"""Monthly reports router."""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from services.report_service import report_service


router = APIRouter(tags=["reports"])


@router.get("/reports/monthly/{year}/{month}")
async def get_monthly_report(year: int, month: int):
    """
    Generate monthly financial report.
    
    Args:
        year: Report year
        month: Report month (1-12)
        
    Returns:
        Comprehensive monthly report
    """
    # Validate month
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    # Validate year
    current_year = datetime.now().year
    if year < 2000 or year > current_year + 1:
        raise HTTPException(status_code=400, detail=f"Year must be between 2000 and {current_year + 1}")
    
    try:
        report = report_service.generate_monthly_report(year, month)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/reports/summary")
async def get_ytd_summary(year: int = None):
    """
    Get year-to-date summary.
    
    Args:
        year: Report year (defaults to current year)
        
    Returns:
        YTD summary
    """
    if year is None:
        year = datetime.now().year
    
    # Validate year
    current_year = datetime.now().year
    if year < 2000 or year > current_year + 1:
        raise HTTPException(status_code=400, detail=f"Year must be between 2000 and {current_year + 1}")
    
    try:
        summary = report_service.generate_ytd_summary(year)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")


@router.get("/reports/available-months")
async def get_available_months():
    """
    Get list of months with transaction data.

    Returns:
        List of available months
    """
    try:
        from services.csv_manager import csv_manager
        transactions = csv_manager.read_csv('transactions.csv')
        
        # Extract unique year-month combinations
        months = set()
        for tx in transactions:
            try:
                date = datetime.fromisoformat(tx['date'].replace('Z', '+00:00'))
                months.add((date.year, date.month))
            except:
                continue
        
        # Sort and format
        available = [
            {
                'year': year,
                'month': month,
                'period': f"{year}-{month:02d}",
                'label': datetime(year, month, 1).strftime('%B %Y')
            }
            for year, month in sorted(months, reverse=True)
        ]
        
        return available
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available months: {str(e)}")

