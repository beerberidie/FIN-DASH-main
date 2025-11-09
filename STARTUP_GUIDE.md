# 🚀 FIN-DASH Startup Guide

This guide explains how to start the FIN-DASH application using the provided startup scripts.

---

## 📋 Prerequisites

Before starting the application, ensure you have:

1. **Python 3.8+** installed
   - Download from: https://www.python.org/
   - Verify: `python --version` or `python3 --version`

2. **Node.js 16+** installed
   - Download from: https://nodejs.org/
   - Verify: `node --version`

3. **Git** (optional, for cloning the repository)
   - Download from: https://git-scm.com/

---

## 🎯 Quick Start

### Windows

**Option 1: Using Batch Script (Recommended)**
```batch
start.bat
```
- Double-click `start.bat` in File Explorer, OR
- Run from Command Prompt: `start.bat`

**Option 2: Using Python Script**
```batch
python start.py
```

### Linux / Mac

**Option 1: Using Shell Script (Recommended)**
```bash
chmod +x start.sh  # Make executable (first time only)
./start.sh
```

**Option 2: Using Python Script**
```bash
python3 start.py
```

---

## 📖 Detailed Instructions

### Windows Users

#### Method 1: Batch Script (Easiest)

1. Navigate to the FIN-DASH project folder
2. Double-click `start.bat`
3. Two new command windows will open:
   - **FIN-DASH Backend** - API server
   - **FIN-DASH Frontend** - Web interface
4. Wait a few seconds for servers to start
5. Open your browser to: http://localhost:5173

**To Stop:**
- Close both command windows, OR
- Press Ctrl+C in each window

#### Method 2: Python Script

1. Open Command Prompt or PowerShell
2. Navigate to project folder: `cd path\to\FIN-DASH-main`
3. Run: `python start.py`
4. Press Ctrl+C to stop

### Linux / Mac Users

#### Method 1: Shell Script (Easiest)

1. Open Terminal
2. Navigate to project folder: `cd path/to/FIN-DASH-main`
3. Make script executable (first time only):
   ```bash
   chmod +x start.sh
   ```
4. Run the script:
   ```bash
   ./start.sh
   ```
5. Open your browser to: http://localhost:5173

**To Stop:**
- Press Ctrl+C in the terminal

#### Method 2: Python Script

1. Open Terminal
2. Navigate to project folder: `cd path/to/FIN-DASH-main`
3. Run: `python3 start.py`
4. Press Ctrl+C to stop

---

## 🔧 Advanced Usage

### Python Script Options

The `start.py` script supports additional options:

```bash
# Start both backend and frontend (default)
python start.py

# Start backend only
python start.py --backend

# Start frontend only
python start.py --frontend

# Show help
python start.py --help
```

### Manual Startup

If you prefer to start servers manually:

**Backend:**
```bash
cd backend
python -m venv venv                    # Create virtual environment (first time)
source venv/bin/activate               # Linux/Mac
# OR
venv\Scripts\activate.bat              # Windows

pip install -r requirements.txt        # Install dependencies (first time)
python app.py                          # Start backend
```

**Frontend:**
```bash
npm install                            # Install dependencies (first time)
npm run dev                            # Start frontend
```

---

## 🌐 Access Points

Once the application is running, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Main web interface |
| **Backend API** | http://127.0.0.1:8777 | REST API server |
| **API Docs** | http://127.0.0.1:8777/docs | Interactive API documentation |

---

## 🐛 Troubleshooting

### "Python is not installed or not in PATH"

**Solution:**
1. Install Python from https://www.python.org/
2. During installation, check "Add Python to PATH"
3. Restart your terminal/command prompt

### "Node.js is not installed or not in PATH"

**Solution:**
1. Install Node.js from https://nodejs.org/
2. Restart your terminal/command prompt
3. Verify with: `node --version`

### "Failed to install backend dependencies"

**Solution:**
1. Delete the `backend/venv` folder
2. Run the startup script again
3. If still failing, manually install:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate.bat on Windows
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### "Failed to install frontend dependencies"

**Solution:**
1. Delete the `node_modules` folder
2. Delete `package-lock.json`
3. Run: `npm install`
4. If still failing, try: `npm cache clean --force` then `npm install`

### "Port already in use"

**Backend (Port 8777):**
- Another instance of the backend is running
- Kill the process using port 8777
- Windows: `netstat -ano | findstr :8777` then `taskkill /PID <PID> /F`
- Linux/Mac: `lsof -ti:8777 | xargs kill -9`

**Frontend (Port 5173):**
- Another instance of the frontend is running
- Kill the process using port 5173
- Windows: `netstat -ano | findstr :5173` then `taskkill /PID <PID> /F`
- Linux/Mac: `lsof -ti:5173 | xargs kill -9`

### Backend starts but frontend doesn't

**Solution:**
1. Check if Node.js is installed: `node --version`
2. Check if npm is installed: `npm --version`
3. Try installing dependencies manually: `npm install`
4. Check for errors in the terminal output

### Frontend starts but backend doesn't

**Solution:**
1. Check if Python is installed: `python --version`
2. Check if virtual environment exists: `backend/venv`
3. Try installing dependencies manually:
   ```bash
   cd backend
   source venv/bin/activate  # or venv\Scripts\activate.bat
   pip install -r requirements.txt
   ```
4. Check for errors in the terminal output

---

## 📝 What the Startup Scripts Do

1. **Check Prerequisites**
   - Verify Python and Node.js are installed
   - Check version compatibility

2. **Setup Backend**
   - Create Python virtual environment (if needed)
   - Install Python dependencies from `requirements.txt`

3. **Setup Frontend**
   - Install Node.js dependencies from `package.json`

4. **Start Servers**
   - Launch FastAPI backend on port 8777
   - Launch Vite frontend on port 5173
   - Monitor processes for errors

5. **Cleanup on Exit**
   - Gracefully stop both servers when you press Ctrl+C

---

## 🎯 First Time Setup

The first time you run the startup script, it will:

1. Create a Python virtual environment (~50 MB)
2. Install Python packages (~200 MB)
3. Install Node.js packages (~300 MB)
4. **Total time:** 2-5 minutes depending on internet speed

**Subsequent startups will be much faster (5-10 seconds)!**

---

## 💡 Tips

1. **Keep the terminal/command window open** while using the application
2. **Don't close the browser tab** - you can minimize it
3. **Use Ctrl+C to stop** - don't just close the window
4. **Check the logs** if something goes wrong:
   - Backend logs appear in the terminal
   - Frontend logs appear in the browser console (F12)

---

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review the terminal output for error messages
3. Check the browser console (F12) for frontend errors
4. Ensure all prerequisites are installed correctly
5. Try deleting `backend/venv` and `node_modules` and running again

---

## 📚 Additional Resources

- **Python Documentation:** https://docs.python.org/
- **Node.js Documentation:** https://nodejs.org/docs/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **React Documentation:** https://react.dev/
- **Vite Documentation:** https://vitejs.dev/

---

**Happy Finance Tracking! 💰**

*FIN-DASH - Your Personal Finance Dashboard*

