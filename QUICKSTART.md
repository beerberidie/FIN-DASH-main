# FIN-DASH Quick Start Guide

Get FIN-DASH running in 5 minutes!

## Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

## Step 1: Start the Backend (Terminal 1)

### Windows:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn python-dotenv pydantic
python app.py
```

### Linux/Mac:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn python-dotenv pydantic
python app.py
```

✓ Backend should be running at **http://localhost:8777**

## Step 2: Start the Frontend (Terminal 2)

```bash
npm install
npm run dev
```

✓ Frontend should be running at **http://localhost:8080**

## Step 3: Open the Dashboard

Open your browser and go to: **http://localhost:8080**

You should see:
- Total Balance: R 5,000.00
- Savings Rate: 50.00%
- Monthly Surplus: R 9,000.00
- Net Worth: R 5,000.00
- 5 sample transactions
- 3 savings goals

## Step 4: Test the API

In a new terminal:

```bash
cd backend
python test_api.py
```

All tests should pass ✓

## Troubleshooting

**Backend won't start?**
- Make sure Python 3.11+ is installed: `python --version`
- Check if port 8777 is available
- Try installing dependencies again: `pip install -r requirements.txt`

**Frontend won't start?**
- Make sure Node.js 18+ is installed: `node --version`
- Delete `node_modules` and run `npm install` again
- Check if port 8080 is available

**Dashboard shows errors?**
- Make sure the backend is running on http://localhost:8777
- Check browser console (F12) for error messages
- Verify `.env` file has `VITE_API_BASE=http://localhost:8777/api`

## What's Next?

- Read [SETUP.md](SETUP.md) for detailed setup instructions
- Read [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md) for implementation details
- Try creating a transaction via API docs: http://localhost:8777/docs
- Edit CSV files in `data/` directory to add your own data

## Quick Commands

**Backend:**
```bash
cd backend
python app.py                    # Start server
python test_api.py               # Run tests
```

**Frontend:**
```bash
npm run dev                      # Start dev server
npm run build                    # Build for production
npm run preview                  # Preview production build
```

**API Documentation:**
- Interactive docs: http://localhost:8777/docs
- Alternative docs: http://localhost:8777/redoc

## Sample Data Included

The application comes with sample data to get you started:

**Transactions (5):**
- Monthly Salary: +R 18,000
- Pick n Pay (Groceries): -R 842.50
- Ocean Basket (Dining): -R 385.00
- Rent Payment: -R 4,500.00
- Shell Fuel (Transport): -R 650.00

**Goals (3):**
- Emergency Fund: R 8,500 / R 15,000 (57%)
- Car Deposit: R 12,000 / R 30,000 (40%)
- Holiday Fund: R 3,200 / R 10,000 (32%)

**Categories (14):**
- Needs: Rent, Groceries, Transport, Utilities, Data/Airtime
- Wants: Eating Out, Entertainment, Subscriptions
- Savings: Emergency Fund, Goals
- Debt: Credit Card, Personal Loan
- Income: Salary, Freelance

---

**Need help?** Check [SETUP.md](SETUP.md) for detailed troubleshooting.

