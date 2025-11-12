"""Import router for bank statement file uploads (CSV, Excel, PDF, OFX, QFX)."""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import Optional, List, Dict, Any
from pathlib import Path
import tempfile
import os
from pydantic import BaseModel
from services.import_service import import_service
from services.categorizer import categorizer


router = APIRouter(tags=["import"])


class ImportSummary(BaseModel):
    """Import summary response."""

    success: bool
    imported: int
    skipped: int
    total: int
    errors: list[str]
    error: Optional[str] = None


class CategorizationPreview(BaseModel):
    """Preview of auto-categorization."""

    description: str
    amount: float
    suggested_category: str
    confidence: float
    confidence_label: str


@router.post("/import/csv", response_model=ImportSummary)
async def import_csv(
    file: UploadFile = File(...),
    account_id: str = Form(...),
    bank_format: Optional[str] = Form(None),
    auto_categorize: bool = Form(True),
):
    """
    Import transactions from CSV file.

    Args:
        file: CSV file upload
        account_id: Account ID to associate transactions with
        bank_format: Bank format (fnb, standard_bank, capitec, nedbank, absa)
        auto_categorize: Whether to auto-categorize transactions

    Returns:
        Import summary with counts and errors
    """
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    # Read file content
    try:
        content = await file.read()
        file_content = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    # Import transactions
    try:
        result = import_service.import_transactions(
            file_content=file_content,
            account_id=account_id,
            bank_format=bank_format,
            auto_categorize=auto_categorize,
        )

        return ImportSummary(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/import/preview", response_model=list[CategorizationPreview])
async def preview_categorization(
    file: UploadFile = File(...), bank_format: Optional[str] = Form(None)
):
    """
    Preview auto-categorization for CSV file without importing.

    Args:
        file: CSV file upload
        bank_format: Bank format (fnb, standard_bank, capitec, nedbank, absa)

    Returns:
        List of categorization previews
    """
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    # Read file content
    try:
        content = await file.read()
        file_content = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    # Parse CSV
    try:
        rows, headers = import_service.parse_csv(file_content, bank_format=bank_format)

        # Auto-detect format if not provided
        if not bank_format:
            detected_format = import_service.detect_bank_format(headers)
            if detected_format:
                bank_format = detected_format
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Could not detect bank format. Please specify bank_format.",
                )

        # Get column mapping
        column_mapping = import_service.BANK_FORMATS.get(bank_format, {})
        if not column_mapping:
            raise HTTPException(
                status_code=400, detail=f"Unknown bank format: {bank_format}"
            )

        # Preview categorization for first 10 rows
        previews = []
        for row in rows[:10]:
            try:
                # Validate row
                is_valid, error = import_service.validate_transaction(
                    row, column_mapping
                )
                if not is_valid:
                    continue

                # Extract data
                desc_col = column_mapping["description_column"]
                amount_col = column_mapping["amount_column"]

                description = row[desc_col].strip()
                amount_str = row[amount_col].replace(",", "").replace(" ", "")
                amount = float(amount_str)

                # Get categorization
                category_id, confidence = categorizer.categorize(description, amount)
                confidence_label = categorizer.get_confidence_label(confidence)

                previews.append(
                    CategorizationPreview(
                        description=description,
                        amount=amount,
                        suggested_category=category_id,
                        confidence=confidence,
                        confidence_label=confidence_label,
                    )
                )

            except Exception:
                continue

        return previews

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")


@router.get("/import/formats")
async def get_supported_formats():
    """
    Get list of supported bank formats and file types.

    Returns:
        Dict of supported bank formats and file types
    """
    return {
        "formats": list(import_service.BANK_FORMATS.keys()),
        "file_types": ["csv", "xls", "xlsx", "pdf", "ofx", "qfx"],
        "details": {
            "fnb": "FNB Bank Statement",
            "standard_bank": "Standard Bank Statement",
            "capitec": "Capitec Bank Statement",
            "nedbank": "Nedbank Statement",
            "absa": "ABSA Bank Statement",
        },
    }


# New multi-format import endpoints


class ImportPreviewResponse(BaseModel):
    """Import preview response."""

    import_id: str
    file_name: str
    file_type: str
    account_id: str
    total_transactions: int
    new_transactions: int
    duplicate_transactions: int
    transactions: List[Dict[str, Any]]
    created_at: str
    status: str


class ImportConfirmRequest(BaseModel):
    """Import confirmation request."""

    skip_duplicates: bool = True
    selected_transaction_indices: Optional[List[int]] = None


class ImportConfirmResponse(BaseModel):
    """Import confirmation response."""

    import_id: str
    imported_count: int
    skipped_count: int
    errors: List[Dict[str, Any]]


@router.post("/import/upload", response_model=ImportPreviewResponse)
async def upload_statement(
    file: UploadFile = File(...),
    account_id: str = Form(...),
    auto_categorize: bool = Form(True),
):
    """
    Upload and parse bank statement file (CSV, Excel, PDF, OFX, QFX).
    Returns preview of transactions to be imported.

    Args:
        file: Bank statement file
        account_id: Account ID to associate transactions with
        auto_categorize: Whether to auto-categorize transactions

    Returns:
        Import preview with parsed transactions
    """
    # Validate file type
    allowed_extensions = [".csv", ".xls", ".xlsx", ".pdf", ".ofx", ".qfx"]
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}",
        )

    # Save uploaded file temporarily
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        # Parse the file
        import_record = import_service.upload_and_parse_file(
            file_path=Path(tmp_file_path),
            account_id=account_id,
            auto_categorize=auto_categorize,
        )

        # Clean up temp file
        os.unlink(tmp_file_path)

        return ImportPreviewResponse(**import_record)

    except ValueError as e:
        if "tmp_file_path" in locals():
            os.unlink(tmp_file_path)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if "tmp_file_path" in locals():
            os.unlink(tmp_file_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/import/preview/{import_id}", response_model=ImportPreviewResponse)
async def get_import_preview(import_id: str):
    """
    Get import preview by ID.

    Args:
        import_id: Import ID

    Returns:
        Import preview
    """
    import_record = import_service.get_import_preview(import_id)

    if not import_record:
        raise HTTPException(status_code=404, detail="Import not found")

    return ImportPreviewResponse(**import_record)


@router.post("/import/confirm/{import_id}", response_model=ImportConfirmResponse)
async def confirm_import(import_id: str, request: ImportConfirmRequest):
    """
    Confirm and execute the import.

    Args:
        import_id: Import ID
        request: Import confirmation request

    Returns:
        Import summary
    """
    try:
        result = import_service.confirm_import(
            import_id=import_id,
            skip_duplicates=request.skip_duplicates,
            selected_transaction_indices=request.selected_transaction_indices,
        )

        return ImportConfirmResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.get("/import/history")
async def get_import_history(limit: int = 50):
    """
    Get import history.

    Args:
        limit: Maximum number of records to return

    Returns:
        List of import history records
    """
    try:
        history = import_service.get_import_history(limit=limit)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")
