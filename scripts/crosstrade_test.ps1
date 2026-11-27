# CrossTrade practice test on Windows: setup check, practice order, dry run.  (docs/GO_LIVE_MULTIFIRM.md steps 2-5)
#
# Before running: NinjaTrader 8 open, CrossTrade NT8 Add-On connected, a data connection live in NinjaTrader,
# and the CrossTrade trial started. Run from the repo folder:
#
#   powershell -ExecutionPolicy Bypass -File scripts\crosstrade_test.ps1 -Step savekey     (once: paste the key, saved on this PC only)
#   powershell -ExecutionPolicy Bypass -File scripts\crosstrade_test.ps1 -Step check
#   powershell -ExecutionPolicy Bypass -File scripts\crosstrade_test.ps1 -Step roundtrip
#   powershell -ExecutionPolicy Bypass -File scripts\crosstrade_test.ps1 -Step brackettest (sim only: 1 contract filled,
#                                                                                         stop+target checked, flattened)
#   powershell -ExecutionPolicy Bypass -File scripts\crosstrade_test.ps1 -Step dryrun      (each trading day, from 09:25 New York)
#
# Add -Collect to copy that day's journal rows to docs\jx_runs, log PASS/FAIL in docs\NOTES_JX.md, commit and push
# (scripts\crosstrade_schedule.ps1 sets up the daily dry run with -Collect). Console output goes to data\crosstrade_<step>_<date>.log.
#
# The CrossTrade key is asked for each run and kept only in this window's memory: it is never written to a file.
# Nothing here trades for real: 'roundtrip' places one 1-lot limit 30% below the market on the account you name
# (use Sim101) and cancels it; 'dryrun' records orders instead of sending them.

param(
    [ValidateSet("savekey", "check", "roundtrip", "brackettest", "exittest", "dryrun")] [string]$Step = "check",
    [string]$Account = "Sim101",
    [string]$Instrument = "MNQ 12-26",
    [string]$Preset = "LucidFlex 50K",
    [double]$AccountStart = 50000,
    [switch]$Collect
)
$ErrorActionPreference = "Stop"

if ($Step -eq "savekey") {
    # Saved as a Windows user environment variable: on this PC only, never in the repo, never in a chat.
    $secure = Read-Host "Paste your CrossTrade key (CrossTrade website: My Account > Security > Reveal), then press Enter" -AsSecureString
    $key = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure))
    if ($key.Length -lt 8) { throw "That does not look like a key; nothing saved." }
    [Environment]::SetEnvironmentVariable("CROSSTRADE_API_KEY", $key, "User")
    Write-Host "Saved. The bot can now use CrossTrade without asking again."
    exit 0
}
$Branch = "claude/ict-trading-resources-ugh07b"
# Run from the repo folder whatever folder this was started from (Task Scheduler starts elsewhere).
Set-Location (Split-Path $PSScriptRoot -Parent)
New-Item -ItemType Directory -Force data | Out-Null
$nyNow = [TimeZoneInfo]::ConvertTime([DateTime]::UtcNow, [TimeZoneInfo]::FindSystemTimeZoneById("Eastern Standard Time"))
# The trading day runs 18:00 to 18:00 New York (same rule as scripts\crosstrade_collect.py).
$nyDate = if ($nyNow.Hour -ge 18) { $nyNow.Date.AddDays(1) } else { $nyNow.Date }
Start-Transcript -Path ("data\crosstrade_{0}_{1:yyyyMMdd}.log" -f $Step, $nyDate) -Append | Out-Null

# uv's installer puts it in %USERPROFILE%\.local\bin, which a window opened before the install does not have on PATH.
if (Test-Path "$env:USERPROFILE\.local\bin\uv.exe") { $env:Path = "$env:USERPROFILE\.local\bin;$env:Path" }
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installing uv (Python runner, from astral.sh)..."
    powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}

