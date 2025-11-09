# Enhanced Single-User Solution - Implementation Guide

**Solution:** Cloud Backup + VPN Remote Access  
**Estimated Time:** 24 hours (3 days)  
**Estimated Cost:** R12,000 (development) + R30-50/month (cloud storage)  
**Difficulty:** ⭐⭐ (Moderate)

---

## Overview

This guide implements the **recommended alternative** to multi-user transformation:

**Phase 1:** Encrypted Cloud Backup (20 hours)  
**Phase 2:** VPN Remote Access with Tailscale (4 hours) - OPTIONAL

**Benefits:**
- ✅ Disaster recovery
- ✅ Remote access from anywhere
- ✅ Data security (encrypted)
- ✅ Keep single-user simplicity
- ✅ Save R410,000 vs. multi-user
- ✅ Save 576 hours of development

---

## Phase 1: Encrypted Cloud Backup

### 1.1 Choose Cloud Provider

**Recommended: Google Drive**

| Provider | Storage | Price/Month | Pros |
|----------|---------|-------------|------|
| **Google Drive** | 100GB | R30 | Easy API, reliable |
| **Dropbox** | 2TB | R200 | Excellent sync |
| **OneDrive** | 100GB | R40 | Microsoft integration |
| **Backblaze B2** | Pay-as-you-go | ~R20 | Cheapest for backups |

**Recommendation:** Google Drive (100GB for R30/month)

### 1.2 Set Up Google Drive API

**Step 1: Create Google Cloud Project**

1. Go to https://console.cloud.google.com/
2. Create new project: "FIN-DASH Backup"
3. Enable Google Drive API
4. Create OAuth 2.0 credentials
5. Download `credentials.json`

**Step 2: Install Dependencies**

```bash
cd backend
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client cryptography schedule
```

Add to `requirements.txt`:
```
google-auth==2.23.0
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
google-api-python-client==2.100.0
cryptography==41.0.5
schedule==1.2.0
```

### 1.3 Create Backup Service

**File:** `backend/services/backup_service.py`

