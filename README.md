# 💰 FIN-DASH - Personal Finance Dashboard

![CI/CD Pipeline](https://github.com/beerberidie/FIN-DASH-main/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11-blue)
![Node.js](https://img.shields.io/badge/Node.js-18-green)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Version:** 2.0.0
**Status:** Production Ready
**Phase:** 3 - Advanced Automation & Analytics

A comprehensive personal finance management application designed for South African users, featuring intelligent automation, budget tracking, debt management, and recurring transactions.

---

## 🎮 Try the Demo

**Experience FIN-DASH with realistic sample data - no setup required!**

FIN-DASH includes a built-in **Demo Mode** that lets you explore all features with 6 months of realistic South African financial data:

- ✅ **600+ sample transactions** from local merchants (Woolworths, Pick n Pay, Takealot, etc.)
- ✅ **4 accounts** (FNB Checking, Capitec Savings, Standard Bank Credit Card, Nedbank Investment)
- ✅ **16 categories** organized by needs/wants/savings
- ✅ **6 monthly budgets** following the 50/30/20 rule
- ✅ **5 investments** (South African stocks and ETFs)
- ✅ **6 recurring transactions** (salary, rent, utilities, subscriptions)

### How to Use Demo Mode

1. **Start the application** (see Quick Start below)
2. **Toggle Demo Mode** using the switch in the top navigation bar
3. **Explore all features** with realistic data
4. **Reset demo data** anytime using the "Reset Demo" button in the banner
5. **Switch back** to your real data by toggling Demo Mode off

Demo mode is perfect for:
- 🎯 **Recruiters** - See the full capabilities without setting up data
- 📚 **Learning** - Understand how to use the app before adding your own data
- 🧪 **Testing** - Try out features risk-free with sample data

---

## 🚀 Quick Start

### Automated Startup (Recommended)

**Windows:**
```batch
start.bat
```
Double-click `start.bat` or run from Command Prompt.

**Linux/Mac:**
```bash
chmod +x start.sh  # First time only
./start.sh
```

**Cross-Platform (Python):**
```bash
python start.py
```

### Access the Application

Once started, open your browser to:
- **Frontend:** http://localhost:5173
- **Backend API:** http://127.0.0.1:8777
- **API Docs:** http://127.0.0.1:8777/docs

📖 **For detailed startup instructions, see [STARTUP_GUIDE.md](STARTUP_GUIDE.md)**

---

## ✨ Features

### Phase 1 - Core Functionality ✅
- ✅ Transaction Management (CRUD operations)
- ✅ Category Management (Needs/Wants/Savings/Debt)
- ✅ Account Management (Multiple accounts)
- ✅ Dashboard Summary (Real-time overview)
- ✅ Budget Tracking (50/30/20 rule)
- ✅ Goal Management (Savings goals with progress)

### Phase 2 - Advanced Features ✅
- ✅ CSV Import with Auto-Categorization (92% accuracy)
- ✅ Debt Management (Avalanche & Snowball calculators)
- ✅ Monthly Financial Reports (Automated insights)

### Phase 3 - Automation & Analytics 🚧
- ✅ **Recurring Transactions** (Automated generation)
- ✅ **Demo Mode** (Realistic sample data for testing and exploration)
- ⏳ Multi-Currency Support
- ⏳ Investment Tracking
- ⏳ Data Export (PDF/Excel)
- ⏳ Enhanced Reporting

---

## 🎯 Key Highlights

- **🎮 Demo Mode:** Try it instantly with 6 months of realistic South African financial data
- **🇿🇦 South African Focus:** ZAR currency, local bank support (FNB, Capitec, Standard Bank, Nedbank, Absa)
- **🤖 Intelligent Automation:** 92% auto-categorization, recurring transactions, automated scheduler
- **📊 Comprehensive Reporting:** Monthly insights, budget performance, debt payoff plans
- **💾 Local-First:** CSV-based storage, no database required, offline-capable
- **🎨 Modern UI:** React + TypeScript + Tailwind CSS + shadcn/ui
- **⚡ Fast API:** FastAPI backend with automatic documentation

---

## 📊 Statistics

- **52 API Endpoints** (23 Phase 1 + 21 Phase 2 + 8 Phase 3)
- **15 UI Components** (5 Phase 1 + 8 Phase 2 + 2 Phase 3)
- **11 Backend Services** (Calculator, CSV Manager, Budget, Goal, Debt, Report, Recurring, Scheduler, etc.)
- **6 Frequency Types** for recurring transactions (daily, weekly, biweekly, monthly, quarterly, yearly)
- **100% Test Coverage** for all major features

---

## 🛠️ Technology Stack

**Backend:**
- FastAPI 0.104.1
- Uvicorn 0.24.0
- Pydantic 2.5.0
- python-dateutil 2.8.2
- APScheduler 3.10.4

**Frontend:**
- React 18.3.1
- TypeScript
- Vite
- TanStack React Query
- shadcn/ui
- Tailwind CSS
- Lucide Icons

**Storage:**
- CSV-based local storage
- No database required

---

## 📋 Prerequisites

- **Python 3.8+** - [Download](https://www.python.org/)
- **Node.js 16+** - [Download](https://nodejs.org/)

---

## Project info

**URL**: https://lovable.dev/projects/50ad44fb-0d15-4873-9632-292aa660ed46

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/50ad44fb-0d15-4873-9632-292aa660ed46) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

Requirements: Python 3.8+ and Node.js 16+ - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Start the application using the startup script
# Windows:
start.bat

# Linux/Mac:
chmod +x start.sh
./start.sh

# Or use Python script (cross-platform):
python start.py
```

**Manual Setup (if needed):**

```sh
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
pip install -r requirements.txt
python app.py

# Frontend setup (in a new terminal)
npm install
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/50ad44fb-0d15-4873-9632-292aa660ed46) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/features/custom-domain#custom-domain)
