# Sync data files from root /data to /backend/data
# This ensures the backend can read the latest data when running from the backend directory

Write-Host "Syncing data files from /data to /backend/data..." -ForegroundColor Cyan

$sourceDir = "data"
$destDir = "backend\data"

# Ensure destination directory exists
if (-not (Test-Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
}

# List of files to sync
$files = @(
    "accounts.csv",
    "budgets.csv",
    "categories.csv",
    "transactions.csv",
    "cards.csv",
    "debts.csv",
    "goals.csv",
    "investments.csv",
    "recurring_transactions.csv",
    "investment_transactions.csv",
    "exchange_rates.csv",
    "import_history.csv",
    "currencies.csv",
    "settings.json"
)

$syncedCount = 0
$errorCount = 0

foreach ($file in $files) {
    $sourcePath = Join-Path $sourceDir $file
    $destPath = Join-Path $destDir $file
    
    if (Test-Path $sourcePath) {
        try {
            Copy-Item -Path $sourcePath -Destination $destPath -Force
            Write-Host "  ✓ Synced: $file" -ForegroundColor Green
            $syncedCount++
        }
        catch {
            Write-Host "  ✗ Error syncing $file : $_" -ForegroundColor Red
            $errorCount++
        }
    }
    else {
        Write-Host "  ⚠ Skipped: $file (not found in source)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Sync complete!" -ForegroundColor Cyan
Write-Host "  Files synced: $syncedCount" -ForegroundColor Green
if ($errorCount -gt 0) {
    Write-Host "  Errors: $errorCount" -ForegroundColor Red
}

Write-Host ""
Write-Host "Backend data directory is now up to date." -ForegroundColor Green
Write-Host "You can now restart the backend server to see the latest data." -ForegroundColor Yellow