```python
"""Encrypted cloud backup service for FIN-DASH."""
import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Optional
from cryptography.fernet import Fernet
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import config

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class BackupService:
    """Handles encrypted backups to Google Drive."""
    
    def __init__(self):
        self.backup_dir = config.DATA_DIR / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        self.encryption_key_file = config.DATA_DIR / ".backup_key"
        self.token_file = config.DATA_DIR / ".backup_token.json"
        self.credentials_file = Path("credentials.json")
        
    def get_encryption_key(self) -> bytes:
        """Get or create encryption key."""
        if self.encryption_key_file.exists():
            return self.encryption_key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            self.encryption_key_file.write_bytes(key)
            # Secure the key file (Unix only)
            if os.name != 'nt':
                os.chmod(self.encryption_key_file, 0o600)
            return key
    
    def encrypt_file(self, filepath: Path) -> Path:
        """Encrypt a file."""
        key = self.get_encryption_key()
        fernet = Fernet(key)
        
        data = filepath.read_bytes()
        encrypted_data = fernet.encrypt(data)
        
        encrypted_path = filepath.with_suffix(filepath.suffix + '.encrypted')
        encrypted_path.write_bytes(encrypted_data)
        return encrypted_path
    
    def decrypt_file(self, encrypted_path: Path, output_path: Path):
        """Decrypt a file."""
        key = self.get_encryption_key()
        fernet = Fernet(key)
        
        encrypted_data = encrypted_path.read_bytes()
        decrypted_data = fernet.decrypt(encrypted_data)
        output_path.write_bytes(decrypted_data)
    
    def create_backup(self) -> Path:
        """Create encrypted backup of all data files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"findash_backup_{timestamp}"
        backup_zip = self.backup_dir / f"{backup_name}.zip"
        
        # Create zip of all CSV files
        with zipfile.ZipFile(backup_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for csv_file in config.DATA_DIR.glob("*.csv"):
                zipf.write(csv_file, csv_file.name)
            # Include settings.json
            settings_file = config.DATA_DIR / "settings.json"
            if settings_file.exists():
                zipf.write(settings_file, "settings.json")
        
        # Encrypt the zip file
        encrypted_backup = self.encrypt_file(backup_zip)
        
        # Remove unencrypted zip
        backup_zip.unlink()
        
        print(f"✓ Created encrypted backup: {encrypted_backup.name}")
        return encrypted_backup
    
    def get_drive_service(self):
        """Get authenticated Google Drive service."""
        creds = None
        
        # Load existing token
        if self.token_file.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_file.exists():
                    raise FileNotFoundError(
                        "credentials.json not found. "
                        "Please download from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_file), SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            self.token_file.write_text(creds.to_json())
        
        return build('drive', 'v3', credentials=creds)
    
    def upload_to_drive(self, filepath: Path) -> str:
        """Upload file to Google Drive."""
        service = self.get_drive_service()
        
        file_metadata = {
            'name': filepath.name,
            'parents': []  # Root folder
        }
        
        media = MediaFileUpload(str(filepath), resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, createdTime'
        ).execute()
        
        print(f"✓ Uploaded to Google Drive: {file.get('name')} (ID: {file.get('id')})")
        return file.get('id')
    
    def list_backups_on_drive(self):
        """List all backups on Google Drive."""
        service = self.get_drive_service()
        
        results = service.files().list(
            q="name contains 'findash_backup_'",
            fields="files(id, name, createdTime, size)",
            orderBy="createdTime desc"
        ).execute()
        
        return results.get('files', [])
    
    def download_from_drive(self, file_id: str, output_path: Path):
        """Download file from Google Drive."""
        service = self.get_drive_service()
        
        request = service.files().get_media(fileId=file_id)
        
        with open(output_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%")
    
    def restore_backup(self, encrypted_backup: Path):
        """Restore from encrypted backup."""
        # Decrypt backup
        decrypted_zip = encrypted_backup.with_suffix('')
        self.decrypt_file(encrypted_backup, decrypted_zip)
        
        # Extract files
        with zipfile.ZipFile(decrypted_zip, 'r') as zipf:
            zipf.extractall(config.DATA_DIR)
        
        # Remove decrypted zip
        decrypted_zip.unlink()
        
        print(f"✓ Restored backup from: {encrypted_backup.name}")
    
    def cleanup_old_backups(self, keep_days: int = 30):
        """Remove local backups older than keep_days."""
        cutoff = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        
        for backup_file in self.backup_dir.glob("findash_backup_*.encrypted"):
            if backup_file.stat().st_mtime < cutoff:
                backup_file.unlink()
                print(f"✓ Removed old backup: {backup_file.name}")
    
    def run_backup(self):
        """Run full backup process."""
        print("\n" + "="*60)
        print("FIN-DASH Backup Starting...")
        print("="*60 + "\n")
        
        try:
            # Create encrypted backup
            backup_file = self.create_backup()
            
            # Upload to Google Drive
            file_id = self.upload_to_drive(backup_file)
            
            # Cleanup old local backups
            self.cleanup_old_backups(keep_days=30)
            
            print("\n" + "="*60)
            print("✓ Backup Completed Successfully!")
            print("="*60 + "\n")
            
            return True
        except Exception as e:
            print(f"\n✗ Backup Failed: {str(e)}\n")
            return False

# Global instance
backup_service = BackupService()
```

### 1.4 Create Backup CLI

**File:** `backend/backup.py`

```python
"""CLI for backup operations."""
import argparse
from services.backup_service import backup_service

def main():
    parser = argparse.ArgumentParser(description='FIN-DASH Backup Manager')
    parser.add_argument('action', choices=['backup', 'list', 'restore'],
                       help='Action to perform')
    parser.add_argument('--file-id', help='Google Drive file ID (for restore)')
    
    args = parser.parse_args()
    
    if args.action == 'backup':
        backup_service.run_backup()
    
    elif args.action == 'list':
        backups = backup_service.list_backups_on_drive()
        print("\nBackups on Google Drive:")
        print("-" * 80)
        for backup in backups:
            print(f"Name: {backup['name']}")
            print(f"ID: {backup['id']}")
            print(f"Created: {backup['createdTime']}")
            print(f"Size: {int(backup.get('size', 0)) / 1024:.2f} KB")
            print("-" * 80)
    
    elif args.action == 'restore':
        if not args.file_id:
            print("Error: --file-id required for restore")
            return
        
        # Download and restore
        from pathlib import Path
        temp_file = Path("temp_backup.zip.encrypted")
        backup_service.download_from_drive(args.file_id, temp_file)
        backup_service.restore_backup(temp_file)
        temp_file.unlink()

if __name__ == '__main__':
    main()
```

