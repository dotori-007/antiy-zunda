# Zundamon Companion Setup Script
$ErrorActionPreference = "Continue"

$companionDir = $PSScriptRoot
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host "         Zundamon Companion Auto Setup" -ForegroundColor Green
Write-Host "=============================================================================="
Write-Host "Path: $companionDir"
Write-Host ""

# 1. Python Check & Selection
Write-Host "[1/4] Checking Python environment..." -ForegroundColor Cyan
$pythonCmd = "python"
$pyPaths = & where.exe python 2>&1
foreach ($p in $pyPaths) {
    if ($p -and ($p -notmatch "WindowsApps") -and (Test-Path $p.Trim())) {
        $pythonCmd = $p.Trim()
        break
    }
}
if ($pythonCmd -eq "python") {
    try {
        $testPy = & py -3 --version 2>&1
        if ($LASTEXITCODE -eq 0) { $pythonCmd = "py -3" }
    } catch {}
}

try {
    $pyVer = & $pythonCmd --version 2>&1
    Write-Host "[OK] Detected: $pyVer (using: $pythonCmd)" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 2. Pip Dependencies
Write-Host "[2/4] Installing dependencies from requirements.txt..." -ForegroundColor Cyan
& $pythonCmd -m pip install -r "$companionDir\requirements.txt"
Write-Host "[OK] Dependencies ready." -ForegroundColor Green
Write-Host ""

# 3. Windows Task Scheduler
Write-Host "[3/4] Registering Windows Task Scheduler (ZundamonMascot)..." -ForegroundColor Cyan
try {
    $vbsPath = Join-Path $companionDir "start_zundamon.vbs"
    $action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$vbsPath`""
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Days 3)
    Register-ScheduledTask -TaskName "ZundamonMascot" -Action $action -Settings $settings -Force | Out-Null
    Write-Host "[OK] Task Scheduler registered successfully! (Runs on battery)" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Task registration failed: $_" -ForegroundColor Yellow
}
Write-Host ""

# 4. Antigravity Skill Registration
Write-Host "[4/4] Registering Antigravity CLI Skill..." -ForegroundColor Cyan
$userProfile = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::UserProfile)
$skillDestDir = Join-Path $userProfile ".gemini\config\skills\zundamon"
if (-not (Test-Path $skillDestDir)) {
    New-Item -ItemType Directory -Path $skillDestDir -Force | Out-Null
}

$templatePath = Join-Path $companionDir "skill\SKILL.template.md"
$destPath = Join-Path $skillDestDir "SKILL.md"

if (Test-Path $templatePath) {
    $content = Get-Content -Path $templatePath -Raw -Encoding UTF8
    $pyExecStr = if ($pythonCmd.Contains(" ")) { "`"$pythonCmd`"" } else { $pythonCmd }
    $content = $content.Replace("{PYTHON_EXE}", $pyExecStr)
    $content = $content.Replace("{COMPANION_DIR}", $companionDir)
    [System.IO.File]::WriteAllText($destPath, $content, [System.Text.Encoding]::UTF8)
    Write-Host "[OK] Antigravity Skill registered: $destPath" -ForegroundColor Green
} else {
    Write-Host "[WARNING] $templatePath not found." -ForegroundColor Yellow
}
Write-Host ""

# 5. VOICEVOX Check
Write-Host "[Check] Checking VOICEVOX engine..." -ForegroundColor Cyan
try {
    $engine = & $pythonCmd -c "import app; print(app.find_voicevox_engine() or '')" 2>&1
    if ($engine -and (Test-Path $engine.Trim())) {
        Write-Host "[OK] VOICEVOX Engine detected: $engine" -ForegroundColor Green
    } else {
        Write-Host "[INFO] VOICEVOX Engine not detected yet." -ForegroundColor Yellow
        Write-Host "       Download for free from https://voicevox.hiroshiba.jp/ to auto-connect!" -ForegroundColor Yellow
    }
} catch {}

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host "  Setup completed successfully!" -ForegroundColor Green
Write-Host "  You can now type /zundamon in Antigravity CLI,"
Write-Host "  or run start_zundamon.vbs to launch the companion directly."
Write-Host "=============================================================================="
Write-Host ""