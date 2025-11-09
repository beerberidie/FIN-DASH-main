# FIN-DASH Phase 4 - Quick Reference Guide

## 🚀 Quick Start

### Starting the Application
```bash
# Option 1: Use start script
python start.py

# Option 2: Manual start
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend
npm run dev
```

### Access URLs
- **Frontend:** http://localhost:8081
- **Backend API:** http://127.0.0.1:8777
- **API Docs:** http://127.0.0.1:8777/docs

---

## 📋 Feature Cheat Sheet

### Card Management

**Create a Card:**
1. Navigate to Cards page
2. Click "Add Card"
3. Fill in details (name, type, account, credit limit)
4. Click "Create Card"

**View Card Analytics:**
1. Find card on Cards page
2. Click "Analytics" button
3. View spending charts and trends

**Edit/Delete Card:**
1. Find card on Cards page
2. Click "Edit" or "Delete" button
3. Confirm action

### Bank Statement Import

**Import Transactions:**
1. Go to Dashboard or Transactions page
2. Click "Import Statement"
3. Select account
4. Upload file (CSV, Excel, PDF, OFX, QFX)
5. Review preview
6. Select transactions to import
7. Click "Import X Transaction(s)"
8. View results

**Supported File Formats:**
- CSV (.csv)
- Excel (.xls, .xlsx)
- PDF (.pdf)
- OFX/QFX (.ofx, .qfx)

---

## 🔧 API Quick Reference

### Card Endpoints

```bash
# List all cards
GET /api/cards

# Get card details
GET /api/cards/{id}

# Create card
POST /api/cards
{
  "name": "My Credit Card",
  "card_type": "credit",
  "account_id": "acc_main",
  "credit_limit": 30000,
  "expiry_month": 12,
  "expiry_year": 2027,
  "is_active": true,
  "color": "#dc2626",
  "icon": "CreditCard"
}

# Update card
PUT /api/cards/{id}
{
  "name": "Updated Name",
  "is_active": false
}

# Delete card
DELETE /api/cards/{id}

# Get card balance
GET /api/cards/{id}/balance

# Get card transactions
GET /api/cards/{id}/transactions

# Get card analytics
GET /api/cards/{id}/analytics?months=6
```

### Import Endpoints

```bash
# Upload and parse file
POST /api/import/upload
Form Data:
- file: <file>
- account_id: "acc_main"
- auto_categorize: true

# Get import preview
GET /api/import/preview/{import_id}

# Confirm import
POST /api/import/confirm/{import_id}
{
  "skip_duplicates": true,
  "selected_transaction_indices": [0, 1, 2, 3]
}

# Get import history
GET /api/import/history?limit=50

# Get supported formats
GET /api/import/formats
```

---

## 📊 Data Structures

### Card Model
```json
{
  "id": "card_20251008143000_a1b2",
  "name": "FNB Gold Credit Card",
  "card_type": "credit",
  "account_id": "acc_creditcard",
  "last_four": "1234",
  "credit_limit": 30000.0,
  "expiry_month": 12,
  "expiry_year": 2027,
  "is_active": true,
  "color": "#dc2626",
  "icon": "CreditCard",
  "created_at": "2025-10-08T14:30:00",
  "updated_at": "2025-10-08T14:30:00"
}
```

### Card Balance
```json
{
  "card_id": "card_20251008143000_a1b2",
  "current_balance": 5000.0,
  "available_balance": 25000.0,
  "credit_limit": 30000.0,
  "credit_utilization": 16.67,
  "transaction_count": 15
}
```

### Import Preview
```json
{
  "import_id": "import_20251008143000_x9y8",
  "file_name": "statement.csv",
  "file_type": "csv",
  "account_id": "acc_main",
  "total_transactions": 10,
  "new_transactions": 8,
  "duplicate_transactions": 2,
  "transactions": [...],
  "created_at": "2025-10-08T14:30:00",
  "status": "pending"
}
```

---

## 🗂️ File Locations

### Backend
```
backend/
├── models/
│   └── card.py                    # Card data model
├── services/
│   ├── card_service.py            # Card business logic
│   ├── statement_parser.py        # File parsing
│   └── import_service.py          # Import logic
├── routers/
│   ├── cards.py                   # Card API endpoints
│   └── import_router.py           # Import API endpoints
└── scripts/
    └── seed_real_data.py          # Data seeding script
```

