# R3 Sistema Riflesso — configurazione Windows (una volta).
# Esegui in PowerShell come utente normale (non serve Admin):
#   irm https://raw.githubusercontent.com/raffaellocantatelli/R3-sistema-riflesso/main/scripts/setup-windows.ps1 | iex
# oppure, dopo il clone:
#   powershell -ExecutionPolicy Bypass -File .\scripts\setup-windows.ps1
#
# Questo script NON apre un tunnel verso Grok. Configura SOLO questo PC.

$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/raffaellocantatelli/R3-sistema-riflesso.git"
$Dest = Join-Path $env:USERPROFILE "R3-sistema-riflesso"

Write-Host "=== R3 Riflesso · setup Windows ===" -ForegroundColor Red
Write-Host "Destinazione: $Dest"
Write-Host "Questo non collega Grok al mouse. Installa il riflesso QUI."
Write-Host ""

function Have($cmd) { return [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

if (-not (Have "git")) {
    Write-Host "[git] non trovato."
    if (Have "winget") {
        Write-Host "[git] installo Git con winget..."
        winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
    } else {
        Write-Host "Installa Git da https://git-scm.com/download/win e rilancia lo script."
        exit 1
    }
}

$py = $null
foreach ($c in @("py", "python")) {
    if (Have $c) { $py = $c; break }
}
if (-not $py) {
    Write-Host "[python] non trovato."
    if (Have "winget") {
        Write-Host "[python] installo Python 3.12 con winget..."
        winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements
        $py = "py"
    } else {
        Write-Host "Installa Python 3.12 da https://www.python.org/downloads/ (spunta Add to PATH) e rilancia."
        exit 1
    }
}

if (-not (Test-Path (Join-Path $Dest "r3_riflesso"))) {
    if (Test-Path $Dest) {
        Write-Host "[git] cartella presente ma incompleta, non la tocco. Clona a mano o svuota $Dest"
        exit 1
    }
    Write-Host "[git] clone $RepoUrl"
    git clone $RepoUrl $Dest
} else {
    Write-Host "[git] repo gia' presente, pull"
    Push-Location $Dest
    git pull --ff-only
    Pop-Location
}

Set-Location $Dest

$venvPy = Join-Path $Dest ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Write-Host "[venv] creo .venv"
    if ($py -eq "py") { py -3 -m venv .venv } else { python -m venv .venv }
}
& $venvPy -m pip install --upgrade pip
if (Test-Path ".\requirements.txt") {
    & $venvPy -m pip install -r requirements.txt
}

$cfgPath = Join-Path $Dest "config.json"
$cfg = Get-Content $cfgPath -Raw -Encoding UTF8 | ConvertFrom-Json
$cfg.language = "it"
$cfg.backend = "demo"
$cfg.dry_run = $false
$cfg | ConvertTo-Json -Depth 6 | Set-Content $cfgPath -Encoding UTF8
Write-Host "[config] language=it backend=demo"

New-Item -ItemType Directory -Force -Path (Join-Path $Dest "scripts") | Out-Null
$desktop = [Environment]::GetFolderPath("Desktop")
$launcher = Join-Path $Dest "scripts\avvia-riflesso.cmd"
$cmd = @"
@echo off
cd /d "$Dest"
".venv\Scripts\python.exe" -m r3_riflesso.reflex --backend demo
pause
"@
Set-Content -Path $launcher -Value $cmd -Encoding ASCII

$replay = Join-Path $Dest "scripts\replay-reel.cmd"
$cmd2 = @"
@echo off
cd /d "$Dest"
".venv\Scripts\python.exe" -m r3_riflesso.reflex --backend demo --replay
pause
"@
Set-Content -Path $replay -Value $cmd2 -Encoding ASCII

$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut((Join-Path $desktop "R3 Riflesso.lnk"))
$lnk.TargetPath = $launcher
$lnk.WorkingDirectory = $Dest
$lnk.Description = "Sistema Riflesso R3 (demo, catalogo chiuso)"
$lnk.Save()

Write-Host ""
Write-Host "FATTO (strato TECNICO, su QUESTO PC)" -ForegroundColor Green
Write-Host "  repo:      $Dest"
Write-Host "  scorciatoia desktop: R3 Riflesso.lnk"
Write-Host ""
Write-Host "Prova ora il reel:"
& $venvPy -m r3_riflesso.reflex --backend demo --replay
Write-Host ""
Write-Host "Grok non e' in questo processo. Il riflesso si. Chiudi con :q"
