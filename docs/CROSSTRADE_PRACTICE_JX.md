# CrossTrade practice test — Jx's steps on the Windows PC

Free test, $0. Nothing here places a real trade: the practice order goes on a **sim** account, 30% below the market, and is
cancelled; the daily dry run records orders instead of sending them. Plan and background: `docs/GO_LIVE_MULTIFIRM.md`.

Copy each grey box into **PowerShell** (Start menu → type `PowerShell` → open "Windows PowerShell"), press Enter, wait for it to
finish. Not "Run as administrator".

## 1. Get the code (once, ~5 min)
Install Git (skip if `git --version` already prints a version):
```bash
winget install --id Git.Git -e --source winget
```
Close PowerShell, open a new one, then:
```bash
git clone -b claude/ict-trading-resources-ugh07b https://github.com/onooo641-jpg/LONG-CONVEXITY.git C:\trading\LONG-CONVEXITY
```
```bash
cd C:\trading\LONG-CONVEXITY
```
```bash
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Close PowerShell, open a new one, then:
```bash
cd C:\trading\LONG-CONVEXITY; uv run --with pytest python -m pytest -q tests/test_crosstrade.py tests/test_multifirm.py tests/test_crosstrade_collect.py
```
Pass = a row of dots and no `FAILED`.

## 2. NinjaTrader 8 desktop (once, ~15 min)
1. NinjaTrader web platform → **Download** → install NinjaTrader 8 → open it and log in with your NinjaTrader account.
2. Control Center → **Connections** menu: the NinjaTrader connection should be green. Do **not** use "Simulated Data Feed"
   (it makes up prices).
3. Control Center → **New → Chart** → instrument `MNQ 12-26`, type **Minute**, value **1** → OK. Pass = a new bar every minute
   (MNQ trades almost round the clock Mon–Fri; it pauses 06:00–07:00 Malaysia time and on weekends).
4. Control Center → **Accounts** tab: note the account names (e.g. `Sim101`, `DEMO10100109`). We use **Sim101**.

If the chart stays empty or shows no live bars: stop here and tell Claude. (Buying a data feed or a Lucid account is your decision.)

## 3. CrossTrade 7-day trial (start on **Sunday 29 Nov or Monday 30 Nov**)
That covers Mon 30 Nov – Fri 4 Dec and ends before your NinjaTrader trial (~10 Dec). No card needed; it does not renew.
1. crosstrade.io → **Sign Up** → start the free trial.
2. Install the **CrossTrade NT8 Add-On** following CrossTrade's own **Set Up Guide** (crosstrade.io/docs → NinjaTrader 8 →
   Set Up Guide). Keep NinjaTrader open while you do it.
3. Pass = the Add-On shows **Connected** inside NinjaTrader.

## 4. Store your CrossTrade key on this PC only (once)
1. crosstrade.io → **My Account → Security** tab → **Reveal**. Copy the key. Never paste it into chat or any file.
2. Start menu → type `environment` → **Edit environment variables for your account**.
3. Top box ("User variables") → **New…** → Name `CROSSTRADE_API_KEY`, Value: paste the key → OK → OK.
4. Close every PowerShell window (new ones pick it up).

## 5. First checks (NinjaTrader + Add-On open, market trading, ~5 min)
```bash
cd C:\trading\LONG-CONVEXITY; powershell -ExecutionPolicy Bypass -File scripts\crosstrade_test.ps1 -Step check -Account Sim101 -Collect
```
Look at the line **newest bar (compare by hand)**. It says "find the bar labelled HH:MM". On the NT8 MNQ chart, hover that bar
(or open the Data Box) and check Open/High/Low/Close match. Tell Claude: **match**, or **matches the bar one minute earlier**.
```bash
cd C:\trading\LONG-CONVEXITY; powershell -ExecutionPolicy Bypass -File scripts\crosstrade_test.ps1 -Step roundtrip -Account Sim101 -Collect
```
The first time it pushes, a GitHub sign-in window may open: sign in once.

## 6. Daily dry run, automatic (once)
```bash
cd C:\trading\LONG-CONVEXITY; powershell -ExecutionPolicy Bypass -File scripts\crosstrade_schedule.ps1 -Account Sim101 -Until 2026-12-05
```
(Set `-Until` to your trial's last day.) It then runs Mon–Fri at **22:25 Malaysia time** (= 09:25 New York) and sends the
results to GitHub by itself. At that time each day: PC on and logged in (sleep is fine, shut down is not), NinjaTrader and the
CrossTrade Add-On open and connected. A PowerShell window opens and runs until ~05:00; don't close it.

Also once: Control Panel → Power Options → Change plan settings → Change advanced power settings → Sleep →
**Allow wake timers → Enable**.

**US daylight saving:** US clocks move forward on **Sun 14 March 2027**. The planning chat said 2027-03-08; the rule (second Sunday of
March) gives 14 March, and 8 March was the 2026 date. From then the US session is about **21:25–04:00 Malaysia time**. The
scheduled task's wake time is fixed in local time when it is registered, so re-run `scripts\crosstrade_schedule.ps1` after the
change, and again after US clocks go back (Sun 7 Nov 2027).

To stop it early:
```bash
cd C:\trading\LONG-CONVEXITY; powershell -ExecutionPolicy Bypass -File scripts\crosstrade_schedule.ps1 -Remove
```

## If something says FAIL
- **HTTP 401 / 403:** key wrong, or the trial has no API access. Re-copy the key (step 4).
- **HTTP 408:** NinjaTrader closed or the Add-On not connected.
- Anything else: tell Claude; the journal and log are pushed automatically (`docs/jx_runs/`), or are in `C:\trading\LONG-CONVEXITY\data\`.
