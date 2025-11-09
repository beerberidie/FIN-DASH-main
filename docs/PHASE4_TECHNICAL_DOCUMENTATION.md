# FIN-DASH Phase 4 Technical Documentation

## Architecture Overview

Phase 4 introduces three major features built on FIN-DASH's CSV-based, local-first architecture:

1. **Card Management System** - Track payment cards with balance calculation and analytics
2. **Multi-Format Statement Parser** - Import transactions from CSV, Excel, PDF, OFX, QFX
3. **Data Seeding System** - Populate with realistic financial data

---

## 1. Card Management System

### Backend Architecture

#### Data Model (`backend/models/card.py`)

```python
class Card(BaseModel):
    id: str                    # Unique identifier (card_YYYYMMDDHHMMSS_XXXX)
    name: str                  # Card name
    card_type: str            # credit, debit, prepaid, virtual
    account_id: str           # Linked account ID
    last_four: Optional[str]  # Last 4 digits
    credit_limit: Optional[float]  # For credit cards
    expiry_month: Optional[int]    # 1-12
    expiry_year: Optional[int]     # YYYY
    is_active: bool           # Active status
    color: str                # Hex color code
    icon: str                 # Icon name
    created_at: str           # ISO timestamp
    updated_at: str           # ISO timestamp
```

**Storage:** `data/cards.csv`

#### Service Layer (`backend/services/card_service.py`)

**Key Methods:**

- `get_all_cards()` - Retrieve all cards
- `get_card(card_id)` - Get single card by ID
- `create_card(card_data)` - Create new card with validation
- `update_card(card_id, card_data)` - Update existing card
- `delete_card(card_id)` - Delete card (soft delete)
- `get_card_balance(card_id)` - Calculate current and available balance
- `get_card_transactions(card_id)` - Get all transactions for card
- `get_card_analytics(card_id, months)` - Generate spending analytics

**Balance Calculation Logic:**

```python
# For credit cards:
current_balance = sum(all_transactions)
available_balance = credit_limit - current_balance
credit_utilization = (current_balance / credit_limit) * 100

# For debit/prepaid cards:
current_balance = sum(all_transactions)
available_balance = current_balance
```

**Analytics Calculation:**

- **Spending by Category:** Group transactions by category, sum amounts
- **Monthly Spending:** Group by month, calculate totals
- **Top Categories:** Sort categories by total spending

#### API Layer (`backend/routers/cards.py`)

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cards` | List all cards |
| GET | `/api/cards/{id}` | Get card details |
| POST | `/api/cards` | Create new card |
| PUT | `/api/cards/{id}` | Update card |
| DELETE | `/api/cards/{id}` | Delete card |
| GET | `/api/cards/{id}/balance` | Get card balance |
| GET | `/api/cards/{id}/transactions` | Get card transactions |
| GET | `/api/cards/{id}/analytics` | Get card analytics |

**Validation:**
- Account must exist before creating card
- Card type must be: credit, debit, prepaid, or virtual
- Credit limit required for credit cards
- Expiry month must be 1-12
- Expiry year must be current year or later

### Frontend Architecture

#### Components

**1. CardList (`src/components/CardList.tsx`)**
- Grid layout displaying all cards
- Color-coded card types
- Balance and utilization display
- Action buttons (edit, delete, analytics)

**2. CardCreateDialog (`src/components/CardCreateDialog.tsx`)**
- Form for creating new cards
- Account selection dropdown
- Card type selection
- Credit limit input (conditional)
- Expiry date picker
- Color picker
- Icon selector

**3. CardEditDialog (`src/components/CardEditDialog.tsx`)**
- Pre-populated form for editing
- Same fields as create dialog
- Update functionality

**4. CardAnalyticsDialog (`src/components/CardAnalyticsDialog.tsx`)**
- Spending by category (pie chart)
- Monthly spending trend (line chart)
- Top categories list
- Transaction count

**5. Cards Page (`src/pages/Cards.tsx`)**
- Main page container
- Header with "Add Card" button
- CardList component
- Dialog management

#### State Management

Uses **TanStack React Query** for:
- Fetching cards (`useQuery`)
- Creating cards (`useMutation`)
- Updating cards (`useMutation`)
- Deleting cards (`useMutation`)
- Cache invalidation after mutations

#### API Client (`src/services/api.ts`)

```typescript
// Card interfaces
interface Card { ... }
interface CardCreate { ... }
interface CardUpdate { ... }
interface CardBalance { ... }
interface CardAnalytics { ... }

