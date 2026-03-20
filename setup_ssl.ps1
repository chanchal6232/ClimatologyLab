# ================================================================
# setup_ssl.ps1 - Automate Nginx and SSL setup on Windows EC2
# Run this AFTER git pull on the server.
# ================================================================

param(
    [string]$Domain = "climatologylab.iitr.ac.in",
    [string]$ProjectDir = "C:\ClimatologyLab",
    [string]$NginxDir = "C:\nginx",
    [string]$NssmDir = "C:\nssm"
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Climatology Lab SSL & Nginx Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# -------------------------------------------------------------------
# STEP 1: Download Nginx for Windows
# -------------------------------------------------------------------
Write-Host "`n[1/5] Downloading Nginx..." -ForegroundColor Yellow
if (-not (Test-Path $NginxDir)) {
    $nginxUrl = "https://nginx.org/download/nginx-1.24.0.zip"
    $zipPath = Join-Path $env:TEMP "nginx.zip"
    Invoke-WebRequest -Uri $nginxUrl -OutFile $zipPath
    Expand-Archive -Path $zipPath -DestinationPath "C:\" -Force
    Rename-Item "C:\nginx-1.24.0" $NginxDir
    Remove-Item $zipPath -Force
    Write-Host "Nginx installed at $NginxDir" -ForegroundColor Green
}
else {
    Write-Host "Nginx already installed at $NginxDir" -ForegroundColor Green
}

# -------------------------------------------------------------------
# STEP 2: Configure Nginx
# -------------------------------------------------------------------
Write-Host "`n[2/5] Configuring Nginx..." -ForegroundColor Yellow
$confPath = Join-Path $ProjectDir "nginx.conf"
$destConf = Join-Path $NginxDir "conf\nginx.conf"

if (Test-Path $confPath) {
    Copy-Item $confPath $destConf -Force
    Write-Host "Nginx config copied to $destConf" -ForegroundColor Green
}
else {
    Write-Host "ERROR: nginx.conf not found in $ProjectDir" -ForegroundColor Red
    exit 1
}

# Create placeholder SSL directory if missing
$sslDir = Join-Path $NssmDir "ssl"
if (-not (Test-Path $sslDir)) { New-Item -ItemType Directory -Path $sslDir -Force | Out-Null }

# -------------------------------------------------------------------
# STEP 3: Register Nginx as a Windows Service
# -------------------------------------------------------------------
Write-Host "`n[3/5] Registering Nginx as a Service..." -ForegroundColor Yellow
$nssmExe = Join-Path $NssmDir "nssm.exe"
if (-not (Test-Path $nssmExe)) {
    Write-Host "ERROR: NSSM not found. Run install_service.ps1 first!" -ForegroundColor Red
    exit 1
}

$svcName = "NginxService"
$existingSvc = Get-Service -Name $svcName -ErrorAction SilentlyContinue
if ($existingSvc) {
    & $nssmExe stop $svcName
    & $nssmExe remove $svcName confirm
}

$nginxExe = Join-Path $NginxDir "nginx.exe"
& $nssmExe install $svcName $nginxExe
& $nssmExe set $svcName AppDirectory $NginxDir
& $nssmExe start $svcName

Write-Host "Nginx service is now running!" -ForegroundColor Green

# -------------------------------------------------------------------
# STEP 4: Open Port 443 in Windows Firewall
# -------------------------------------------------------------------
Write-Host "`n[4/5] Opening Port 443 in Firewall..." -ForegroundColor Yellow
$ruleName = "Allow HTTPS (Port 443)"
if (-not (Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
    Write-Host "Firewall rule created for Port 443" -ForegroundColor Green
}
else {
    Write-Host "Firewall rule already exists" -ForegroundColor Green
}

# -------------------------------------------------------------------
# STEP 5: Setup Win-ACME for Let's Encrypt (Optional - only if no manual cert)
# -------------------------------------------------------------------
$sslCertPath = Join-Path $sslDir "certificate.crt"

if (-not (Test-Path $sslCertPath)) {
    Write-Host "`n[5/5] Manual certificate not found. Downloading Win-ACME for SSL..." -ForegroundColor Yellow
    $wacmeDir = "C:\win-acme"
    if (-not (Test-Path $wacmeDir)) {
        New-Item -ItemType Directory -Path $wacmeDir -Force | Out-Null
        $wacmeUrl = "https://github.com/win-acme/win-acme/releases/download/v2.2.8.1635/win-acme.v2.2.8.1635.x64.pluggable.zip"
        $zipPath = Join-Path $env:TEMP "win-acme.zip"
        Invoke-WebRequest -Uri $wacmeUrl -OutFile $zipPath
        Expand-Archive -Path $zipPath -DestinationPath $wacmeDir -Force
        Remove-Item $zipPath -Force
    }
    Write-Host "Please run win-acme to get a certificate, or save your manual ones to $sslDir" -ForegroundColor Yellow
}
else {
    Write-Host "`n[5/5] Manual certificate detected at $sslCertPath. Skipping Win-ACME." -ForegroundColor Green
}

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "`nFINAL STEPS:" -ForegroundColor Yellow
Write-Host "1. Ensure Port 443 is open in AWS Security Groups."
if (Test-Path $sslCertPath) {
    Write-Host "2. Manual certificates detected. Nginx is ready to use them." -ForegroundColor Green
}
else {
    Write-Host "2. Run the following command in C:\win-acme to get your certificate:"
    Write-Host "   .\wacs.exe --target manual --host $Domain --certificatestore My --installation nginx --nginxconfigpath $destConf" -ForegroundColor White
}
Write-Host "`n3. Restart ALL services:"
Write-Host "   .\install_service.ps1"
Write-Host "   nssm restart NginxService"