### Frontend
```
src/
├── components/
│   ├── CardList.tsx               # Card grid display
│   ├── CardCreateDialog.tsx       # Create card form
│   ├── CardEditDialog.tsx         # Edit card form
│   ├── CardAnalyticsDialog.tsx    # Card analytics
│   ├── FileUploadZone.tsx         # File upload UI
│   ├── ImportPreview.tsx          # Import preview table
│   ├── ImportProgress.tsx         # Import progress
│   └── StatementImportDialog.tsx  # Import wizard
└── pages/
    └── Cards.tsx                  # Cards page
```

### Data
```
data/
├── cards.csv                      # Card data
├── import_history.csv             # Import history
├── accounts.csv                   # Account data
├── transactions.csv               # Transaction data
└── ...
```

---

## 🎨 Card Types & Colors

### Card Types
- `credit` - Credit Card
- `debit` - Debit Card
- `prepaid` - Prepaid Card
- `virtual` - Virtual Card

### Suggested Colors
- Red: `#dc2626` (Credit cards)
- Blue: `#2563eb` (Debit cards)
- Green: `#16a34a` (Prepaid cards)
- Purple: `#9333ea` (Virtual cards)

### Available Icons
- `CreditCard`
- `Wallet`
- `DollarSign`
- `Landmark`
- `Briefcase`

---

## 🔍 Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Kill process on port 8777
# Windows:
netstat -ano | findstr :8777
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8777 | xargs kill -9
```

**Module not found:**
```bash
pip install -r backend/requirements.txt
```

**DATA_DIR error:**
```bash
# Check backend/.env
DATA_DIR=data  # Not ../data
```

### Frontend Issues

**Build fails:**
```bash
# Clear cache and rebuild
rm -rf node_modules
npm install
npm run build
```

**Port already in use:**
```bash
# Vite will automatically use next available port
# Default: 8080, fallback: 8081
```

### Import Issues

**File not parsing:**
- Check file format (CSV, Excel, PDF, OFX, QFX)
- Ensure CSV has headers
- Check file size (max 10MB)

**Duplicates not detected:**
- Verify transaction dates match
- Check description similarity
- Ensure amounts are exact

**Wrong categories:**
- Disable auto-categorization
- Manually assign categories
- Build up historical data for better matching

---

## 📈 Performance Tips

### Card Management
- Limit analytics to 6-12 months for faster loading
- Archive old cards (mark as inactive)
- Regularly clean up old transactions

### Statement Import
- Import smaller files (< 1000 transactions)
- Use CSV format for fastest parsing
- Enable skip duplicates to reduce processing

### General
- Keep CSV files under 10,000 rows
- Regularly backup data folder
- Clear browser cache if UI is slow

---

## 🔐 Security Notes

### Card Data
- Only last 4 digits stored
- No CVV or full card number
- All data stored locally

### File Upload
- Files processed locally
- No external transmission
- Temporary files deleted after processing

### Data Privacy
- Single-user application
- No authentication required
- No external API calls
- All data stays on your machine

---

## 📚 Documentation Links

- **User Guide:** `docs/PHASE4_USER_GUIDE.md`
- **Technical Docs:** `docs/PHASE4_TECHNICAL_DOCUMENTATION.md`
- **Status Report:** `docs/PHASE4_STATUS.md`
- **Implementation Plan:** `docs/PHASE4_IMPLEMENTATION_PLAN.md`
- **Technical Specs:** `docs/PHASE4_TECHNICAL_SPECIFICATIONS.md`

---

## 🆘 Common Commands

```bash
# Start application
python start.py

# Run backend only
python backend/app.py

# Run frontend only
npm run dev

# Build frontend
npm run build

# Seed data
python backend/scripts/seed_real_data.py --verbose

# Install dependencies
pip install -r backend/requirements.txt
npm install

# Run tests
python test_card_api.py

# Check backend status
curl http://127.0.0.1:8777/api/summary
```

---

**Last Updated:** October 8, 2025  
**Version:** Phase 4.0

