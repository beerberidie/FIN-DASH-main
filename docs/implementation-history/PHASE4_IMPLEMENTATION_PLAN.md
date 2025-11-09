# Phase 4: FIN-DASH Enhancement Implementation Plan

**Date:** October 7, 2025  
**Status:** Planning Phase  
**Estimated Duration:** 3-4 days

---

## 📋 Overview

This document outlines the implementation plan for three major enhancements to FIN-DASH:

1. **Card Management Section** - Track payment cards linked to accounts
2. **Bank Statement Import (Drag & Drop)** - Advanced file upload with multi-format support
3. **Real Account Data Import** - Populate with actual financial data

---

## 🎯 Feature 1: Card Management Section

### **Objective**
Create a comprehensive card management system to track credit cards, debit cards, and other payment methods linked to accounts.

### **Backend Implementation**

#### **1.1 Data Model** (`backend/models/card.py`)
```python
class Card(BaseModel):
    id: str
    name: str  # e.g., "Visa Gold Card", "Debit Card"
    card_type: Literal["credit", "debit", "prepaid", "virtual"]
    last_four_digits: str  # Last 4 digits for identification
    account_id: str  # Linked account
    issuer: str  # e.g., "Standard Bank", "FNB", "Capitec"
    available_balance: float  # For credit cards: available credit
    current_balance: float  # For credit cards: amount owed (negative)
    credit_limit: Optional[float]  # For credit cards
    expiry_month: Optional[int]  # 1-12
    expiry_year: Optional[int]  # YYYY
    is_active: bool
    color: str  # Hex color for UI
    icon: str  # Icon name
    created_at: str
    updated_at: str
```

**CSV Fields:**
- `id, name, card_type, last_four_digits, account_id, issuer, available_balance, current_balance, credit_limit, expiry_month, expiry_year, is_active, color, icon, created_at, updated_at`

#### **1.2 API Endpoints** (`backend/routers/cards.py`)
- `GET /cards` - List all cards
- `GET /cards/{card_id}` - Get card details
- `GET /cards/{card_id}/balance` - Get card balance
- `GET /cards/{card_id}/transactions` - Get transactions for a card
- `GET /cards/{card_id}/analytics` - Get spending analytics for a card
- `POST /cards` - Create a new card
- `PUT /cards/{card_id}` - Update card details
- `DELETE /cards/{card_id}` - Delete a card

#### **1.3 Transaction Model Enhancement**
Add `card_id` field to Transaction model:
```python
card_id: Optional[str] = None  # Link transaction to specific card
```

Update `TRANSACTION_FIELDNAMES` to include `card_id`.

#### **1.4 Card Service** (`backend/services/card_service.py`)
- Calculate card balances
- Get card-specific spending analytics
- Validate card-account linkage
- Calculate credit utilization

### **Frontend Implementation**

#### **1.5 Components**
1. **CardList.tsx** - Display all cards with balances
2. **CardCreateDialog.tsx** - Form to add new card
3. **CardEditDialog.tsx** - Form to edit card
4. **CardDetailsCard.tsx** - Card details display component
5. **CardAnalytics.tsx** - Card-specific spending charts
6. **CardSelector.tsx** - Reusable dropdown for selecting cards

#### **1.6 Page**
- **Cards.tsx** (`/cards`) - Main cards management page with tabs:
  - Overview: All cards with balances
  - Analytics: Card-specific spending analysis
  - Transactions: Filter transactions by card

#### **1.7 Integration**
- Add card selector to transaction create/edit forms
- Add "Cards" navigation button to main dashboard
- Update transaction list to show card information

---

## 🎯 Feature 2: Bank Statement Import (Drag & Drop)

### **Objective**
Implement advanced file upload with support for multiple bank statement formats (PDF, CSV, Excel, OFX, QFX).

### **Backend Implementation**

#### **2.1 File Parser Service** (`backend/services/statement_parser.py`)

**Supported Formats:**
1. **CSV** - Already supported, enhance with better detection
2. **Excel (.xlsx, .xls)** - Use openpyxl/xlrd
3. **PDF** - Use PyPDF2 or pdfplumber for text extraction
4. **OFX/QFX** - Use ofxparse library
5. **JSON** - Generic JSON format

**Dependencies to Add:**
```
openpyxl==3.1.5  # Already installed
xlrd==2.0.1  # For older Excel files
pdfplumber==0.11.0  # PDF parsing
ofxparse==0.21  # OFX/QFX parsing
```

**Parser Structure:**
```python
class StatementParser:
    def detect_format(self, file_content: bytes, filename: str) -> str
    def parse_csv(self, content: str) -> List[Dict]
    def parse_excel(self, content: bytes) -> List[Dict]
    def parse_pdf(self, content: bytes) -> List[Dict]
    def parse_ofx(self, content: bytes) -> List[Dict]
    def extract_transactions(self, file_content: bytes, format: str) -> List[Dict]
```

