# Phase 4: Technical Specifications

**Date:** October 7, 2025  
**Version:** 1.0

---

## 1. Card Management - Technical Details

### Database Schema (CSV)

**File:** `data/cards.csv`

**Fields:**
```
id, name, card_type, last_four_digits, account_id, issuer, available_balance, current_balance, credit_limit, expiry_month, expiry_year, is_active, color, icon, created_at, updated_at
```

**Example Row:**
```csv
card_cc_001,Visa Gold Card,credit,1234,acc_creditcard,Standard Bank,6946.00,-1053.00,8000.00,12,2027,true,#3b82f6,CreditCard,2025-10-07T10:00:00,2025-10-07T10:00:00
```

### API Endpoints Specification

#### `GET /cards`
**Response:**
```json
[
  {
    "id": "card_cc_001",
    "name": "Visa Gold Card",
    "card_type": "credit",
    "last_four_digits": "1234",
    "account_id": "acc_creditcard",
    "issuer": "Standard Bank",
    "available_balance": 6946.00,
    "current_balance": -1053.00,
    "credit_limit": 8000.00,
    "expiry_month": 12,
    "expiry_year": 2027,
    "is_active": true,
    "color": "#3b82f6",
    "icon": "CreditCard",
    "created_at": "2025-10-07T10:00:00",
    "updated_at": "2025-10-07T10:00:00"
  }
]
```

#### `GET /cards/{card_id}/analytics`
**Response:**
```json
{
  "card_id": "card_cc_001",
  "total_transactions": 45,
  "total_spent": 15234.50,
  "average_transaction": 338.54,
  "spending_by_category": {
    "cat_food": 3500.00,
    "cat_transport": 2000.00
  },
  "monthly_spending": {
    "2025-09": 5000.00,
    "2025-10": 3500.00
  },
  "credit_utilization": 13.16
}
```

### Transaction Model Enhancement

**Updated TRANSACTION_FIELDNAMES:**
```python
TRANSACTION_FIELDNAMES = [
    'id', 'date', 'description', 'amount', 'category_id', 'account_id',
    'card_id',  # NEW FIELD
    'type', 'currency', 'source', 'external_id', 'tags', 'created_at', 'updated_at'
]
```

**Migration Strategy:**
- Add `card_id` column to existing transactions.csv
- Default value: empty string for existing transactions
- Update all transaction create/update operations

---

## 2. Bank Statement Import - Technical Details

### Supported File Formats

#### **CSV Format**
**Detection:** File extension `.csv`
**Parser:** Python csv.DictReader
**Features:**
- Auto-detect delimiter (comma, semicolon, tab)
- Auto-detect header row
- Column mapping suggestions

**Example:**
```csv
Date,Description,Amount,Balance
2025-10-01,Grocery Store,-250.00,5000.00
2025-10-02,Salary,+15000.00,20000.00
```

#### **Excel Format (.xlsx, .xls)**
**Detection:** File extension `.xlsx` or `.xls`
**Parser:** openpyxl (xlsx), xlrd (xls)
**Features:**
- Read first sheet with data
- Auto-detect header row
- Support merged cells
- Handle formulas (read calculated values)

**Example Structure:**
| Date | Description | Debit | Credit | Balance |
|------|-------------|-------|--------|---------|
| 2025-10-01 | Grocery | 250.00 | | 5000.00 |
| 2025-10-02 | Salary | | 15000.00 | 20000.00 |

#### **PDF Format**
**Detection:** File extension `.pdf`
**Parser:** pdfplumber
**Features:**
- Text extraction from PDF
- Pattern matching for transaction lines
- Support for table structures
- Multi-page support

**Pattern Matching:**
```python
# Common patterns
DATE_PATTERN = r'\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}'
AMOUNT_PATTERN = r'[-+]?R?\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
```

**Supported Layouts:**
- Standard Bank statement format
- FNB statement format
- Capitec statement format
- Generic table-based layouts

#### **OFX/QFX Format**
**Detection:** File extension `.ofx` or `.qfx`
**Parser:** ofxparse library
**Features:**
- Standard OFX 1.x and 2.x support
- Automatic transaction extraction
- Date/amount parsing
- Memo/description extraction

**Example OFX:**
```xml
<OFX>
  <BANKMSGSRSV1>
    <STMTTRNRS>
      <STMTRS>
        <BANKTRANLIST>
          <STMTTRN>
            <TRNTYPE>DEBIT</TRNTYPE>
            <DTPOSTED>20251001</DTPOSTED>
            <TRNAMT>-250.00</TRNAMT>
            <NAME>Grocery Store</NAME>
          </STMTTRN>
        </BANKTRANLIST>
      </STMTRS>
    </STMTTRNRS>
  </BANKMSGSRSV1>
</OFX>
```

### File Upload API

#### `POST /import/statement`
**Request:**
```
Content-Type: multipart/form-data

file: <binary file data>
account_id: acc_main
card_id: card_cc_001 (optional)
auto_categorize: true
skip_duplicates: true
```

**Response:**
```json
{
  "success": true,
  "filename": "statement_oct_2025.pdf",
  "format": "pdf",
  "detected_bank": "Standard Bank",
  "imported": 45,
  "skipped": 3,
  "duplicates": 2,
  "errors": [],
  "date_range": {
    "start": "2025-10-01",
    "end": "2025-10-31"
  }
}
```