# A scheduled run cannot answer a prompt: it uses CROSSTRADE_API_KEY from the Windows user environment if set there
# (set it yourself; it lives on this PC only, never in the repo). Otherwise the key is asked for.
$userKey = [Environment]::GetEnvironmentVariable("CROSSTRADE_API_KEY", "User")
$keptUserKey = [bool]$userKey
if ($keptUserKey) {
    $env:CROSSTRADE_API_KEY = $userKey
} else {
    $secure = Read-Host "CrossTrade secret key (My Account > Security > Reveal)" -AsSecureString
    $env:CROSSTRADE_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure))
}
$env:BRIDGE_BROKER = "crosstrade"
$env:CROSSTRADE_ACCOUNT = $Account
$env:CROSSTRADE_INSTRUMENT = $Instrument
$env:BRIDGE_PRESET = $Preset
$env:BRIDGE_ACCOUNT_START = "$AccountStart"
$env:BRIDGE_USE_GUARD = "0"
$env:BRIDGE_HEDGE_REGISTRY = "$PWD\data\hedge.json"

$journal = "data\journal_crosstrade_test.jsonl"
# Journal rows carry whole seconds, so this is cut to whole seconds too.
$runStart = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
$code = 1
try {
    switch ($Step) {
        "check" {
            uv run python -m bridge.live --preflight --offline --risk 900
            if ($LASTEXITCODE -ne 0) { throw "offline check failed" }
            uv run python -m bridge.live --preflight --risk 900
            $code = $LASTEXITCODE
            if ($code -ne 0) {
                Write-Host "`nConnected check failed. HTTP 401/403: the key is wrong or the trial has no API access (needs Pro)."
                Write-Host "HTTP 408: NinjaTrader is closed or the CrossTrade Add-On is not connected."
                throw "connected check failed"
            }
            Write-Host "`nNow compare the newest bar printed above with the NinjaTrader chart for the same minute."
        }
        "roundtrip" {
            if ($Account -notmatch "^Sim") {
                $ok = Read-Host "$Account does not look like a sim account. Type YES to place the probe order on it anyway"
                if ($ok -ne "YES") { throw "stopped" }
            }
            uv run python -m bridge.live --roundtrip --journal $journal --risk 900
            $code = $LASTEXITCODE
        }
        "exittest" {
            # Sim only (bridge.exit_probe refuses other accounts). Short 1 contract, 3-point stop/target, waits up to 10 min.
            uv run python -m bridge.live --exit-test --journal $journal --risk 900
            $code = $LASTEXITCODE
        }
        "brackettest" {
            # bridge.bracket_probe itself refuses any account whose name does not start with "Sim".
            uv run python -m bridge.live --bracket-test --journal $journal --risk 900
            $code = $LASTEXITCODE
        }
        "dryrun" {
            uv run python -m bridge.live --journal $journal --risk 900
            $code = $LASTEXITCODE
        }
    }
    Write-Host "`nDone (exit $code). Send the journal ($journal) and anything above marked FAIL back to Claude."
}
finally {
    $ErrorActionPreference = "Continue"   # git and uv write progress to stderr; that must not abort the collect
    if ($Collect) {
        # The collect script scans the rows for the key itself, so it gets the key for this one call only.
        uv run python scripts\crosstrade_collect.py --step $Step --exit-code $code --date ("{0:yyyy-MM-dd}" -f $nyDate) --since $runStart
        $collected = $LASTEXITCODE
        Remove-Item Env:CROSSTRADE_API_KEY -ErrorAction SilentlyContinue
        if ($collected -eq 2) {
            Write-Host "Journal NOT copied: it looked like it held a secret. Nothing was committed. Tell Claude."
        } elseif ((git rev-parse --abbrev-ref HEAD) -ne $Branch) {
            Write-Host "Not on $Branch, so nothing was committed. The journal copy is in docs\jx_runs."
        } else {
            $ymd = "{0:yyyyMMdd}" -f $nyDate
            git pull --rebase --autostash origin $Branch
            git add "docs/jx_runs/crosstrade_test_journal_$ymd.jsonl" docs/NOTES_JX.md
            git commit -m "CrossTrade practice test: $Step journal $ymd (exit $code)"
            git pull --rebase --autostash origin $Branch
            git push origin $Branch
            if ($LASTEXITCODE -ne 0) { Write-Host "Push failed; the commit is saved on this PC. Tell Claude." }
        }
    }
    Remove-Item Env:CROSSTRADE_API_KEY -ErrorAction SilentlyContinue
    Stop-Transcript | Out-Null
}
