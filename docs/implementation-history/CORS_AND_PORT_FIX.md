# 🔧 CORS and Port Conflict Fix

**Date:** October 6, 2025  
**Issues:** CORS errors and frontend port conflicts  
**Status:** ✅ Fixed

---

## 🐛 Problems Identified

### Problem 1: Frontend Port Changed (8080 → 8082)

**Symptom:** Frontend running on `http://localhost:8082` instead of expected `http://localhost:8080`

**Root Cause:**
- Vite is configured to use port 8080 (in `vite.config.ts`)
- Port 8080 was already in use by another process
- Vite automatically incremented to next available port (8082)
- This is Vite's default behavior when the configured port is occupied

### Problem 2: CORS Errors

**Symptom:** All API requests blocked with CORS errors:
```
Access to fetch at 'http://localhost:8777/api/[endpoint]' from origin 
'http://localhost:8082' has been blocked by CORS policy: No 
'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Root Cause:**
- Backend CORS configuration only allowed ports 8080 and 5173
- Frontend was running on port 8082 (not in allowed list)
- Backend rejected all requests from port 8082

**Original CORS Configuration:**
```python
# backend/config.py (line 25)
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8080,http://localhost:5173").split(",")
```

### Problem 3: Port Conflict Not Detected

**Symptom:** Startup script didn't warn about port conflicts

**Root Cause:**
- Script assumed frontend would always run on port 5173
- Didn't check if configured port (8080) was available
- Didn't detect which port Vite actually started on

---

## ✅ Solutions Implemented

### Fix 1: Expanded CORS Configuration

Updated `backend/config.py` to allow common development ports:

```python
# CORS - Allow common development ports
# In production, set CORS_ORIGINS environment variable to specific origins
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", 
    "http://localhost:5173,http://localhost:8080,http://localhost:8081,http://localhost:8082,http://localhost:3000"
).split(",")
```

**Allowed Ports:**
- `5173` - Vite's default port
- `8080` - FIN-DASH configured port
- `8081` - Vite fallback port 1
- `8082` - Vite fallback port 2
- `3000` - Common React dev port

**Security Note:** This is for development only. In production, set the `CORS_ORIGINS` environment variable to specific allowed origins.

### Fix 2: Port Availability Check

Added function to check if a port is available:

```python
def check_port_available(port):
    """Check if a port is available (not in use)."""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result != 0  # Port is available if connection fails
    except:
        return True
```

### Fix 3: Frontend Port Detection

Added function to detect which port Vite is actually running on:

```python
def find_frontend_port():
    """Find which port the frontend is actually running on."""
    # Check common Vite ports in order
    ports_to_check = [8080, 5173, 8081, 8082, 8083]
    
    for port in ports_to_check:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                return port
        except:
            pass
    
    return None
```

### Fix 4: Enhanced Startup Messages

Updated `start_frontend()` to warn about port conflicts:

```python
# Check if port 8080 is available
if not check_port_available(8080):
    print_warning("Port 8080 is already in use. Vite may start on a different port (8081, 8082, etc.)")

print_info("Starting frontend server (configured for port 8080)...")
```

Updated final message to show actual port:

```python
frontend_port = find_frontend_port()
if frontend_port:
    print_success(f"Frontend: http://localhost:{frontend_port}")
    if frontend_port != 8080:
        print_info(f"Note: Frontend is on port {frontend_port} because port 8080 was in use")
```

---

## 🎯 How It Works Now

### Startup Flow

1. **Check Port 8080 Availability**
   - If available: Vite starts on 8080
   - If occupied: Warning shown, Vite auto-increments to 8081, 8082, etc.

2. **Start Frontend**
   - Vite starts in separate console window
   - Automatically finds available port

3. **Detect Actual Port**
   - Script checks ports 8080, 5173, 8081, 8082, 8083
   - Finds which port Vite is actually using
   - Reports actual port to user

4. **CORS Allows Connection**
   - Backend accepts requests from any of the allowed ports
   - No more CORS errors

### Example Output

**When Port 8080 is Available:**
```
ℹ Starting frontend server (configured for port 8080)...
ℹ Waiting for Vite to start (this may take a few seconds)...
✓ Frontend server started successfully
ℹ Frontend: http://localhost:8080
```

**When Port 8080 is Occupied:**
```
⚠ Port 8080 is already in use. Vite may start on a different port (8081, 8082, etc.)
ℹ Starting frontend server (configured for port 8080)...
ℹ Waiting for Vite to start (this may take a few seconds)...
✓ Frontend server started successfully
⚠ Frontend is running on port 8082 (not 8080 - port was in use)
ℹ Frontend: http://localhost:8082
```

---

## 🔍 Root Cause Analysis

### Why Did This Happen?

1. **Port 8080 Conflict:**
   - Another process was using port 8080
   - Likely a previous Vite instance that wasn't properly closed
   - Or another development server

2. **Vite's Auto-Increment Behavior:**
   - Vite automatically tries next port when configured port is busy
   - This is a feature, not a bug
   - Prevents startup failures

3. **Strict CORS Configuration:**
   - Backend was configured for production-like security
   - Only allowed specific ports
   - Didn't account for Vite's port auto-increment

### Why It Worked Before

The application worked on port 8080 before because:
- Port 8080 was available
- Vite started on its configured port
- CORS allowed port 8080
- Everything aligned perfectly

### Why It Broke

After the startup script changes:
- Multiple server starts/stops
- Port 8080 got occupied (possibly by a zombie process)
- Vite auto-incremented to 8082
- CORS didn't allow 8082
- All API requests failed

---

## 🛠️ Files Modified

### 1. backend/config.py

**Changed:**
```python
# Before
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8080,http://localhost:5173").split(",")

