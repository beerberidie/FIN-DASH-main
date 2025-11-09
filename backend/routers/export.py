"""Export API endpoints for PDF, Excel, and CSV exports."""
import os
from datetime import datetime, date as date_type
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from fastapi.responses import FileResponse

from models.export import (
    ExportConfig, ExportResponse,
    TransactionExportRequest, BudgetReportExportRequest,
    DebtReportExportRequest, InvestmentPortfolioExportRequest,
    FinancialSummaryExportRequest
)
from services.pdf_export_service import pdf_export_service
from services.excel_export_service import excel_export_service
from services.csv_manager import csv_manager
from utils.dates import now_iso

router = APIRouter(prefix="/export", tags=["export"])


def _get_export_config() -> ExportConfig:
    """Get export configuration from settings."""
    settings = csv_manager.read_json("settings.json")
    
    return ExportConfig(
        company_name="FIN-DASH",
        base_currency=settings.get('base_currency', 'ZAR'),
        date_format="%Y-%m-%d",
        number_format=",.2f",
        page_size="A4",
        orientation="portrait"
    )


def _create_export_response(filepath: str, export_type: str, format: str) -> ExportResponse:
    """Create export response with file metadata."""
    file_size = os.path.getsize(filepath)
    filename = os.path.basename(filepath)
    
    return ExportResponse(
        filename=filename,
        file_path=filepath,
        file_size=file_size,
        export_type=export_type,
        format=format,
        created_at=now_iso()
    )


# Transaction Exports

@router.post("/transactions/pdf", response_model=ExportResponse)
def export_transactions_pdf(
    start_date: Optional[date_type] = Query(None, description="Start date for filter"),
    end_date: Optional[date_type] = Query(None, description="End date for filter"),
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    transaction_type: Optional[str] = Query(None, description="Filter by type (income/expense)")
):
    """
    Export transactions to PDF.
    
    Query Parameters:
    - **start_date**: Start date for date range filter (optional)
    - **end_date**: End date for date range filter (optional)
    - **account_id**: Filter by account ID (optional)
    - **category_id**: Filter by category ID (optional)
    - **transaction_type**: Filter by transaction type (optional)
    
    Returns:
    - Export metadata with file path for download
    """
    config = _get_export_config()
    
    filepath = pdf_export_service.export_transactions_pdf(
        start_date=start_date,
        end_date=end_date,
        account_id=account_id,
        category_id=category_id,
        transaction_type=transaction_type,
        config=config
    )
    
    return _create_export_response(filepath, "transactions", "pdf")


@router.post("/transactions/excel", response_model=ExportResponse)
def export_transactions_excel(
    start_date: Optional[date_type] = Query(None, description="Start date for filter"),
    end_date: Optional[date_type] = Query(None, description="End date for filter"),
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    transaction_type: Optional[str] = Query(None, description="Filter by type (income/expense)")
):
    """
    Export transactions to Excel.
    
    Query Parameters:
    - **start_date**: Start date for date range filter (optional)
    - **end_date**: End date for date range filter (optional)
    - **account_id**: Filter by account ID (optional)
    - **category_id**: Filter by category ID (optional)
    - **transaction_type**: Filter by transaction type (optional)
    
    Returns:
    - Export metadata with file path for download
    """
    config = _get_export_config()
    
    filepath = excel_export_service.export_transactions_excel(
        start_date=start_date,
        end_date=end_date,
        account_id=account_id,
        category_id=category_id,
        transaction_type=transaction_type,
        config=config
    )
    
    return _create_export_response(filepath, "transactions", "excel")


@router.post("/transactions/csv", response_model=ExportResponse)
def export_transactions_csv(
    start_date: Optional[date_type] = Query(None, description="Start date for filter"),
    end_date: Optional[date_type] = Query(None, description="End date for filter"),
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    transaction_type: Optional[str] = Query(None, description="Filter by type (income/expense)")
):
    """
    Export transactions to CSV.
    
    Query Parameters:
    - **start_date**: Start date for date range filter (optional)
    - **end_date**: End date for date range filter (optional)
    - **account_id**: Filter by account ID (optional)
    - **category_id**: Filter by category ID (optional)
    - **transaction_type**: Filter by transaction type (optional)
    
    Returns:
    - Export metadata with file path for download
    """
    config = _get_export_config()
    
    filepath = excel_export_service.export_transactions_csv(
        start_date=start_date,
        end_date=end_date,
        account_id=account_id,
        category_id=category_id,
        transaction_type=transaction_type,
        config=config
    )
    
    return _create_export_response(filepath, "transactions", "csv")