### 1.5 Schedule Automatic Backups

**File:** `backend/scheduler_backup.py`

```python
"""Backup scheduler - runs daily backups."""
import schedule
import time
from services.backup_service import backup_service

def run_daily_backup():
    """Run daily backup at 2 AM."""
    backup_service.run_backup()

# Schedule backup daily at 2:00 AM
schedule.every().day.at("02:00").do(run_daily_backup)

print("Backup scheduler started. Daily backups at 2:00 AM.")
print("Press Ctrl+C to stop.")

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

### 1.6 Usage

**Manual Backup:**
```bash
cd backend
python backup.py backup
```

**List Backups:**
```bash
python backup.py list
```

**Restore Backup:**
```bash
python backup.py restore --file-id <GOOGLE_DRIVE_FILE_ID>
```

**Start Automatic Daily Backups:**
```bash
python scheduler_backup.py
```

**Run as Background Service (Windows):**
```powershell
# Create scheduled task
schtasks /create /tn "FIN-DASH Backup" /tr "python C:\path\to\backend\scheduler_backup.py" /sc daily /st 02:00
```

**Run as Background Service (Linux/Mac):**
```bash
# Add to crontab
crontab -e

# Add line:
0 2 * * * cd /path/to/backend && python scheduler_backup.py
```

---

## Phase 2: VPN Remote Access (OPTIONAL)

### 2.1 Install Tailscale

**What is Tailscale?**
- Zero-config VPN
- Free for personal use (up to 100 devices)
- Works behind NAT/firewalls
- Encrypted peer-to-peer connections
- No port forwarding needed

**Step 1: Sign Up**
1. Go to https://tailscale.com/
2. Sign up with Google/Microsoft/GitHub account
3. Free tier: 100 devices, unlimited bandwidth

**Step 2: Install on Home Server (Windows)**
```powershell
# Download and install from https://tailscale.com/download/windows
# Or use winget:
winget install tailscale.tailscale
```

**Step 2: Install on Home Server (Linux)**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

**Step 3: Install on Phone/Laptop**
- Download Tailscale app from App Store/Google Play
- Or install on laptop from https://tailscale.com/download
- Sign in with same account

### 2.2 Configure FIN-DASH for Remote Access

**Step 1: Update Backend Config**

Edit `backend/config.py`:
```python
# Change from localhost-only to all interfaces
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")  # Changed from 127.0.0.1

# Add Tailscale IP to CORS
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:8080,http://localhost:8081,"
    "http://100.*.*.* ,http://100.*.*.*:8081"  # Tailscale IPs
).split(",")
```

**Step 2: Get Tailscale IP**
```bash
# On home server
tailscale ip -4
# Example output: 100.101.102.103
```

**Step 3: Access Remotely**

From phone/laptop connected to Tailscale:
```
http://100.101.102.103:8081
```

### 2.3 Security Considerations

**Tailscale Security:**
- ✅ End-to-end encrypted (WireGuard protocol)
- ✅ Zero-trust network
- ✅ No open ports on router
- ✅ Access control lists (ACLs)
- ✅ MFA support

**Additional Security:**
- Consider adding basic auth to FIN-DASH
- Use HTTPS (Let's Encrypt with Tailscale)
- Enable Tailscale MFA
- Review Tailscale access logs

### 2.4 Alternative: WireGuard (More Control)

If you prefer self-hosted VPN:

**Install WireGuard:**
```bash
# Ubuntu/Debian
sudo apt install wireguard

# Generate keys
wg genkey | tee privatekey | wg pubkey > publickey
```

**Configure Server:**
```ini
# /etc/wireguard/wg0.conf
[Interface]
PrivateKey = <SERVER_PRIVATE_KEY>
Address = 10.0.0.1/24
ListenPort = 51820

