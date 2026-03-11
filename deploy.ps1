# ================================================================
# deploy.ps1 — One-shot deployment script for EC2 Windows Server
# Run this via PowerShell on the EC2 instance after copying the
# project folder and filling in .env.production values.
# ================================================================

param(
    [string]$ProjectDir = "C:\ClimatologyLab",
    [string]$PythonVersion = "3.12.8"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Climatology Lab — EC2 Deployment Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# -------------------------------------------------------------------
# STEP 1: Check / Install Python
# -------------------------------------------------------------------
Write-Host "`n[1/8] Checking Python installation..." -ForegroundColor Yellow

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python not found. Downloading Python $PythonVersion installer..." -ForegroundColor Red
    $installerUrl = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-amd64.exe"
    $installerPath = "$env:TEMP\python-installer.exe"
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
    Write-Host "Installing Python $PythonVersion (this may take a minute)..."
    Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1" -Wait
    Remove-Item $installerPath -Force
    # Refresh PATH
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
    Write-Host "Python installed successfully!" -ForegroundColor Green
} else {
    Write-Host "Python found: $(python --version)" -ForegroundColor Green
}

# -------------------------------------------------------------------
# STEP 2: Create project directory and copy files
# -------------------------------------------------------------------
Write-Host "`n[2/8] Setting up project directory..." -ForegroundColor Yellow

if (-Not (Test-Path $ProjectDir)) {
    New-Item -ItemType Directory -Path $ProjectDir -Force | Out-Null
    Write-Host "Created $ProjectDir"
    Write-Host ""
    Write-Host "*** ACTION REQUIRED ***" -ForegroundColor Red
    Write-Host "Copy your project files into $ProjectDir and re-run this script." -ForegroundColor Red
    Write-Host "You can use File Explorer, SCP, or Git clone." -ForegroundColor Red
    exit 1
}

# Check that manage.py exists (basic sanity check)
if (-Not (Test-Path "$ProjectDir\manage.py")) {
    Write-Host "ERROR: $ProjectDir\manage.py not found!" -ForegroundColor Red
    Write-Host "Make sure your Django project files are in $ProjectDir" -ForegroundColor Red
    exit 1
}

Write-Host "Project files found in $ProjectDir" -ForegroundColor Green

# -------------------------------------------------------------------
# STEP 3: Create virtual environment
# -------------------------------------------------------------------
Write-Host "`n[3/8] Creating/updating virtual environment..." -ForegroundColor Yellow

$venvDir = "$ProjectDir\venv"
if (-Not (Test-Path "$venvDir\Scripts\activate.ps1")) {
    python -m venv $venvDir
    Write-Host "Virtual environment created at $venvDir" -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
}

# Activate
& "$venvDir\Scripts\Activate.ps1"

# -------------------------------------------------------------------
# STEP 4: Install dependencies
# -------------------------------------------------------------------
Write-Host "`n[4/8] Installing Python dependencies..." -ForegroundColor Yellow

pip install --upgrade pip
pip install -r "$ProjectDir\requirements.txt"
Write-Host "Dependencies installed!" -ForegroundColor Green

# -------------------------------------------------------------------
# STEP 5: Set up .env
# -------------------------------------------------------------------
Write-Host "`n[5/8] Checking environment configuration..." -ForegroundColor Yellow

$envFile = "$ProjectDir\.env"
$envProdFile = "$ProjectDir\.env.production"

if (-Not (Test-Path $envFile)) {
    if (Test-Path $envProdFile) {
        Copy-Item $envProdFile $envFile
        Write-Host ".env.production copied to .env" -ForegroundColor Green
        Write-Host ""
        Write-Host "*** ACTION REQUIRED ***" -ForegroundColor Red
        Write-Host "Edit $envFile and fill in the actual passwords/keys, then re-run." -ForegroundColor Red
        notepad $envFile
        exit 1
    } else {
        Write-Host "ERROR: Neither .env nor .env.production found!" -ForegroundColor Red
        exit 1
    }
}

# Quick validation
$envContent = Get-Content $envFile -Raw
if ($envContent -match "CHANGE-ME|YOUR_RDS_PASSWORD|YOUR_RESEND_API_KEY") {
    Write-Host "WARNING: .env still contains placeholder values!" -ForegroundColor Red
    Write-Host "Edit $envFile and replace all placeholder values, then re-run." -ForegroundColor Red
    notepad $envFile
    exit 1
}

Write-Host ".env configured!" -ForegroundColor Green

# -------------------------------------------------------------------
# STEP 6: Collect static files
# -------------------------------------------------------------------
Write-Host "`n[6/8] Collecting static files..." -ForegroundColor Yellow

Set-Location $ProjectDir
python manage.py collectstatic --noinput
Write-Host "Static files collected!" -ForegroundColor Green

# -------------------------------------------------------------------
# STEP 7: Run database migrations
# -------------------------------------------------------------------
Write-Host "`n[7/8] Running database migrations against RDS..." -ForegroundColor Yellow

python manage.py migrate
Write-Host "Migrations complete!" -ForegroundColor Green

# -------------------------------------------------------------------
# STEP 8: Validate deployment
# -------------------------------------------------------------------
Write-Host "`n[8/8] Running deployment checks..." -ForegroundColor Yellow

python manage.py check --deploy
Write-Host ""

# -------------------------------------------------------------------
# STEP 9: Open firewall
# -------------------------------------------------------------------
Write-Host "`nConfiguring Windows Firewall..." -ForegroundColor Yellow

$ruleName = "ClimatologyLab-HTTP"
$existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
if (-not $existingRule) {
    New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow | Out-Null
    Write-Host "Firewall rule added for port 80" -ForegroundColor Green
} else {
    Write-Host "Firewall rule already exists" -ForegroundColor Green
}

# -------------------------------------------------------------------
# DONE
# -------------------------------------------------------------------
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host " Deployment preparation complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the server manually:" -ForegroundColor Cyan
Write-Host "  cd $ProjectDir" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python run_server.py" -ForegroundColor White
Write-Host ""
Write-Host "To install as a Windows service (auto-start on boot):" -ForegroundColor Cyan
Write-Host "  .\install_service.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Then visit: http://3.6.210.134" -ForegroundColor Cyan
