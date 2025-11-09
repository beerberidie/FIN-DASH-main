# FIN-DASH Setup Guide - Phase 1 (MVP)

## Overview
FIN-DASH is a personal finance dashboard with a CSV-based backend and React frontend. This guide will help you set up and run the application locally.

## Prerequisites

### Required Software
- **Python 3.11+** - For the backend API
- **Node.js 18+** - For the frontend
- **npm** or **yarn** - Package manager

### Check Installations
```bash
python --version  # Should be 3.11 or higher
node --version    # Should be 18 or higher
npm --version
```

## Quick Start

### 1. Backend Setup

#### On Windows:
```bash
cd backend
start.bat
```

#### On Linux/Mac:
```bash
cd backend
chmod +x start.sh
./start.sh
```

#### Manual Setup (if scripts don't work):
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py
```

The backend will start on **http://localhost:8777**

### 2. Frontend Setup

In a new terminal:

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will start on **http://localhost:8080**

## Verify Installation

### 1. Check Backend
Open your browser and navigate to:
- **API Docs**: http://localhost:8777/docs
- **Health Check**: http://localhost:8777/health

You should see the FastAPI interactive documentation.

### 2. Check Frontend
Open your browser and navigate to:
- **Dashboard**: http://localhost:8080

You should see the Financial Command Dashboard with:
- Overview cards showing balance, savings rate, surplus, and net worth
- Recent transactions table
- Savings goals panel
- Budget overview (mock data for now)

### 3. Test API Integration
The dashboard should display real data from the CSV files in the `data/` directory:
- 5 sample transactions
- 3 savings goals
- Calculated summary metrics

## Project Structure

```
FIN-DASH-main/
├── backend/                 # FastAPI backend
│   ├── app.py              # Main application
│   ├── config.py           # Configuration
│   ├── models/             # Pydantic models
│   ├── routers/            # API endpoints
│   ├── services/           # Business logic
│   ├── utils/              # Utilities
│   └── requirements.txt    # Python dependencies
├── data/                    # CSV data files
│   ├── transactions.csv
│   ├── categories.csv
│   ├── accounts.csv
│   ├── goals.csv
│   ├── budgets.csv
│   ├── debts.csv
│   └── settings.json
├── src/                     # React frontend
│   ├── components/         # UI components
│   ├── services/           # API client
│   ├── lib/                # Utilities
│   └── pages/              # Page components
└── package.json            # Node dependencies
```

## Data Files

The application uses CSV files for data storage located in the `data/` directory:

- **transactions.csv** - All financial transactions
- **categories.csv** - Transaction categories (needs/wants/savings/debt/income)
- **accounts.csv** - Bank accounts
- **goals.csv** - Savings goals
- **budgets.csv** - Monthly budgets (empty for now, Phase 2)
- **debts.csv** - Debts/liabilities (empty for now, Phase 2)
- **settings.json** - Application settings

### Sample Data
The application comes with sample data:
- 5 sample transactions (salary, groceries, dining, rent, transport)
- 14 default categories
- 1 main checking account
- 3 savings goals (Emergency Fund, Car Deposit, Holiday Fund)

## API Endpoints

### Summary
- `GET /api/summary` - Dashboard overview with all metrics

### Transactions
- `GET /api/transactions` - List all transactions (with filters)
- `POST /api/transactions` - Create new transaction
- `PUT /api/transactions/{id}` - Update transaction
- `DELETE /api/transactions/{id}` - Delete transaction

### Categories
- `GET /api/categories` - List all categories
- `POST /api/categories` - Create custom category

### Accounts
- `GET /api/accounts` - List all accounts
- `GET /api/accounts/{id}/balance` - Get account balance

## Troubleshooting

### Backend Issues

**Port 8777 already in use:**
```bash
# Change the port in backend/.env
APP_PORT=8778
```

**Module not found errors:**
```bash
# Make sure you're in the virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**File locking errors (Windows):**
- The CSV manager uses `fcntl` which is Unix-only
- On Windows, file locking is handled differently
- If you encounter errors, the app will still work but without file locking

### Frontend Issues

**Port 8080 already in use:**
```bash
# Vite will automatically try the next available port
# Or specify a different port in vite.config.ts
```

**API connection errors:**
- Make sure the backend is running on http://localhost:8777
- Check the `.env` file has `VITE_API_BASE=http://localhost:8777/api`
- Check browser console for CORS errors

**Data not loading:**
- Open browser DevTools (F12)
- Check the Network tab for failed API calls
- Verify the backend is running and accessible

## Development Workflow

### Adding Transactions
Currently, you can add transactions via:
1. **API Docs** - http://localhost:8777/docs
   - Navigate to POST /api/transactions
   - Click "Try it out"
   - Fill in the transaction data
   - Execute

2. **Direct CSV Edit** - Edit `data/transactions.csv`
   - Add a new row with proper format
   - Refresh the frontend to see changes

### Modifying Data
- **Transactions**: Edit `data/transactions.csv`
- **Categories**: Edit `data/categories.csv`
- **Goals**: Edit `data/goals.csv`
- **Settings**: Edit `data/settings.json`

After editing CSV files, the changes will be reflected immediately (no server restart needed).

## Next Steps (Phase 2)

Phase 1 (MVP) is now complete! The following features will be added in Phase 2:
- Budget management with planned vs actual tracking
- CSV import functionality for bank statements
- Auto-categorization of transactions
- Debt tracking and payoff plans
- Transaction filtering and search
- Manual transaction creation via UI

## Support

If you encounter issues:
1. Check this guide's Troubleshooting section
2. Verify all prerequisites are installed
3. Check that both backend and frontend are running
4. Look for error messages in terminal/console

## Phase 1 Success Criteria ✓

- [x] Backend API running on localhost:8777
- [x] Frontend running on localhost:8080
- [x] Dashboard displays real data from CSV files
- [x] Transactions table shows sample data
- [x] Goals panel shows progress
- [x] Summary metrics calculated correctly
- [x] API responses < 200ms
- [x] Loading states visible
- [x] Error handling implemented
- [x] Currency formatted as ZAR (R symbol)

