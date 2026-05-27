# MySQL 8.4 - Complete Uninstall + Reinstall
# Run as Administrator

Write-Host "`n=== MySQL 8.4 - Complete Uninstall & Reinstall ===" -ForegroundColor Cyan

# Step 1: Stop the service
Write-Host "`n[1/6] Stopping MySQL service..." -ForegroundColor Yellow
net stop MySQL84 2>&1 | Write-Host
Start-Sleep 3

# Step 2: Remove the service
Write-Host "`n[2/6] Removing MySQL service..." -ForegroundColor Yellow
& "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqld.exe" --remove MySQL84 2>&1 | Write-Host
Start-Sleep 2

# Step 3: Uninstall via winget
Write-Host "`n[3/6] Uninstalling MySQL via winget..." -ForegroundColor Yellow
winget uninstall --id Oracle.MySQL -e --force --accept-source-agreements 2>&1 | Write-Host
Start-Sleep 3

# Step 4: Clean up leftover files
Write-Host "`n[4/6] Cleaning up leftover data..." -ForegroundColor Yellow
$paths = @(
    "C:\ProgramData\MySQL",
    "C:\Program Files\MySQL"
)
foreach ($p in $paths) {
    if (Test-Path $p) {
        Write-Host "  Removing $p..."
        takeown /F $p /R /D Y 2>&1 | Out-Null
        icacls $p /grant Administrators:F /T 2>&1 | Out-Null
        Remove-Item $p -Recurse -Force -ErrorAction SilentlyContinue
        if (-not (Test-Path $p)) {
            Write-Host "  Removed." -ForegroundColor Green
        } else {
            cmd /c "rmdir /s /q `"$p`"" 2>&1 | Out-Null
            if (-not (Test-Path $p)) { Write-Host "  Removed (alt method)." -ForegroundColor Green }
            else { Write-Host "  WARNING: Could not fully remove $p" -ForegroundColor Red }
        }
    } else {
        Write-Host "  $p already clean." -ForegroundColor Green
    }
}

# Step 5: Reinstall MySQL
Write-Host "`n[5/6] Reinstalling MySQL..." -ForegroundColor Yellow
winget install --id Oracle.MySQL -e --accept-package-agreements --accept-source-agreements 2>&1 | Write-Host
Start-Sleep 5

# Find the newly installed MySQL
$mysqlBin = Get-ChildItem "C:\Program Files\MySQL" -Recurse -Filter "mysql.exe" -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty DirectoryName
if (-not $mysqlBin) {
    Write-Host "  ERROR: MySQL not found after install!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "  Installed at: $mysqlBin" -ForegroundColor Green

# Find the my.ini
$myIniDir = Split-Path (Split-Path $mysqlBin)
$myIni = Get-ChildItem "C:\ProgramData\MySQL" -Recurse -Filter "my.ini" -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName

# Step 6: Initialize and configure
Write-Host "`n[6/6] Initializing MySQL with secure defaults..." -ForegroundColor Yellow

# Check if service exists
$svcName = Get-Service -Name "MySQL*" -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Name
if ($svcName) {
    Write-Host "  Service found: $svcName" -ForegroundColor Green
    # Start the service
    net start $svcName 2>&1 | Write-Host
    Start-Sleep 5
} else {
    Write-Host "  No service found. Installing service..." -ForegroundColor Yellow
    & "$mysqlBin\mysqld.exe" --install 2>&1 | Write-Host
    
    # Initialize
    $dataDir = "C:\ProgramData\MySQL\MySQL Server 8.4\Data"
    if (-not (Test-Path $dataDir)) {
        & "$mysqlBin\mysqld.exe" --initialize-insecure --console 2>&1 | Write-Host
    }
    net start MySQL84 2>&1 | Write-Host
    Start-Sleep 5
}

# Try connecting
Write-Host "`n=== Testing Connection ===" -ForegroundColor Cyan

# First try without password (fresh install)
$result = & "$mysqlBin\mysql.exe" -u root --skip-password -e "SELECT 'CONNECTED!' AS result;" 2>&1
if ($result -match "CONNECTED") {
    Write-Host "  Connected without password (fresh install)." -ForegroundColor Green
    Write-Host "  Setting root password to 'root'..." -ForegroundColor Yellow
    & "$mysqlBin\mysql.exe" -u root --skip-password -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root'; FLUSH PRIVILEGES;" 2>&1 | Write-Host
}

# Test with password
Write-Host "`n=== FINAL TEST ===" -ForegroundColor Cyan
& "$mysqlBin\mysql.exe" -u root -proot -e "SELECT 'CONNECTION SUCCESSFUL!' AS result; SELECT user, host, plugin FROM mysql.user WHERE user='root';" 2>&1 | ForEach-Object { Write-Host "  $_" }

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n*** SUCCESS! MySQL is freshly installed and working! ***" -ForegroundColor Green
    Write-Host "Username: root | Password: root" -ForegroundColor Green
} else {
    # Maybe the installer set a password prompt - try without password
    Write-Host "`n  Trying without password..." -ForegroundColor Yellow
    & "$mysqlBin\mysql.exe" -u root --skip-password -e "SELECT 'CONNECTED (no password)!' AS result; SELECT user, host, plugin FROM mysql.user;" 2>&1 | ForEach-Object { Write-Host "  $_" }
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