#### `POST /import/statements/batch`
**Request:**
```
Content-Type: multipart/form-data

files[]: <file1>
files[]: <file2>
files[]: <file3>
account_id: acc_main
auto_categorize: true
```

**Response:**
```json
{
  "total_files": 3,
  "successful_files": 2,
  "failed_files": 1,
  "total_imported": 87,
  "total_skipped": 5,
  "file_results": [
    {
      "filename": "statement1.csv",
      "success": true,
      "imported": 45,
      "skipped": 2
    },
    {
      "filename": "statement2.pdf",
      "success": true,
      "imported": 42,
      "skipped": 3
    },
    {
      "filename": "statement3.ofx",
      "success": false,
      "error": "Invalid OFX format"
    }
  ]
}
```

#### `POST /import/preview`
**Request:**
```
Content-Type: multipart/form-data

file: <binary file data>
```

**Response:**
```json
{
  "filename": "statement.pdf",
  "format": "pdf",
  "detected_bank": "FNB",
  "transaction_count": 45,
  "date_range": {
    "start": "2025-10-01",
    "end": "2025-10-31"
  },
  "sample_transactions": [
    {
      "date": "2025-10-01",
      "description": "Grocery Store",
      "amount": -250.00,
      "suggested_category": "cat_food",
      "confidence": 0.95
    }
  ],
  "duplicates_found": 2,
  "errors": []
}
```

### Duplicate Detection Algorithm

```python
def is_duplicate(new_transaction: Dict, existing_transactions: List[Dict]) -> bool:
    """
    Check if transaction is a duplicate.
    
    Matching criteria:
    1. Same account_id
    2. Same date (within 1 day tolerance)
    3. Same amount (exact match)
    4. Similar description (90% similarity using fuzzy matching)
    """
    for existing in existing_transactions:
        if (
            existing['account_id'] == new_transaction['account_id'] and
            abs((parse_date(existing['date']) - parse_date(new_transaction['date'])).days) <= 1 and
            abs(float(existing['amount']) - float(new_transaction['amount'])) < 0.01 and
            fuzz.ratio(existing['description'], new_transaction['description']) >= 90
        ):
            return True
    return False
```

---

## 3. Real Data Import - Seeding Script

### Script Structure

**File:** `backend/scripts/seed_real_data.py`

```python
#!/usr/bin/env python3
"""
Seed FIN-DASH with real account data.

Usage:
    python backend/scripts/seed_real_data.py [--clear] [--dry-run] [--verbose]

Options:
    --clear     Clear existing data before seeding
    --dry-run   Show what would be created without creating
    --verbose   Show detailed output
"""

import argparse
import requests
from datetime import datetime

API_BASE = "http://127.0.0.1:8777/api"

def create_accounts():
    """Create all accounts."""
    accounts = [...]  # Account data
    for account in accounts:
        response = requests.post(f"{API_BASE}/accounts", json=account)
        # Handle response

def create_cards():
    """Create all cards."""
    # Similar structure

def create_categories():
    """Create all categories."""
    # Similar structure

def create_budget():
    """Create current month budget."""
    # Similar structure

def main():
    parser = argparse.ArgumentParser(description="Seed FIN-DASH with real data")
    parser.add_argument("--clear", action="store_true", help="Clear existing data")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.clear:
        # Clear existing data with confirmation
        pass
    
    # Create data
    create_accounts()
    create_cards()
    create_categories()
    create_budget()
    
    print("✅ Data seeding complete!")

if __name__ == "__main__":
    main()
```

### Data Validation

**Pre-seeding Checks:**
1. Verify API is running
2. Check for existing data
3. Validate account types
4. Validate category groups
5. Validate budget amounts

**Post-seeding Verification:**
1. Verify all accounts created
2. Verify all cards created
3. Verify all categories created
4. Verify budget created
5. Calculate and verify balances

---

## 4. Frontend Components Specification

### Card Management Components

#### **CardList.tsx**
**Props:** None
**Features:**
- Display all cards in grid layout
- Show available balance and current balance
- Color-coded by card type
- Click to view details
- Edit and delete actions

#### **CardCreateDialog.tsx**
**Props:**
```typescript
interface CardCreateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}
```
**Features:**
- Form with all card fields
- Account selector dropdown
- Card type selector
- Expiry date pickers
- Color picker
- Icon selector

#### **CardSelector.tsx** (Reusable)
**Props:**
```typescript
interface CardSelectorProps {
  value: string;
  onValueChange: (value: string) => void;
  accountId?: string;  // Filter cards by account
  placeholder?: string;
}
```

### Statement Import Components

#### **StatementImportDialog.tsx**
**Props:**
```typescript
interface StatementImportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}
```
**Features:**
- Drag & drop zone
- Multiple file selection
- File format detection
- Preview before import
- Progress tracking
- Error display

#### **FileUploadZone.tsx** (Reusable)
**Props:**
```typescript
interface FileUploadZoneProps {
  onFilesSelected: (files: File[]) => void;
  acceptedFormats: string[];
  maxFiles?: number;
  maxSize?: number;  // in MB
}
```

---

## 5. Testing Strategy

### Unit Tests
- Card CRUD operations
- File format detection
- Transaction parsing for each format
- Duplicate detection algorithm
- Balance calculations

### Integration Tests
- End-to-end card management flow
- Statement import flow for each format
- Batch import with multiple files
- Data seeding script execution

### UI Tests
- Card list display
- Card create/edit forms
- Drag & drop file upload
- Import preview
- Progress tracking

---

**Implementation ready to begin!**

