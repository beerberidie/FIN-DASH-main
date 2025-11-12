"""Import service for bank statements (CSV, Excel, PDF, OFX, QFX)."""

import csv
import io
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from services.csv_manager import csv_manager
from services.categorizer import categorizer
from services.statement_parser import StatementParser
from utils.ids import generate_transaction_id
from utils.dates import parse_date


class ImportService:
    """Service for importing transactions from various file formats."""

    def __init__(self):
        self.parser = StatementParser()
        # Store pending imports in memory
        self.pending_imports: Dict[str, Dict[str, Any]] = {}

    # Predefined bank formats for South African banks
    BANK_FORMATS = {
        "fnb": {
            "date_column": "Date",
            "description_column": "Description",
            "amount_column": "Amount",
            "balance_column": "Balance",
            "date_format": "%Y/%m/%d",
        },
        "standard_bank": {
            "date_column": "Transaction Date",
            "description_column": "Description",
            "amount_column": "Amount",
            "balance_column": "Balance",
            "date_format": "%d/%m/%Y",
        },
        "capitec": {
            "date_column": "Date",
            "description_column": "Description",
            "amount_column": "Amount",
            "balance_column": "Balance",
            "date_format": "%d-%m-%Y",
        },
        "nedbank": {
            "date_column": "Date",
            "description_column": "Description",
            "amount_column": "Amount",
            "balance_column": "Balance",
            "date_format": "%Y-%m-%d",
        },
        "absa": {
            "date_column": "Date",
            "description_column": "Description",
            "amount_column": "Amount",
            "balance_column": "Balance",
            "date_format": "%d/%m/%Y",
        },
    }

    def __init__(self):
        """Initialize import service."""
        self.existing_transactions: List[Dict] = []
        self._load_existing_transactions()

    def _load_existing_transactions(self):
        """Load existing transactions for deduplication."""
        try:
            self.existing_transactions = csv_manager.read_all("transactions.csv")
        except Exception:
            self.existing_transactions = []

    def parse_csv(
        self,
        file_content: str,
        column_mapping: Optional[Dict[str, str]] = None,
        bank_format: Optional[str] = None,
    ) -> Tuple[List[Dict], List[str]]:
        """
        Parse CSV file content.

        Args:
            file_content: CSV file content as string
            column_mapping: Custom column mapping (overrides bank_format)
            bank_format: Predefined bank format name

        Returns:
            Tuple of (parsed_rows, headers)
        """
        # Use bank format if provided
        if bank_format and bank_format in self.BANK_FORMATS:
            column_mapping = self.BANK_FORMATS[bank_format]

        # Parse CSV
        reader = csv.DictReader(io.StringIO(file_content))
        headers = reader.fieldnames or []
        rows = list(reader)

        return rows, headers

    def detect_bank_format(self, headers: List[str]) -> Optional[str]:
        """
        Auto-detect bank format from CSV headers.

        Args:
            headers: List of column headers

        Returns:
            Bank format name or None
        """
        headers_lower = [h.lower() for h in headers]

        # Check for FNB format
        if (
            "date" in headers_lower
            and "description" in headers_lower
            and "amount" in headers_lower
        ):
            if any("balance" in h for h in headers_lower):
                # Could be FNB, Capitec, or Nedbank - check date format in first row
                return "fnb"  # Default to FNB

        # Check for Standard Bank format
        if "transaction date" in headers_lower:
            return "standard_bank"

        return None

    def validate_transaction(
        self, row: Dict, column_mapping: Dict[str, str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a transaction row.

        Args:
            row: CSV row data
            column_mapping: Column mapping configuration

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required columns
        date_col = column_mapping.get("date_column")
        desc_col = column_mapping.get("description_column")
        amount_col = column_mapping.get("amount_column")

        if not date_col or date_col not in row:
            return False, f"Missing date column: {date_col}"

        if not desc_col or desc_col not in row:
            return False, f"Missing description column: {desc_col}"

        if not amount_col or amount_col not in row:
            return False, f"Missing amount column: {amount_col}"

        # Validate date
        try:
            date_format = column_mapping.get("date_format", "%Y-%m-%d")
            datetime.strptime(row[date_col], date_format)
        except ValueError:
            return False, f"Invalid date format: {row[date_col]}"

        # Validate amount
        try:
            float(row[amount_col].replace(",", "").replace(" ", ""))
        except ValueError:
            return False, f"Invalid amount: {row[amount_col]}"

        return True, None

    def is_duplicate(self, transaction: Dict) -> bool:
        """
        Check if transaction is a duplicate.

        Args:
            transaction: Transaction data

        Returns:
            True if duplicate, False otherwise
        """
        date = transaction["date"]
        amount = transaction["amount"]
        description = transaction["description"]

        for existing in self.existing_transactions:
            # Check exact match on date, amount, and description
            if (
                existing["date"] == date
                and existing["amount"] == amount
                and existing["description"] == description
            ):
                return True

            # Check external_id if present
            if transaction.get("external_id") and existing.get("external_id"):
                if transaction["external_id"] == existing["external_id"]:
                    return True

        return False

    def import_transactions(
        self,
        file_content: str,
        account_id: str,
        column_mapping: Optional[Dict[str, str]] = None,
        bank_format: Optional[str] = None,
        auto_categorize: bool = True,
    ) -> Dict:
        """
        Import transactions from CSV file.

        Args:
            file_content: CSV file content
            account_id: Account ID to associate transactions with
            column_mapping: Custom column mapping
            bank_format: Predefined bank format
            auto_categorize: Whether to auto-categorize transactions

        Returns:
            Import summary dict
        """
        # Parse CSV
        rows, headers = self.parse_csv(file_content, column_mapping, bank_format)

        # Auto-detect bank format if not provided
        if not column_mapping and not bank_format:
            detected_format = self.detect_bank_format(headers)
            if detected_format:
                column_mapping = self.BANK_FORMATS[detected_format]
            else:
                return {
                    "success": False,
                    "error": "Could not detect bank format. Please provide column mapping.",
                    "imported": 0,
                    "skipped": 0,
                    "errors": [],
                }

        # Use bank format if provided
        if bank_format and not column_mapping:
            column_mapping = self.BANK_FORMATS.get(bank_format, {})

        # Import transactions
        imported = 0
        skipped = 0
        errors = []
        imported_transactions = []

        for idx, row in enumerate(rows):
            try:
                # Validate row
                is_valid, error = self.validate_transaction(row, column_mapping)
                if not is_valid:
                    errors.append(f"Row {idx + 1}: {error}")
                    skipped += 1
                    continue

                # Parse transaction
                transaction = self._parse_transaction(
                    row, column_mapping, account_id, auto_categorize
                )

                # Check for duplicates
                if self.is_duplicate(transaction):
                    skipped += 1
                    continue

                # Add to import list
                imported_transactions.append(transaction)
                imported += 1

            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")
                skipped += 1

        # Save imported transactions
        if imported_transactions:
            try:
                for transaction in imported_transactions:
                    csv_manager.append("transactions.csv", transaction)

                # Reload existing transactions for future imports
                self._load_existing_transactions()

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to save transactions: {str(e)}",
                    "imported": 0,
                    "skipped": len(rows),
                    "errors": errors,
                }

        return {
            "success": True,
            "imported": imported,
            "skipped": skipped,
            "errors": errors,
            "total": len(rows),
        }

    def _parse_transaction(
        self,
        row: Dict,
        column_mapping: Dict[str, str],
        account_id: str,
        auto_categorize: bool,
    ) -> Dict:
        """Parse a CSV row into a transaction dict."""
        # Extract columns
        date_col = column_mapping["date_column"]
        desc_col = column_mapping["description_column"]
        amount_col = column_mapping["amount_column"]
        date_format = column_mapping.get("date_format", "%Y-%m-%d")

        # Parse date
        date_obj = datetime.strptime(row[date_col], date_format)
        date_str = date_obj.strftime("%Y-%m-%d")

        # Parse amount
        amount_str = row[amount_col].replace(",", "").replace(" ", "")
        amount = float(amount_str)

        # Description
        description = row[desc_col].strip()

        # Auto-categorize
        category_id = "cat_needs_groceries"  # Default
        if auto_categorize:
            category_id, confidence = categorizer.categorize(description, amount)

        # Generate transaction
        transaction = {
            "id": generate_transaction_id(),
            "date": date_str,
            "description": description,
            "amount": str(amount),
            "category_id": category_id,
            "account_id": account_id,
            "external_id": "",
            "notes": "",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        return transaction

    def upload_and_parse_file(
        self, file_path: Path, account_id: str, auto_categorize: bool = True
    ) -> Dict[str, Any]:
        """
        Upload and parse a bank statement file (CSV, Excel, PDF, OFX, QFX).
        Returns import preview with parsed transactions.
        """
        # Parse the file using StatementParser
        transactions, file_type = self.parser.parse_file(file_path)

        if not transactions:
            raise ValueError("No transactions found in file")

        # Load existing transactions for duplicate detection
        existing_transactions = csv_manager.read_csv("transactions.csv")

        # Process each transaction
        for txn in transactions:
            # Check for duplicates
            txn["is_duplicate"] = self._is_duplicate_transaction(
                txn, existing_transactions
            )
            txn["account_id"] = account_id

            # Auto-categorize if enabled
            if auto_categorize and not txn.get("category_id"):
                category_id, confidence = categorizer.categorize(
                    txn.get("description", ""), txn.get("amount", 0)
                )
                txn["category_id"] = category_id
                txn["category_confidence"] = confidence

            # Determine transaction type
            if "type" not in txn:
                txn["type"] = "income" if txn["amount"] > 0 else "expense"

        # Create import record
        import_id = (
            f"import_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        )

        import_record = {
            "import_id": import_id,
            "file_name": file_path.name,
            "file_type": file_type,
            "account_id": account_id,
            "total_transactions": len(transactions),
            "new_transactions": sum(1 for t in transactions if not t["is_duplicate"]),
            "duplicate_transactions": sum(1 for t in transactions if t["is_duplicate"]),
            "transactions": transactions,
            "created_at": datetime.now().isoformat(),
            "status": "pending",
        }

        # Store in memory
        self.pending_imports[import_id] = import_record

        return import_record

    def get_import_preview(self, import_id: str) -> Optional[Dict[str, Any]]:
        """Get import preview by ID."""
        return self.pending_imports.get(import_id)

    def confirm_import(
        self,
        import_id: str,
        skip_duplicates: bool = True,
        selected_transaction_indices: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Confirm and execute the import.
        Returns summary of imported transactions.
        """
        import_record = self.pending_imports.get(import_id)

        if not import_record:
            raise ValueError(f"Import not found: {import_id}")

        if import_record["status"] != "pending":
            raise ValueError(f"Import already processed: {import_id}")

        transactions = import_record["transactions"]

        # Filter transactions
        if selected_transaction_indices is not None:
            transactions = [
                transactions[i]
                for i in selected_transaction_indices
                if i < len(transactions)
            ]

        if skip_duplicates:
            transactions = [t for t in transactions if not t["is_duplicate"]]

        # Import transactions
        imported_count = 0
        skipped_count = 0
        errors = []

        for txn in transactions:
            try:
                self._save_imported_transaction(txn)
                imported_count += 1
            except Exception as e:
                errors.append({"transaction": txn, "error": str(e)})
                skipped_count += 1

        # Update import record
        import_record["status"] = "completed"
        import_record["imported_count"] = imported_count
        import_record["skipped_count"] = skipped_count
        import_record["errors"] = errors
        import_record["completed_at"] = datetime.now().isoformat()

        # Save import history
        self._save_import_history(import_record)

        return {
            "import_id": import_id,
            "imported_count": imported_count,
            "skipped_count": skipped_count,
            "errors": errors,
        }

    def get_import_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get import history."""
        try:
            history = csv_manager.read_csv("import_history.csv")
            # Sort by created_at descending
            history.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return history[:limit]
        except FileNotFoundError:
            return []

    def _is_duplicate_transaction(
        self, transaction: Dict[str, Any], existing_transactions: List[Dict[str, Any]]
    ) -> bool:
        """
        Check if transaction is a duplicate.
        Uses matching on date, description, and amount.
        """
        from fuzzywuzzy import fuzz

        txn_date = transaction.get("date")
        txn_desc = transaction.get("description", "").lower()
        txn_amount = transaction.get("amount")

        if not txn_date or not txn_desc or txn_amount is None:
            return False

        for existing in existing_transactions:
            existing_date = existing.get("date")
            existing_desc = existing.get("description", "").lower()

            try:
                existing_amount = float(existing.get("amount", 0))
            except (ValueError, TypeError):
                continue

            # Check if dates match
            if existing_date != txn_date:
                continue

            # Check if amounts match (within 0.01)
            if abs(existing_amount - txn_amount) > 0.01:
                continue

            # Check if descriptions are similar (fuzzy match)
            similarity = fuzz.ratio(txn_desc, existing_desc)
            if similarity > 85:
                return True

        return False

    def _save_imported_transaction(self, transaction: Dict[str, Any]) -> None:
        """Save an imported transaction to CSV."""
        from models.transaction import TRANSACTION_FIELDNAMES

        # Create transaction record
        txn_record = {
            "id": generate_transaction_id(),
            "date": transaction["date"],
            "description": transaction["description"],
            "amount": str(transaction["amount"]),
            "category_id": transaction.get("category_id", ""),
            "account_id": transaction["account_id"],
            "type": transaction["type"],
            "source": "import",
            "external_id": transaction.get("external_id", ""),
            "tags": transaction.get("tags", ""),
            "card_id": transaction.get("card_id", ""),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        # Save to CSV
        csv_manager.append_csv("transactions.csv", txn_record, TRANSACTION_FIELDNAMES)

    def _save_import_history(self, import_record: Dict[str, Any]) -> None:
        """Save import to history."""
        # Create simplified history record (without full transaction list)
        history_record = {
            "import_id": import_record["import_id"],
            "file_name": import_record["file_name"],
            "file_type": import_record["file_type"],
            "account_id": import_record["account_id"],
            "total_transactions": import_record["total_transactions"],
            "imported_count": import_record.get("imported_count", 0),
            "skipped_count": import_record.get("skipped_count", 0),
            "status": import_record["status"],
            "created_at": import_record["created_at"],
            "completed_at": import_record.get("completed_at", ""),
        }

        fieldnames = [
            "import_id",
            "file_name",
            "file_type",
            "account_id",
            "total_transactions",
            "imported_count",
            "skipped_count",
            "status",
            "created_at",
            "completed_at",
        ]

        try:
            csv_manager.append_csv("import_history.csv", history_record, fieldnames)
        except FileNotFoundError:
            # Create file if it doesn't exist
            csv_manager.write_csv("import_history.csv", [history_record], fieldnames)


# Global import service instance
import_service = ImportService()
