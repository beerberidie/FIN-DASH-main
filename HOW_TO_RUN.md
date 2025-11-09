# 🚀 How to Run FIN-DASH Application

**Complete Guide to Starting and Using FIN-DASH**

---

## 📋 Prerequisites

Before running FIN-DASH, ensure you have:

- ✅ **Python 3.11+** installed ([Download](https://www.python.org/))
- ✅ **Node.js 18+** installed ([Download](https://nodejs.org/))
- ✅ **npm** (comes with Node.js)

### Verify Installation

```bash
# Check Python version
python --version
# Should show: Python 3.11.x or higher

# Check Node.js version
node --version
# Should show: v18.x.x or higher

# Check npm version
npm --version
# Should show: 9.x.x or higher
```

---

## 🎯 Method 1: Automated Startup (RECOMMENDED)

The easiest way to start FIN-DASH is using the automated startup scripts.

### **Windows:**

**Option A: Double-click the file**
1. Navigate to the FIN-DASH project folder
2. Double-click `start.bat`
3. Wait for both servers to start (2 new windows will open)

**Option B: Command Prompt**
```batch
start.bat
```

### **Linux/Mac:**

```bash
# Make executable (first time only)
chmod +x start.sh

# Run the script
./start.sh
```

### **Cross-Platform (Python):**

```bash
python start.py
```

### **What the Automated Script Does:**

1. ✅ Checks if Python and Node.js are installed
2. ✅ Creates Python virtual environment (if needed)
3. ✅ Installs backend dependencies
4. ✅ Installs frontend dependencies
5. ✅ Starts backend server (http://127.0.0.1:8777)
6. ✅ Starts frontend server (http://localhost:5173)
7. ✅ Opens 2 separate terminal windows for each server

---

## 🔧 Method 2: Manual Startup (Step-by-Step)

If you prefer manual control or need to troubleshoot, follow these steps:

### **Step 1: Start the Backend Server**

Open a **new terminal/command prompt** and run:

**Windows:**
```batch
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**Linux/Mac:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['C:\...\FIN-DASH-main']
INFO:     Uvicorn running on http://127.0.0.1:8777 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXX] using WatchFiles
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Backend is now running at:** http://127.0.0.1:8777

### **Step 2: Start the Frontend Server**

Open a **second terminal/command prompt** (keep the backend running) and run:

```bash
# From the project root directory
npm install
npm run dev
```

**Expected Output:**
```
  VITE v5.4.19  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

✅ **Frontend is now running at:** http://localhost:5173

---

## 🌐 Accessing the Application

Once both servers are running:

### **Main Application:**
- **URL:** http://localhost:5173
- **Description:** The FIN-DASH web interface

### **Backend API:**
- **URL:** http://127.0.0.1:8777
- **Description:** FastAPI backend server

### **API Documentation (Swagger UI):**
- **URL:** http://127.0.0.1:8777/docs
- **Description:** Interactive API documentation with all 98 endpoints

### **Alternative API Documentation (ReDoc):**
- **URL:** http://127.0.0.1:8777/redoc
- **Description:** Alternative API documentation format

---

## 🛑 Stopping the Application

### **If using Automated Startup:**
- Close the two terminal windows that were opened
- Or press `Ctrl+C` in each window

### **If using Manual Startup:**
- Press `Ctrl+C` in the backend terminal
- Press `Ctrl+C` in the frontend terminal

---

## 🔍 Troubleshooting

### **Problem: "Port already in use" error**

**Backend (Port 8777):**
```bash
# Windows
netstat -ano | findstr :8777
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8777 | xargs kill -9
```

**Frontend (Port 5173):**
```bash
# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5173 | xargs kill -9
```

### **Problem: Backend dependencies not installing**

```bash
cd backend
# Delete existing venv
rm -rf venv  # Linux/Mac
rmdir /s venv  # Windows

# Recreate venv
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### **Problem: Frontend dependencies not installing**

```bash
# Delete node_modules and lockfile
rm -rf node_modules package-lock.json  # Linux/Mac
rmdir /s node_modules  # Windows
del package-lock.json  # Windows

# Reinstall
npm install
```

### **Problem: CORS errors in browser console**

This should not happen with the current configuration, but if it does:
- Ensure backend is running on http://127.0.0.1:8777
- Ensure frontend is running on http://localhost:5173
- Check `backend/app.py` has CORS middleware configured

### **Problem: "Module not found" errors**

**Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

**Frontend:**
```bash
npm install
```

---

## 📊 What You Should See

### **Dashboard (Home Page):**
- Total Balance
- Monthly Income
- Monthly Expenses
- Monthly Surplus
- Savings Rate
- Net Worth
- Recent Transactions
- Budget Overview
- Financial Goals

### **Available Features:**

**Phase 1 (Complete):**
- ✅ Transactions Management
- ✅ Categories Management
- ✅ Accounts Management
- ✅ Budgets Tracking
- ✅ Goals Management

**Phase 2 (Complete):**
- ✅ CSV Import with Auto-Categorization
- ✅ Debt Management
- ✅ Monthly Reports

**Phase 3 (Backend Complete):**
- ✅ Recurring Transactions (Full Stack)
- ✅ Multi-Currency Support (Backend)
- ✅ Investment Tracking (Backend)
- ✅ Data Export (Backend)
- ✅ Enhanced Analytics (Backend)

---

## 🎯 Quick Test

Once the application is running, test it:

1. **Open:** http://localhost:5173
2. **Check Dashboard:** Should show sample data
3. **Navigate to Transactions:** Click "Transactions" in sidebar
4. **Check API:** Open http://127.0.0.1:8777/docs
5. **Test Endpoint:** Try GET /api/summary in Swagger UI

---

## 📝 Development Mode

Both servers run in **development mode** with:
- ✅ **Hot Reload:** Changes to code automatically reload the server
- ✅ **Detailed Logging:** See all requests and errors
- ✅ **Source Maps:** Easy debugging

### **Backend Development:**
- Edit files in `backend/` folder
- Server auto-reloads on file changes
- Check terminal for logs

### **Frontend Development:**
- Edit files in `src/` folder
- Browser auto-refreshes on file changes
- Check browser console for logs

---

## 🚀 Production Deployment

For production deployment, see:
- `DEPLOYMENT_SUCCESS.md` - Production deployment guide
- `STARTUP_GUIDE.md` - Detailed startup instructions

---

## 📞 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Review `STARTUP_GUIDE.md` for detailed instructions
3. Check `PHASE3_STATUS.md` for current feature status
4. Review API documentation at http://127.0.0.1:8777/docs

---

## ✨ Summary

**Quickest Way to Start:**
```bash
# Windows
start.bat

# Linux/Mac
./start.sh

# Cross-platform
python start.py
```

**Then open:** http://localhost:5173

**That's it!** 🎉

---

*Last Updated: October 6, 2025*
*FIN-DASH Version: 2.0.0*

