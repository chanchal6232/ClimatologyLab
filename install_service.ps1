# ================================================================
# install_service.ps1 - Register Waitress as a Windows Service
# using NSSM (Non-Sucking Service Manager)
# Run this AFTER deploy.ps1 completes successfully.
# ================================================================

param(
    [string]$ProjectDir = 'C:\ClimatologyLab',
    [string]$ServiceName = 'ClimatologyLab'
)

$ErrorActionPreference = 'Stop'

Write-Host '==========================================' -ForegroundColor Cyan
Write-Host ' Install Climatology Lab Windows Service' -ForegroundColor Cyan
Write-Host '==========================================' -ForegroundColor Cyan

# -------------------------------------------------------------------
# STEP 1: Download and install NSSM
# -------------------------------------------------------------------
Write-Host ''
Write-Host '[1/4] Setting up NSSM...' -ForegroundColor Yellow

$nssmDir = 'C:\nssm'
$nssmExe = Join-Path $nssmDir 'nssm.exe'

if (-Not (Test-Path $nssmExe)) {
    Write-Host 'Downloading NSSM...'
    $nssmUrl = 'https://nssm.cc/release/nssm-2.24.zip'
    $zipPath = Join-Path $env:TEMP 'nssm.zip'
    Invoke-WebRequest -Uri $nssmUrl -OutFile $zipPath

    # Extract
    $extractDir = Join-Path $env:TEMP 'nssm-extract'
    Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force

    # Copy the 64-bit exe
    if (-Not (Test-Path $nssmDir)) { New-Item -ItemType Directory -Path $nssmDir -Force | Out-Null }
    $srcExe = Join-Path $extractDir 'nssm-2.24\win64\nssm.exe'
    Copy-Item $srcExe $nssmExe -Force

    # Cleanup
    Remove-Item $zipPath -Force
    Remove-Item $extractDir -Recurse -Force

    Write-Host ('NSSM installed at ' + $nssmExe) -ForegroundColor Green
} else {
    Write-Host 'NSSM already installed' -ForegroundColor Green
}

# -------------------------------------------------------------------
# STEP 2: Remove existing service if present
# -------------------------------------------------------------------
Write-Host ''
Write-Host '[2/4] Checking for existing service...' -ForegroundColor Yellow

$existingSvc = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existingSvc) {
    Write-Host 'Stopping and removing existing service...'
    & $nssmExe stop $ServiceName
    & $nssmExe remove $ServiceName confirm
    Start-Sleep -Seconds 2
    Write-Host 'Old service removed' -ForegroundColor Green
} else {
    Write-Host 'No existing service found' -ForegroundColor Green
}

# -------------------------------------------------------------------
# STEP 3: Install the service
# -------------------------------------------------------------------
Write-Host ''
Write-Host '[3/4] Installing Windows service...' -ForegroundColor Yellow

$pythonExe = Join-Path $ProjectDir 'venv\Scripts\python.exe'
$scriptPath = Join-Path $ProjectDir 'run_server.py'

if (-Not (Test-Path $pythonExe)) {
    Write-Host ('ERROR: Virtual environment not found at ' + $ProjectDir + '\venv') -ForegroundColor Red
    Write-Host 'Run deploy.ps1 first!' -ForegroundColor Red
    exit 1
}

# Install service
& $nssmExe install $ServiceName $pythonExe $scriptPath

# Configure service parameters
& $nssmExe set $ServiceName AppDirectory $ProjectDir
& $nssmExe set $ServiceName DisplayName 'Climatology Lab Website'
& $nssmExe set $ServiceName Description 'Django web application for IIT Roorkee Climatology Lab'
& $nssmExe set $ServiceName Start SERVICE_AUTO_START
& $nssmExe set $ServiceName ObjectName LocalSystem

# Configure logging
$logDir = Join-Path $ProjectDir 'logs'
if (-Not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
$stdoutLog = Join-Path $logDir 'service-stdout.log'
$stderrLog = Join-Path $logDir 'service-stderr.log'
& $nssmExe set $ServiceName AppStdout $stdoutLog
& $nssmExe set $ServiceName AppStderr $stderrLog
& $nssmExe set $ServiceName AppStdoutCreationDisposition 4
& $nssmExe set $ServiceName AppStderrCreationDisposition 4
& $nssmExe set $ServiceName AppRotateFiles 1
& $nssmExe set $ServiceName AppRotateSeconds 86400
& $nssmExe set $ServiceName AppRotateBytes 10485760

Write-Host 'Service installed!' -ForegroundColor Green

# -------------------------------------------------------------------
# STEP 4: Start the service
# -------------------------------------------------------------------
Write-Host ''
Write-Host '[4/4] Starting the service...' -ForegroundColor Yellow

& $nssmExe start $ServiceName
Start-Sleep -Seconds 3

$svc = Get-Service -Name $ServiceName
if ($svc.Status -eq 'Running') {
    Write-Host ''
    Write-Host '==========================================' -ForegroundColor Green
    Write-Host ' Service is RUNNING!' -ForegroundColor Green
    Write-Host '==========================================' -ForegroundColor Green
    Write-Host ''
    Write-Host ('Service Name:  ' + $ServiceName) -ForegroundColor Cyan
    Write-Host 'Status:        Running' -ForegroundColor Cyan
    Write-Host 'Auto-Start:    Yes (starts on reboot)' -ForegroundColor Cyan
    Write-Host ('Logs:          ' + $logDir) -ForegroundColor Cyan
    Write-Host ''
    Write-Host 'Visit: http://3.6.210.134' -ForegroundColor Cyan
    Write-Host ''
    Write-Host 'Useful commands:' -ForegroundColor Yellow
    Write-Host ('  Stop:    ' + $nssmExe + ' stop ' + $ServiceName) -ForegroundColor White
    Write-Host ('  Start:   ' + $nssmExe + ' start ' + $ServiceName) -ForegroundColor White
    Write-Host ('  Restart: ' + $nssmExe + ' restart ' + $ServiceName) -ForegroundColor White
    Write-Host ('  Status:  Get-Service ' + $ServiceName) -ForegroundColor White
    Write-Host ('  Remove:  ' + $nssmExe + ' remove ' + $ServiceName + ' confirm') -ForegroundColor White
} else {
    Write-Host ('WARNING: Service may not have started. Check logs at: ' + $logDir) -ForegroundColor Red
    Write-Host ($nssmExe + ' status ' + $ServiceName) -ForegroundColor Yellow
}
