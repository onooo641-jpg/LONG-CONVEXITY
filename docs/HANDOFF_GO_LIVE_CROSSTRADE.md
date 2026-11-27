# Handoff: going live beyond Topstep (Lucid / DayTraders via CrossTrade) — status and next steps

**Read this first if you are picking up the go-live work.** Updated 2026-11-27. Workstream A (prop firms).
Detailed technical guide: `docs/GO_LIVE_MULTIFIRM.md`. Topstep's own path: `docs/GO_LIVE.md`.

## 1. Where things stand (one line each)
| Item | Status |
|---|---|
| Which products qualify | 7 products (Lucid, DayTraders, Topstep $3K, …), from `docs/PREREG_PROP_SEARCH3_20261126.md` (table in `GO_LIVE_MULTIFIRM.md`) |
| Bot connector for Lucid / DayTraders / FFN | **Built**: `bridge/crosstrade.py` (NinjaTrader 8 via the CrossTrade NT8 Add-On). First run against the real server 2026-11-27 (sim): check and round trip pass after two fixes |
| Cross-account anti-hedge check | **Built**: engine-scoped claims in `bridge/hedge.py`, shared file `BRIDGE_HEDGE_REGISTRY` |
| Firm rules in the bot | **Built**: `FIRM_PRESETS` in `bridge/config.py` (LucidFlex/LucidDaily 50K, DayTraders 100K/150K Static, Topstep $3K) |
| Practice test (free) | **Running.** 2026-11-27: connected check and Sim101 round trip pass; daily dry run scheduled until 2026-12-05; no dry-run day finished yet |
| Live trading on the new firms | Not before the practice test and a dry run reconcile |

## 2. Facts and where they come from
| Fact | Source |
|---|---|
| CrossTrade's trading API (REST) needs the **Pro plan or above** | Official: crosstrade.io/docs/api/overview (rendered 2026-11-27, run 45929437254) |
| Pro = **$49/month or $469/year**; Standard $29/month has no API | Third-party: Jx's Google search 2026-11-27 (citing CrossTrade pricing page, QuantVPS, Copygram). Confirm at checkout |
| CrossTrade **7-day free trial**, no card, does not auto-renew, includes the REST API | Jx, 2026-11-27 (third-party). The connected check confirms API access on day one |
| Jx's NinjaTrader account: simulation account `DEMO10100109`, $50K sim balance, free trial "expires in 13 days" on 2026-11-27 (ends ≈ 2026-12-10) | Jx's screenshot, 2026-11-27 |
| Rate limit 3 requests/s per CrossTrade user (burst 20), shared by every engine | Official: crosstrade.io/docs/api/rate-limiting |
| NT8 stamps a bar at its close (connector shifts to the open) | The server says `timestampConvention: bar_close` (2026-11-27). Hand comparison with the NT8 chart not yet done |
| No direct Rithmic client: Rithmic needs conformance testing for a custom app | Reason CrossTrade was chosen for all three firms |

**History of the price statement:** the "~$49/month" figure was first given from memory, without a check. The docs read on
2026-11-27 showed only "Pro or above" and no price. Jx's search then confirmed $49/month for Pro (third-party).

## 3. How the connector differs from Topstep (accepted risks)
- The stop and target are placed **after the first fill** (`cancel_and_bracket`), so each trade is unprotected for about 2 s.
- If the bracket fails three times, the connector flattens the position.
- **A resting entry is unprotected if the engine process dies.** Cancel it by hand in NinjaTrader.
- A partial fill counts as the whole fill; the rest of the entry is cancelled.
- Fills for reconciliation come from a NinjaTrader export. CrossTrade's executions endpoint only covers the last 15 minutes.

## 4. Next steps (checklist; tick in this file as they happen)
Only Jx can do sign-ups, type passwords and spend money. Everything else is for a Claude session.

- [x] 2026-11-27 Jx made a NinjaTrader account (sim `DEMO10100109`, trial ends ≈ 2026-12-10).
- [x] 2026-11-27 Jx turned on Remote Control in the Claude desktop app. The cloud session could not use any of the PC's folders
      (`list_computer_folders`: every folder `not_available`; likely the Windows app version). So a **local session on Jx's PC** was
      offered instead (desktop-app card "Set up CrossTrade practice test on this PC"; prompt in section 6).
- [x] 2026-11-27 Jx chose to continue with NinjaTrader over pausing for Topstep-only (offered: Topstep 50K + $3K Challenge on the
      existing connector). Jx's part is done in **one sitting on Sun 29 / Mon 30 Nov**: install NT8 and log in, CrossTrade trial and
      Add-On, key as a user environment variable, then "done" to the PC session. After that the PC stays on with NinjaTrader open on
      US trading nights (21:15–05:15 Malaysia time).