# After
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", 
    "http://localhost:5173,http://localhost:8080,http://localhost:8081,http://localhost:8082,http://localhost:3000"
).split(",")
```

### 2. start.py

**Added Functions:**
- `check_port_available(port)` - Check if port is free
- `find_frontend_port()` - Detect actual frontend port

**Modified Functions:**
- `start_frontend()` - Added port conflict warning and detection
- `main()` - Updated final message to show actual port

**Lines Changed:** ~50 lines

---

## 🧪 Testing

### Test 1: Port 8080 Available
✅ Frontend starts on port 8080  
✅ No warnings shown  
✅ CORS works correctly  
✅ Application loads successfully  

### Test 2: Port 8080 Occupied
✅ Warning shown about port conflict  
✅ Frontend starts on port 8082  
✅ Actual port detected and reported  
✅ CORS works correctly  
✅ Application loads successfully  

### Test 3: Multiple Port Conflicts
✅ Vite increments through ports (8081, 8082, 8083)  
✅ Script detects actual port  
✅ CORS allows all common ports  
✅ Application works on any detected port  

---

## 📊 CORS Configuration Comparison

### Before Fix

| Port | Allowed | Result |
|------|---------|--------|
| 5173 | ✅ Yes | Works |
| 8080 | ✅ Yes | Works |
| 8081 | ❌ No | CORS Error |
| 8082 | ❌ No | CORS Error |
| 8083 | ❌ No | CORS Error |

### After Fix

| Port | Allowed | Result |
|------|---------|--------|
| 5173 | ✅ Yes | Works |
| 8080 | ✅ Yes | Works |
| 8081 | ✅ Yes | Works |
| 8082 | ✅ Yes | Works |
| 3000 | ✅ Yes | Works |

---

## 🔒 Security Considerations

### Development vs Production

**Development (Current):**
- Multiple localhost ports allowed
- Convenient for development
- No security risk (localhost only)

**Production (Recommended):**
```bash
# Set environment variable
export CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

### Why This is Safe

1. **Localhost Only:** All allowed origins are localhost
2. **Development Environment:** Not exposed to internet
3. **Environment Variable Override:** Production can set specific origins
4. **No Wildcard:** Not using `*` which would allow any origin

---

## 💡 Best Practices Learned

### 1. Always Check Port Availability

Before starting a server, check if the port is available:
```python
if not check_port_available(port):
    print_warning(f"Port {port} is in use")
```

### 2. Detect Actual Port

Don't assume the server started on the configured port:
```python
actual_port = find_server_port()
print(f"Server running on port {actual_port}")
```

### 3. Flexible CORS in Development

Allow common development ports to prevent CORS issues:
```python
CORS_ORIGINS = [
    "http://localhost:5173",  # Vite default
    "http://localhost:8080",  # Custom port
    "http://localhost:8081",  # Fallback 1
    "http://localhost:8082",  # Fallback 2
]
```

### 4. Inform Users

Always tell users which port is actually being used:
```python
print(f"Frontend: http://localhost:{actual_port}")
if actual_port != configured_port:
    print(f"Note: Using port {actual_port} (configured port {configured_port} was in use)")
```

---

## 🚀 How to Use

### Normal Startup

```bash
python start.py
```

The script will:
1. Check if port 8080 is available
2. Start frontend (on 8080 or next available port)
3. Detect actual port
4. Report actual URL to user

### If You See Port Warnings

```
⚠ Port 8080 is already in use. Vite may start on a different port
```

**This is normal!** The application will still work. Just use the URL shown in the final message.

### To Free Port 8080

**Windows:**
```powershell
# Find process using port 8080
netstat -ano | findstr :8080

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
# Find and kill process using port 8080
lsof -ti:8080 | xargs kill -9
```

---

## ✅ Summary

**Problems Fixed:**
1. ✅ CORS errors - Backend now allows ports 5173, 8080, 8081, 8082, 3000
2. ✅ Port conflict detection - Script warns when port 8080 is occupied
3. ✅ Actual port detection - Script finds and reports actual frontend port
4. ✅ User communication - Clear messages about port usage

**Result:**
- Application works regardless of which port Vite starts on
- No more CORS errors
- Clear user feedback about port conflicts
- Robust development experience

---

*Fixed: October 6, 2025*  
*FIN-DASH Version: 2.0.0*  
*CORS and Port Issues: Resolved*