#### **2.2 Enhanced Import Service** (`backend/services/import_service.py`)

**New Features:**
- Multi-file batch processing
- Format auto-detection
- Preview before import
- Duplicate detection across files
- Transaction mapping suggestions
- Error reporting per file

**New Methods:**
```python
def import_statement_file(self, file_content: bytes, filename: str, account_id: str) -> Dict
def batch_import_statements(self, files: List[Tuple[bytes, str]], account_id: str) -> Dict
def preview_statement(self, file_content: bytes, filename: str) -> Dict
def detect_bank_from_statement(self, transactions: List[Dict]) -> Optional[str]
```

#### **2.3 API Endpoints** (`backend/routers/import_router.py`)

**New Endpoints:**
- `POST /import/statement` - Import single statement file (any format)
- `POST /import/statements/batch` - Import multiple statement files
- `POST /import/preview` - Preview transactions before import
- `GET /import/supported-formats` - List supported file formats
- `POST /import/detect-format` - Detect file format

#### **2.4 Models** (`backend/models/import_models.py`)
```python
class StatementImportRequest(BaseModel):
    account_id: str
    card_id: Optional[str]
    auto_categorize: bool = True
    skip_duplicates: bool = True

class StatementPreview(BaseModel):
    filename: str
    format: str
    detected_bank: Optional[str]
    transaction_count: int
    date_range: Dict[str, str]
    sample_transactions: List[Dict]
    duplicates_found: int
    errors: List[str]

class BatchImportResult(BaseModel):
    total_files: int
    successful_files: int
    failed_files: int
    total_imported: int
    total_skipped: int
    file_results: List[Dict]
```

### **Frontend Implementation**

#### **2.5 Components**
1. **StatementImportDialog.tsx** - Drag & drop file upload
2. **FileUploadZone.tsx** - Reusable drag & drop zone
3. **ImportPreview.tsx** - Preview transactions before import
4. **BatchImportProgress.tsx** - Progress indicator for batch imports
5. **FormatDetector.tsx** - Show detected file format

#### **2.6 Features**
- Drag & drop multiple files
- File format icons and validation
- Preview transactions with mapping
- Batch progress tracking
- Error handling per file
- Success/failure summary

#### **2.7 Integration**
- Replace existing CSVImportDialog with StatementImportDialog
- Add to main dashboard and transactions page
- Support for multiple file selection

---

## 🎯 Feature 3: Real Account Data Import

### **Objective**
Populate FIN-DASH with actual financial data using a seeding script.

### **Implementation**

#### **3.1 Data Seeding Script** (`backend/scripts/seed_real_data.py`)

**Accounts to Create:**
```python
accounts = [
    {
        "name": "Easy Account",
        "type": "bank",
        "opening_balance": 181.0,
        "is_active": True
    },
    {
        "name": "CreditCard",
        "type": "bank",  # Will be linked to credit card
        "opening_balance": 0.0,  # Credit cards start at 0
        "is_active": True
    },
    {
        "name": "Ebucks",
        "type": "virtual",  # Rewards account
        "opening_balance": 19731.0,  # eBucks points
        "is_active": True
    },
    {
        "name": "Savings",
        "type": "bank",
        "opening_balance": 566.0,
        "is_active": True
    },
    {
        "name": "Share Investor",
        "type": "investment",
        "opening_balance": 231.0,
        "is_active": True
    }
]
```

**Cards to Create:**
```python
cards = [
    {
        "name": "Credit Card",
        "card_type": "credit",
        "last_four_digits": "****",  # User can update
        "account_id": "acc_creditcard",
        "issuer": "Bank",
        "available_balance": 6946.0,
        "current_balance": -1053.0,
        "credit_limit": 8000.0,
        "is_active": True,
        "color": "#3b82f6",
        "icon": "CreditCard"
    }
]
```

**Categories to Create:**
```python
expense_categories = [
    {"name": "Food", "group": "needs", "budget": 2000.00},
    {"name": "Gifts", "group": "wants", "budget": 0.00},
    {"name": "Health/Medical", "group": "needs", "budget": 2017.00},
    {"name": "Home", "group": "needs", "budget": 2000.00},
    {"name": "Transportation", "group": "needs", "budget": 2000.00},
    {"name": "Personal", "group": "wants", "budget": 3000.00},
    {"name": "Pets", "group": "wants", "budget": 0.00},
    {"name": "Utilities", "group": "needs", "budget": 500.00},
    {"name": "Travel", "group": "wants", "budget": 0.00},
    {"name": "Debt", "group": "debt", "budget": 0.00},
    {"name": "Other", "group": "wants", "budget": 0.00},
    {"name": "Wifi", "group": "needs", "budget": 300.00},
    {"name": "Gap Cover", "group": "needs", "budget": 138.00},
    {"name": "YouTube Premium", "group": "wants", "budget": 100.00},
    {"name": "YouTube Music", "group": "wants", "budget": 60.00},
    {"name": "Spotify", "group": "wants", "budget": 90.00},
    {"name": "Netflix", "group": "wants", "budget": 159.00},
    {"name": "Bike Insurance", "group": "needs", "budget": 338.00},
    {"name": "Bank Charges", "group": "needs", "budget": 150.00},
    {"name": "Cell Phone", "group": "needs", "budget": 250.00},
    {"name": "Liberty (Insurance)", "group": "needs", "budget": 700.00},
]

income_categories = [
    {"name": "Paycheck", "group": "income", "budget": 11500.00},
    {"name": "Savings", "group": "savings", "budget": 0.00},
    {"name": "Bonus", "group": "income", "budget": 0.00},
    {"name": "Interest", "group": "income", "budget": 0.00},
    {"name": "Other Income", "group": "income", "budget": 0.00},
    {"name": "Custom Category", "group": "income", "budget": 0.00},
]
```

