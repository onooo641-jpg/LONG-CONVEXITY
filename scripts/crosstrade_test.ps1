# CrossTrade practice test on Windows: setup check, practice order, dry run.  (docs/GO_LIVE_MULTIFIRM.md steps 2-5)
#
# Before running: NinjaTrader 8 open, CrossTrade NT8 Add-On connected, a data connection live in NinjaTrader,
# and the CrossTrade trial started. Run from the repo folder:
#
#   powershell -ExecutionPolicy Bypass -File scripts\crosstrade_test.ps1 -Step check
#   powershell -ExecutionPolicy Bypass -File scripts\crosstrade_test.ps1 -Step roundtrip
#   powershell -ExecutionPolicy Bypass -File scripts\crosstrade_test.ps1 -Step dryrun      (each trading day, from 09:25 New York)
#
# The CrossTrade key is asked for each run and kept only in this window's memory: it is never written to a file.
# Nothing here trades for real: 'roundtrip' places one 1-lot limit 30% below the market on the account you name
# (use Sim101) and cancels it; 'dryrun' records orders instead of sending them.

param(
    [ValidateSet("check", "roundtrip", "dryrun")] [string]$Step = "check",
    [string]$Account = "Sim101",
    [string]$Instrument = "MNQ 12-26",
    [string]$Preset = "LucidFlex 50K",
    [double]$AccountStart = 50000
)
$ErrorActionPreference = "Stop"

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
try {
    switch ($Step) {
        "check" {
            uv run python -m bridge.live --preflight --offline --risk 900
            if ($LASTEXITCODE -ne 0) { throw "offline check failed" }
            uv run python -m bridge.live --preflight --risk 900
            if ($LASTEXITCODE -ne 0) {
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
        }
        "dryrun" {
            uv run python -m bridge.live --journal $journal --risk 900
        }
    }
    Write-Host "`nDone. Send the journal ($journal) and anything above marked FAIL back to Claude."
}
finally {
    Remove-Item Env:CROSSTRADE_API_KEY -ErrorAction SilentlyContinue
}