[Peer]
PublicKey = <CLIENT_PUBLIC_KEY>
AllowedIPs = 10.0.0.2/32
```

**Start WireGuard:**
```bash
sudo wg-quick up wg0
sudo systemctl enable wg-quick@wg0
```

**Port Forwarding:**
- Forward UDP port 51820 on router
- Point to home server IP

**Complexity:** Higher than Tailscale  
**Recommendation:** Use Tailscale unless you need full control

---

## Testing & Verification

### Test Backup

1. **Create Test Backup:**
   ```bash
   python backup.py backup
   ```

2. **Verify on Google Drive:**
   - Check Google Drive for encrypted backup file
   - Should see `findash_backup_YYYYMMDD_HHMMSS.zip.encrypted`

3. **Test Restore:**
   ```bash
   # List backups
   python backup.py list
   
   # Restore (use file ID from list)
   python backup.py restore --file-id <FILE_ID>
   ```

4. **Verify Data:**
   - Check that all CSV files are restored
   - Open FIN-DASH and verify data

### Test VPN Access

1. **Connect to Tailscale:**
   - On phone/laptop, open Tailscale app
   - Verify connected

2. **Get Server IP:**
   ```bash
   tailscale ip -4
   ```

3. **Access FIN-DASH:**
   - Open browser on phone/laptop
   - Navigate to `http://<TAILSCALE_IP>:8081`
   - Verify dashboard loads

4. **Test Functionality:**
   - Add transaction
   - View accounts
   - Check budget
   - Verify all features work

---

## Maintenance

### Daily
- ✅ Automatic backup runs at 2 AM (if scheduler running)

### Weekly
- ✅ Verify backup completed successfully
- ✅ Check Google Drive storage usage

### Monthly
- ✅ Test restore process
- ✅ Review backup retention (30 days)
- ✅ Update dependencies if needed

### Quarterly
- ✅ Review Tailscale access logs
- ✅ Rotate encryption key (optional)
- ✅ Test disaster recovery

---

## Cost Summary

### One-Time Costs
- Development time: 24 hours (R12,000 or 3 days your time)
- Google Cloud setup: R0 (free)
- Tailscale setup: R0 (free)
- **Total:** R12,000

### Monthly Costs
- Google Drive (100GB): R30/month
- Tailscale: R0/month (free tier)
- Electricity (home server): R50-100/month
- **Total:** R80-130/month

### 5-Year Total
- Development: R12,000
- Hosting: R4,800-7,800 (5 years × R80-130/month)
- **Total:** R16,800-19,800

**Savings vs. Multi-User:** R405,600-408,600 (96% savings!)

---

## Troubleshooting

### Backup Issues

**Problem:** "credentials.json not found"
- **Solution:** Download OAuth credentials from Google Cloud Console

**Problem:** "Permission denied" on encryption key
- **Solution:** Check file permissions: `chmod 600 .backup_key`

**Problem:** Backup fails to upload
- **Solution:** Check internet connection, verify Google Drive API enabled

### VPN Issues

**Problem:** Can't connect to Tailscale
- **Solution:** Check Tailscale service running: `sudo systemctl status tailscaled`

**Problem:** Can't access FIN-DASH via Tailscale IP
- **Solution:** Verify APP_HOST is 0.0.0.0, check firewall rules

**Problem:** CORS error when accessing remotely
- **Solution:** Add Tailscale IP range to CORS_ORIGINS

---

## Next Steps

1. **Implement Phase 1 (Backup)** - Week 1
2. **Test backup and restore** - Week 1
3. **Implement Phase 2 (VPN)** - Week 2 (optional)
4. **Test remote access** - Week 2
5. **Set up automatic backups** - Week 2
6. **Document your setup** - Week 3
7. **Enjoy your enhanced FIN-DASH!** - Forever

---

## Conclusion

You now have:
- ✅ Encrypted cloud backups (disaster recovery)
- ✅ Remote access via VPN (access from anywhere)
- ✅ Maintained single-user simplicity
- ✅ Saved R410,000 vs. multi-user
- ✅ Saved 576 hours of development
- ✅ Avoided security and legal liability

**Total investment:** 3 days + R80-130/month  
**Value:** Priceless peace of mind!

---

**Document Version:** 1.0  
**Date:** October 8, 2025  
**Status:** Ready to implement