**Budget to Create:**
```python
# Current month budget
budget = {
    "year": 2025,
    "month": 10,  # October
    "needs_planned": 8393.00,  # Sum of needs categories
    "wants_planned": 3409.00,  # Sum of wants categories
    "savings_planned": 0.00,
    "notes": "Initial budget setup"
}
```

#### **3.2 Script Features**
- Check for existing data before creating
- Use API endpoints to create data (ensures validation)
- Create accounts, cards, categories, and budget
- Generate summary report
- Option to clear existing data first (with confirmation)

#### **3.3 Execution**
```bash
python backend/scripts/seed_real_data.py
```

**Options:**
- `--clear` - Clear existing data first
- `--dry-run` - Show what would be created without creating
- `--verbose` - Show detailed output

---

## 📊 Implementation Timeline

### **Week 1: Card Management (Days 1-2)**
- Day 1: Backend (models, API, service)
- Day 2: Frontend (components, page, integration)

### **Week 2: Statement Import (Days 3-4)**
- Day 3: Backend (parsers, enhanced import service, API)
- Day 4: Frontend (drag & drop, preview, batch processing)

### **Week 3: Data Seeding (Day 5)**
- Day 5: Create seeding script, test, execute

---

## 🔧 Technical Specifications

### **File Format Support Details**

#### **CSV Format**
- Already supported
- Enhance with better column detection
- Support for multiple CSV variants

#### **Excel Format (.xlsx, .xls)**
- Use openpyxl for .xlsx
- Use xlrd for .xls
- Auto-detect header row
- Support multiple sheets (use first sheet with data)

#### **PDF Format**
- Use pdfplumber for text extraction
- Pattern matching for transaction lines
- Support for common bank statement layouts
- OCR fallback for scanned PDFs (optional, future enhancement)

#### **OFX/QFX Format**
- Use ofxparse library
- Standard format used by many banks
- Direct transaction extraction
- Automatic date/amount parsing

#### **JSON Format**
- Generic JSON structure
- Configurable field mapping
- Useful for API imports

### **Duplicate Detection Strategy**

**Matching Criteria:**
1. Same account_id
2. Same date
3. Same amount
4. Similar description (fuzzy matching with 90% threshold)

**Hash Generation:**
```python
def generate_transaction_hash(account_id, date, amount, description):
    normalized_desc = description.lower().strip()
    return hashlib.md5(f"{account_id}|{date}|{amount}|{normalized_desc}".encode()).hexdigest()
```

---

## 📦 Dependencies to Add

```txt
# requirements.txt additions
xlrd==2.0.1  # Excel .xls support
pdfplumber==0.11.0  # PDF parsing
ofxparse==0.21  # OFX/QFX parsing
python-magic==0.4.27  # File type detection (optional)
```

---

## ✅ Success Criteria

### **Card Management**
- [ ] Create, read, update, delete cards
- [ ] Link cards to accounts
- [ ] Track card balances (available and current)
- [ ] Link transactions to cards
- [ ] View card-specific analytics
- [ ] Display cards on dashboard

### **Statement Import**
- [ ] Support CSV, Excel, PDF, OFX, QFX formats
- [ ] Drag & drop multiple files
- [ ] Preview transactions before import
- [ ] Batch processing with progress tracking
- [ ] Duplicate detection across files
- [ ] Error handling per file
- [ ] Success/failure summary

### **Real Data Import**
- [ ] All 5 accounts created
- [ ] Credit card created and linked
- [ ] All 27 categories created
- [ ] Budget created for current month
- [ ] Data displayed correctly in UI
- [ ] Balances calculated correctly

---

## 🚀 Next Steps

1. Review and approve this implementation plan
2. Install required dependencies
3. Implement Feature 1: Card Management
4. Implement Feature 2: Statement Import
5. Implement Feature 3: Data Seeding
6. Test all features
7. Create documentation

---

**Ready to proceed with implementation?**