# Financial Summary Export

@router.post("/financial-summary/pdf", response_model=ExportResponse)
def export_financial_summary_pdf():
    """
    Export financial summary to PDF.
    
    Returns:
    - Export metadata with file path for download
    """
    config = _get_export_config()
    
    filepath = pdf_export_service.export_financial_summary_pdf(config=config)
    
    return _create_export_response(filepath, "financial_summary", "pdf")


# Investment Portfolio Exports

@router.post("/investment-portfolio/pdf", response_model=ExportResponse)
def export_investment_portfolio_pdf(
    include_transactions: bool = Query(True, description="Include transaction history"),
    investment_type: Optional[str] = Query(None, description="Filter by investment type")
):
    """
    Export investment portfolio to PDF.
    
    Query Parameters:
    - **include_transactions**: Include transaction history (default: true)
    - **investment_type**: Filter by investment type (optional)
    
    Returns:
    - Export metadata with file path for download
    """
    config = _get_export_config()
    
    filepath = pdf_export_service.export_investment_portfolio_pdf(
        include_transactions=include_transactions,
        investment_type=investment_type,
        config=config
    )
    
    return _create_export_response(filepath, "investment_portfolio", "pdf")


@router.post("/investment-portfolio/excel", response_model=ExportResponse)
def export_investment_portfolio_excel(
    include_transactions: bool = Query(True, description="Include transaction history"),
    investment_type: Optional[str] = Query(None, description="Filter by investment type")
):
    """
    Export investment portfolio to Excel.
    
    Query Parameters:
    - **include_transactions**: Include transaction history (default: true)
    - **investment_type**: Filter by investment type (optional)
    
    Returns:
    - Export metadata with file path for download
    """
    config = _get_export_config()
    
    filepath = excel_export_service.export_investment_portfolio_excel(
        include_transactions=include_transactions,
        investment_type=investment_type,
        config=config
    )
    
    return _create_export_response(filepath, "investment_portfolio", "excel")


# Debt Report Export

@router.post("/debt-report/pdf", response_model=ExportResponse)
def export_debt_report_pdf(
    include_paid_off: bool = Query(False, description="Include paid-off debts")
):
    """
    Export debt report to PDF.
    
    Query Parameters:
    - **include_paid_off**: Include paid-off debts (default: false)
    
    Returns:
    - Export metadata with file path for download
    """
    config = _get_export_config()
    
    filepath = pdf_export_service.export_debt_report_pdf(
        include_paid_off=include_paid_off,
        config=config
    )
    
    return _create_export_response(filepath, "debt_report", "pdf")


# File Download Endpoint

@router.get("/download/{filename}")
def download_export(filename: str):
    """
    Download an exported file.
    
    Path Parameters:
    - **filename**: Name of the file to download
    
    Returns:
    - File download response
    """
    filepath = os.path.join("exports", filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type based on extension
    if filename.endswith('.pdf'):
        media_type = 'application/pdf'
    elif filename.endswith('.xlsx'):
        media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif filename.endswith('.csv'):
        media_type = 'text/csv'
    else:
        media_type = 'application/octet-stream'
    
    return FileResponse(
        path=filepath,
        media_type=media_type,
        filename=filename
    )


# List Exports

@router.get("/list")
def list_exports():
    """
    List all available export files.
    
    Returns:
    - List of export files with metadata
    """
    exports_dir = "exports"
    
    if not os.path.exists(exports_dir):
        return []
    
    files = []
    for filename in os.listdir(exports_dir):
        filepath = os.path.join(exports_dir, filename)
        
        if os.path.isfile(filepath):
            file_size = os.path.getsize(filepath)
            created_at = datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
            
            # Determine export type and format from filename
            export_type = "unknown"
            format = filename.split('.')[-1]
            
            if 'transaction' in filename:
                export_type = "transactions"
            elif 'financial_summary' in filename:
                export_type = "financial_summary"
            elif 'investment' in filename:
                export_type = "investment_portfolio"
            elif 'debt' in filename:
                export_type = "debt_report"
            
            files.append({
                'filename': filename,
                'file_path': filepath,
                'file_size': file_size,
                'export_type': export_type,
                'format': format,
                'created_at': created_at
            })
    
    # Sort by creation date descending
    files.sort(key=lambda x: x['created_at'], reverse=True)
    
    return files