// API functions
getCards(): Promise<Card[]>
getCard(id: string): Promise<Card>
createCard(card: CardCreate): Promise<Card>
updateCard(id: string, card: CardUpdate): Promise<Card>
deleteCard(id: string): Promise<void>
getCardBalance(id: string): Promise<CardBalance>
getCardTransactions(id: string): Promise<Transaction[]>
getCardAnalytics(id: string, months?: number): Promise<CardAnalytics>
```

---

## 2. Bank Statement Import System

### Backend Architecture

#### Statement Parser (`backend/services/statement_parser.py`)

**Supported Formats:**
- CSV (.csv)
- Excel (.xls, .xlsx)
- PDF (.pdf)
- OFX/QFX (.ofx, .qfx)

**Key Methods:**

```python
class StatementParser:
    @staticmethod
    def parse_file(file_path: Path) -> Tuple[List[Dict], str]:
        """Main entry point - detects format and parses"""
        
    @staticmethod
    def parse_csv(file_path: Path) -> List[Dict]:
        """Parse CSV with auto-detection"""
        
    @staticmethod
    def parse_excel(file_path: Path) -> List[Dict]:
        """Parse Excel (.xls, .xlsx)"""
        
    @staticmethod
    def parse_pdf(file_path: Path) -> List[Dict]:
        """Parse PDF with regex patterns"""
        
    @staticmethod
    def parse_ofx(file_path: Path) -> List[Dict]:
        """Parse OFX/QFX files"""
```

**Column Detection Algorithm:**

1. Read first row as headers
2. For each required column (date, description, amount):
   - Try exact match (case-insensitive)
   - Try fuzzy match (80% similarity threshold)
   - Use common variations (e.g., "desc", "transaction", "memo")
3. Return column mapping or raise error

**Date Parsing:**

Supports 15+ date formats:
- `YYYY-MM-DD`, `YYYY/MM/DD`
- `DD-MM-YYYY`, `DD/MM/YYYY`
- `MM-DD-YYYY`, `MM/DD/YYYY`
- `DD MMM YYYY`, `MMM DD, YYYY`
- And more...

**Amount Parsing:**

Handles:
- Currency symbols (R, $, €, £)
- Thousands separators (,)
- Decimal separators (.)
- Negative indicators (-, parentheses)
- Debit/Credit columns

#### Import Service (`backend/services/import_service.py`)

**Import Workflow:**

```
1. Upload File → Parse → Create Preview
2. Store in pending_imports dict with unique ID
3. User reviews preview
4. Confirm import → Filter duplicates → Save to CSV
5. Update import history
```

**Key Methods:**

```python
def upload_and_parse_file(
    file_path: Path,
    account_id: str,
    auto_categorize: bool = True
) -> Dict[str, Any]:
    """Upload and parse file, return preview"""
    
def get_import_preview(import_id: str) -> Optional[Dict]:
    """Get preview by ID"""
    
def confirm_import(
    import_id: str,
    skip_duplicates: bool = True,
    selected_transaction_indices: Optional[List[int]] = None
) -> Dict[str, Any]:
    """Execute import"""
```

**Duplicate Detection:**

Uses fuzzy matching (85% similarity):
```python
def _is_duplicate_transaction(new_tx: Dict, existing_tx: Dict) -> bool:
    # Check date (within 1 day)
    date_match = abs(date_diff) <= 1
    
    # Check description (85% similarity)
    desc_similarity = fuzz.ratio(desc1, desc2)
    desc_match = desc_similarity >= 85
    
    # Check amount (exact match)
    amount_match = abs(amount1 - amount2) < 0.01
    
    return date_match and desc_match and amount_match
```

**Auto-Categorization:**

1. Get all existing transactions
2. For each new transaction:
   - Find similar descriptions (fuzzy match)
   - Get category from most similar transaction
   - Assign category if similarity > 80%

#### API Layer (`backend/routers/import_router.py`)

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/import/upload` | Upload and parse file |
| GET | `/api/import/preview/{id}` | Get import preview |
| POST | `/api/import/confirm/{id}` | Confirm import |
| GET | `/api/import/history` | Get import history |
| GET | `/api/import/formats` | Get supported formats |

**Request/Response Models:**

```python
class ImportPreviewResponse(BaseModel):
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
    skip_duplicates: bool = True
    selected_transaction_indices: Optional[List[int]] = None

class ImportConfirmResponse(BaseModel):
    import_id: str
    imported_count: int
    skipped_count: int
    errors: List[Dict[str, Any]]
```

### Frontend Architecture

#### Components

**1. FileUploadZone (`src/components/FileUploadZone.tsx`)**
- Drag & drop interface
- File validation (type, size)
- Visual feedback
- File preview

**2. ImportPreview (`src/components/ImportPreview.tsx`)**
- Transaction summary cards
- Scrollable transaction table
- Checkbox selection
- Duplicate badges
- Category display

**3. ImportProgress (`src/components/ImportProgress.tsx`)**
- Status indicators
- Progress bar
- Results summary
- Error display

**4. StatementImportDialog (`src/components/StatementImportDialog.tsx`)**
- Multi-step wizard
- Account selection
- File upload
- Transaction preview
- Import confirmation
- Results display

#### Import Flow

```
Step 1: Upload
- Select account
- Upload file
- Toggle auto-categorize
- Click "Upload & Parse"

Step 2: Preview
- View parsed transactions
- See duplicates flagged
- Select/deselect transactions
- Toggle skip duplicates
- Click "Import X Transaction(s)"

Step 3: Importing
- Show progress indicator
- Wait for completion

Step 4: Complete
- Show results summary
- Display imported/skipped/error counts
- Click "Done" to close
```

