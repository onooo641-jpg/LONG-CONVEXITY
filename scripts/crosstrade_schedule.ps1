# Sets up the CrossTrade practice dry run to start by itself every US trading day (Mon-Fri) at 09:25 New York.
# (docs/GO_LIVE_MULTIFIRM.md step 5). Run once from the repo folder, in a normal (not admin) PowerShell window:
#
#   powershell -ExecutionPolicy Bypass -File scripts\crosstrade_schedule.ps1 -Account Sim101 -Until 2026-12-11
#   powershell -ExecutionPolicy Bypass -File scripts\crosstrade_schedule.ps1 -Remove        (delete the task)
#
# Each run: scripts\crosstrade_test.ps1 -Step dryrun -Collect (records orders, sends none; then copies the journal,
# logs PASS/FAIL in docs\NOTES_JX.md, commits and pushes). Needs CROSSTRADE_API_KEY set as a Windows USER variable.
# At that time the PC must be on and logged in (the task wakes it from sleep, not from shut down), and NinjaTrader 8
# with the CrossTrade Add-On must be open and connected.
#
# The start time is worked out in this PC's clock from New York time on the day you run this. US clocks change on
# 2027-03-14; if the task is still wanted after that, run this again.

param(
    [string]$Account = "Sim101",
    [datetime]$Until = (Get-Date).Date.AddDays(8),
    [switch]$Remove
)
$ErrorActionPreference = "Stop"
$TaskName = "LONG-CONVEXITY CrossTrade dry run"
$repo = Split-Path $PSScriptRoot -Parent

if ($Remove) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed '$TaskName' (if it existed)."
    return
}
if (-not [Environment]::GetEnvironmentVariable("CROSSTRADE_API_KEY", "User")) {
    throw "CROSSTRADE_API_KEY is not set as a Windows USER variable yet; a scheduled run cannot ask for it."
}

# 09:25 New York -> this PC's clock, and which local weekdays that falls on.
$et = [TimeZoneInfo]::FindSystemTimeZoneById("Eastern Standard Time")
$nyToday = [TimeZoneInfo]::ConvertTime([DateTime]::UtcNow, $et).Date
$nyRun = [DateTime]::SpecifyKind($nyToday.AddHours(9).AddMinutes(25), [DateTimeKind]::Unspecified)
$localRun = [TimeZoneInfo]::ConvertTime($nyRun, $et, [TimeZoneInfo]::Local)
$shift = ($localRun.Date - $nyRun.Date).Days
$names = "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
$days = 1..5 | ForEach-Object { $names[($_ + $shift + 7) % 7] }

$taskArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$repo\scripts\crosstrade_test.ps1`" -Step dryrun -Account `"$Account`" -Collect"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $taskArgs -WorkingDirectory $repo
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $days -At $localRun
$trigger.EndBoundary = $Until.ToString("yyyy-MM-ddT23:59:59")
# Interactive = runs in Jx's logged-in session (where NinjaTrader is), and needs no stored Windows password.
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 9)
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal `
    -Settings $settings -Description "CrossTrade practice dry run (no orders sent). See docs\GO_LIVE_MULTIFIRM.md." -Force | Out-Null

Write-Host ("Task '{0}' set: {1} at {2:HH:mm} this PC's time (= 09:25 New York), account {3}, last run {4:yyyy-MM-dd}." -f `
    $TaskName, ($days -join ", "), $localRun, $Account, $Until)
Write-Host "Keep the PC on and logged in at that time, with NinjaTrader 8 and the CrossTrade Add-On open and connected."
Write-Host "Also: Control Panel > Power Options > Change plan settings > Change advanced power settings > Sleep > Allow wake timers = Enable."