- [x] 2026-11-27 (cloud session) Prepared the PC side so the local session only has to run it: Jx's click-by-click guide
      `docs/CROSSTRADE_PRACTICE_JX.md`; the check now prints the newest bar and the NT8 chart label to compare; `-Collect` on
      `scripts/crosstrade_test.ps1` copies the day's journal, logs PASS/FAIL in NOTES_JX, commits and pushes;
      `scripts/crosstrade_schedule.ps1` registers the Mon–Fri 09:25 New York task. The .ps1 files were not executed (no PowerShell
      in the cloud container); fix them on the PC if they error.
- [x] 2026-11-27 (local session) Repo cloned to `C:\trading\LONG-CONVEXITY`; 29 CrossTrade/multifirm tests pass. NinjaTrader
      8.1.9.1 and the CrossTrade Add-On 1.14.2 were found already installed (details in `docs/NOTES_JX.md`).
- [x] 2026-11-27 NinjaTrader 8 desktop installed and logged in. MNQ 12-26 1-minute bars arrive live (372 bars via the
      connector, newest closed bar 1.5 min old). No purchase was needed.
- [x] 2026-11-27 CrossTrade Add-On installed and connected. Trial start date: **not recorded yet** (the Add-On was already
      installed on 27 Nov, earlier than the planned 29/30 Nov; ask Jx, because it sets the trial's last day).
- [x] 2026-11-27 Key saved on the PC as the Windows user variable `CROSSTRADE_API_KEY`.
- [x] 2026-11-27 `-Step check -Account Sim101`: 17/17 PASS, after the bar-request fix.
  - [ ] Hand comparison of one bar with the NT8 chart (the server already states `bar_close`).
- [x] 2026-11-27 `-Step roundtrip` on Sim101: PASS, after the instrument-name fix.
- [x] 2026-11-27 Daily `-Step dryrun` scheduled: Mon-Fri 22:25 Malaysia time, until 2026-12-05. First run 2026-11-27.
- [ ] Save each day's journal to `docs/jx_runs/crosstrade_test_journal_<YYYYMMDD>.jsonl` and add a dated line to `docs/NOTES_JX.md`
      (done by `-Collect`; tick after the last dry-run day).
- [ ] Reconcile the dry run against the research engine (`scripts/reconcile.py`). Fills come from NinjaTrader's export.
- [ ] Decide (Jx): buy CrossTrade Pro ($49/month) and the first evaluation(s), then `--live`.

**Open question for Jx:** whose computer and accounts will run Lucid / DayTraders, Jx's or the friend's? The friend's existing
Topstep trading stays on the friend's computer (CLAUDE.md).

## 5. Files
| File | What |
|---|---|
| `bridge/crosstrade.py` | The connector (endpoints listed in its header) |
| `bridge/config.py` | `BRIDGE_BROKER`, `FIRM_PRESETS`, CrossTrade variables (`CROSSTRADE_API_KEY`, `_ACCOUNT`, `_INSTRUMENT`, `_PROTECT_POLL_S`) |
| `bridge/live.py` | `make_broker()`; preflight, roundtrip, dry run and live for either broker |
| `bridge/roundtrip.py` | One proof file per engine (`proof_path`) |
| `bridge/preflight.py` | CrossTrade checks (payloads offline; account, connection, bars when connected) |
| `tests/test_crosstrade.py`, `tests/test_multifirm.py` | Tests from the documented request/response shapes |
| `scripts/crosstrade_test.ps1` | Windows script: `-Step check`, `roundtrip`, `dryrun`, `-Collect` (not yet run on Windows) |
| `scripts/crosstrade_schedule.ps1` | Registers the daily dry run in Windows Task Scheduler (`-Remove` deletes it) |
| `scripts/crosstrade_collect.py` | Copies one New York day's journal rows to `docs/jx_runs`, refuses secrets, logs PASS/FAIL |
| `docs/CROSSTRADE_PRACTICE_JX.md` | Jx's click-by-click steps on the PC |
| `data/public/propverify/expand_osstrade_io_docs_*.json` | The rendered CrossTrade docs the connector was written from |
| `docs/GO_LIVE_MULTIFIRM.md` | Full technical guide |

## 6. Prompt given to the local session on Jx's PC (2026-11-27)
> You are running on Jx's own Windows PC. Goal: get the free practice test of the bot's new CrossTrade connector running here, doing
> everything yourself except sign-ups, passwords and spending (those are Jx's; ask him in one short line and wait).
>
> Repo: github.com/onooo641-jpg/LONG-CONVEXITY, branch `claude/ict-trading-resources-ugh07b`.
> - Read `CLAUDE.md` first. Standing rules: never commit secrets; no spending without Jx; `git pull --rebase` before every
>   commit/push; never force-push; no strategy-parameter changes; no help evading prop-firm rules.
> - Then read `docs/GO_LIVE_MULTIFIRM.md` (the plan) and `bridge/crosstrade.py` (the connector, written from CrossTrade's API docs
>   and never yet run against a real server).
>
> Jx is not technical: keep messages to him short and concrete, one action at a time, with exactly what to click.
>
> State as of 2026-11-27:
> - Jx has a NinjaTrader account: web platform, simulation account DEMO10100109, $50K sim, free trial with 13 days left (ends
>   about 2026-12-10). NinjaTrader 8 DESKTOP is not installed yet; CrossTrade needs the desktop app.
> - No CrossTrade account yet. CrossTrade's 7-day trial needs no card, does not auto-renew, and (per Jx) includes the REST API.
> - No Lucid/DayTraders account. Do not buy one. If NinjaTrader's free sim data turns out not to be enough for 1-minute bars, stop
>   and tell Jx (buying a LucidFlex 50K, about $80, is his decision).
>
> Steps:
> 1. Clone the repo (if no clone exists) to `C:\trading\LONG-CONVEXITY` and check out the branch.
>    - Install `uv` if missing (astral.sh installer).
>    - Run `uv run --with pytest python -m pytest -q tests/test_crosstrade.py tests/test_multifirm.py`; all must pass.
> 2. Install NinjaTrader 8 desktop (download from ninjatrader.com; the web platform's "Download" button).
>    - Jx logs in himself.
>    - Confirm a chart of MNQ 12-26 shows live 1-minute bars (NinjaTrader's own sim data connection).
>    - Note the exact NT8 account name to trade on (Sim101 or the DEMO account).
> 3. Only once step 2 works: tell Jx to start the CrossTrade 7-day trial, ideally on a Sunday/Monday, so it covers 5 US trading days
>    and ends before the NinjaTrader trial (about 2026-12-10). Then guide him through installing and connecting the CrossTrade NT8
>    Add-On (follow CrossTrade's own docs at crosstrade.io/docs).
> 4. Run `scripts\crosstrade_test.ps1 -Step savekey` in a PowerShell window Jx can see. He pastes his CrossTrade key into its
>    prompt; it is saved as the Windows user variable `CROSSTRADE_API_KEY`. Never read it into chat, a file in the repo, or a commit.
> 5. From the repo folder run `powershell -ExecutionPolicy Bypass -File scripts\crosstrade_test.ps1 -Step check -Account <NT8 account>`,
>    then `-Step roundtrip`.
>    - On any failure, find the cause.
>    - If the connector disagrees with the real CrossTrade responses, fix `bridge/crosstrade.py` mechanically, add or adjust a test in
>      `tests/test_crosstrade.py`, and keep all tests passing.
>    - Compare the newest bar the check prints with the NT8 chart for the same minute. The connector assumes NT8 stamps bars at their
>      close and shifts them to the open; confirm or fix.
> 6. Create a Windows Task Scheduler task that runs `-Step dryrun` every US trading day (Mon–Fri) at 09:25 America/New_York (21:25 or
>    22:25 Malaysia time, depending on US daylight saving) for the trial's duration. The PC must stay awake, with NinjaTrader and the
>    Add-On running then; tell Jx.
> 7. After each run:
>    - copy `data\journal_crosstrade_test.jsonl` to `docs/jx_runs/crosstrade_test_journal_<YYYYMMDD>.jsonl` (journals never contain
>      secrets; check anyway);
>    - add a short dated entry to `docs/NOTES_JX.md` (what ran, PASS/FAIL, any fix);
>    - commit with `git pull --rebase` first, and push to the branch.
> 8. Finish with a plain summary for Jx: what works, what failed and was fixed, what still needs him.

**Why a separate session on the PC (2026-11-27):** the cloud session runs on a server and cannot reach Jx's PC. Remote Control was
on, but the Windows Claude app offered none of the PC's folders to cloud sessions. A session started on the PC itself can install
and run things there. This file carries the context between them.

**How Jx starts it** (if the suggested-task card is not visible):
1. In the Claude desktop app, click **+ New** (top left).
2. Pick the PC (local), not the cloud environment "LONG-CONVEXITY". Choose or create a folder such as `C:\trading`.
3. Send: "Clone github.com/onooo641-jpg/LONG-CONVEXITY (branch claude/ict-trading-resources-ugh07b), then do section 6 of
   docs/HANDOFF_GO_LIVE_CROSSTRADE.md."

**Local session, also:** tick the checklist in section 4 of this file as steps complete.