---

## 3. Data Seeding System

### Seeding Script (`backend/scripts/seed_real_data.py`)

**Purpose:** Populate FIN-DASH with realistic financial data for testing/demo

**Included Data:**

1. **Accounts (5)**
   - FNB Cheque Account (checking)
   - FNB Easy Account (checking)
   - FNB Credit Card (credit)
   - FNB eBucks Savings (savings)
   - FNB Share Investor (investment)

2. **Cards (1)**
   - FNB Gold Credit Card (R30,000 limit)

3. **Categories (27)**
   - Income: Salary, Freelance, Investment Income, etc.
   - Expenses: Groceries, Rent, Utilities, etc.
   - Savings: Emergency Fund, Retirement, etc.

4. **Budget (October 2025)**
   - Realistic allocations for all categories

5. **Transactions**
   - Sample transactions for October 2025

**Usage:**

```bash
# Run seeding script
python backend/scripts/seed_real_data.py --verbose

# Options:
--verbose    Show detailed output
```

**Implementation:**

```python
def seed_accounts():
    """Create 5 realistic accounts"""
    
def seed_cards():
    """Create 1 credit card"""
    
def seed_categories():
    """Create 27 categories"""
    
def seed_budget():
    """Create October 2025 budget"""
    
def seed_transactions():
    """Create sample transactions"""
```

---

## Dependencies

### Backend

**New Dependencies (Phase 4):**
```
xlrd==2.0.1              # Excel .xls parsing
openpyxl                 # Excel .xlsx parsing
pdfplumber==0.11.0       # PDF parsing
ofxparse==0.21           # OFX/QFX parsing
fuzzywuzzy==0.18.0       # Fuzzy string matching
python-Levenshtein==0.25.0  # Fast fuzzy matching
```

### Frontend

No new dependencies required. Uses existing:
- React 18.3.1
- TanStack React Query
- shadcn/ui components
- Lucide React icons

---

## Data Storage

### CSV Files

**cards.csv:**
```csv
id,name,card_type,account_id,last_four,credit_limit,expiry_month,expiry_year,is_active,color,icon,created_at,updated_at
```

**import_history.csv:**
```csv
import_id,file_name,file_type,account_id,total_transactions,imported_count,skipped_count,status,created_at,completed_at
```

### In-Memory Storage

**Pending Imports:**
- Stored in `ImportService.pending_imports` dictionary
- Key: import_id
- Value: import preview data
- Cleared after confirmation or timeout

---

## Performance Considerations

### Card Management
- Balance calculation: O(n) where n = number of transactions
- Analytics calculation: O(n*m) where m = number of categories
- Optimization: Cache balances, recalculate only on transaction changes

### Statement Import
- CSV parsing: O(n) where n = number of rows
- Duplicate detection: O(n*m) where m = existing transactions
- Optimization: Use fuzzy matching library with C extensions (python-Levenshtein)

### Data Seeding
- One-time operation
- No performance concerns

---

## Security Considerations

### Card Data
- Card numbers stored as last 4 digits only
- No CVV or full card number storage
- Local-first architecture (no external transmission)

### File Upload
- File size limit: 10MB
- File type validation
- Temporary file cleanup after processing
- No persistent storage of uploaded files

### Data Privacy
- All data stored locally in CSV files
- No authentication required (single-user)
- No external API calls
- No data transmission to external servers

---

## Testing

### Backend Testing

**Card Management:**
```bash
# Test card creation
python test_card_api.py
```

**Statement Import:**
```bash
# Test CSV import
curl -X POST http://localhost:8777/api/import/upload \
  -F "file=@test_data/sample_bank_statement.csv" \
  -F "account_id=acc_main" \
  -F "auto_categorize=true"
```

### Frontend Testing

1. Start dev server: `npm run dev`
2. Navigate to http://localhost:8081
3. Test card management features
4. Test statement import with sample files

---

## Troubleshooting

### Common Issues

**Issue:** Card creation fails with "Account not found"
- **Cause:** DATA_DIR path incorrect
- **Solution:** Check `backend/.env` has `DATA_DIR=data`

**Issue:** Import fails with "Unsupported file type"
- **Cause:** File extension not recognized
- **Solution:** Ensure file has .csv, .xls, .xlsx, .pdf, .ofx, or .qfx extension

**Issue:** Duplicate detection not working
- **Cause:** Similarity threshold too high
- **Solution:** Adjust threshold in `import_service.py` (default 85%)

**Issue:** Auto-categorization assigns wrong categories
- **Cause:** Insufficient historical data
- **Solution:** Manually categorize more transactions to improve matching

---

## Future Enhancements

### Card Management
- Card rewards tracking
- Card payment reminders
- Multi-currency card support
- Card statement reconciliation

### Statement Import
- Scheduled imports
- Email import (forward statements to email)
- Bank API integration
- Machine learning for categorization

### Data Seeding
- Multiple data sets (different countries, scenarios)
- Custom data generation
- Import from real bank data

---

**Last Updated:** October 8, 2025  
**Version:** Phase 4.0

