# How to run the UniswapX paper filler on your PC (about 36 hours, no money)

**What it is:** a small program that only *reads* public data. It has **no wallet, no keys and cannot trade**. It watches UniswapX
orders on Arbitrum, checks what price a public exchange route could have paid, and compares that with the bot that actually filled each
order. You send back two files; I turn them into the verdict (test #371 Stage 5, `docs/PREREG_UNISWAPX_20261124.md`).

## Windows (about 10 minutes to set up)
1. **Install Python** (skip if you already have it): go to https://www.python.org/downloads/ → *Download Python 3.x* → run the installer →
   **tick "Add python.exe to PATH"** at the bottom of the first screen → *Install Now*.
2. **Save the program**: create a folder `C:\paperfiller` and put `uniswapx_paper_filler.py` in it (the file I sent you).
3. **Stop the PC from sleeping**: Settings → System → Power (& battery) → *Screen and sleep* → set "When plugged in, put my device to
   sleep after" to **Never**. Keep it plugged in.
4. **Start it**: press the Windows key, type `cmd`, press Enter. In the black window type these two lines (Enter after each):
   ```
   cd C:\paperfiller
   python uniswapx_paper_filler.py --hours 36
   ```
   It prints a short summary every 10 minutes. **Leave the window open.**
5. **After 36 hours** it stops by itself. Send me the two files from `C:\paperfiller`: `uniswapx_paper_summary.txt` and
   `uniswapx_paper_log.jsonl` (attach them in this chat).

## Mac
Install Python from python.org, put the file in a folder (e.g. Desktop/paperfiller), open Terminal and run
`cd ~/Desktop/paperfiller` then `python3 uniswapx_paper_filler.py --hours 36`. Keep the Mac awake (System Settings → Battery/Energy →
prevent sleeping when the display is off).

## If something goes wrong
- **PC restarted or the window closed:** just run the same two lines again. It adds to the same log; the summary counts every segment.
- **You want to stop early:** press Ctrl+C. The log is kept.
- **"python is not recognized":** Python wasn't added to PATH — re-run the installer, choose *Modify*, tick "Add Python to environment
  variables".
- **Lots of "api_error" lines:** your internet or the public service was down for a moment; it keeps retrying by itself.

## What I will report
Out of the orders filled while it ran: how often a public-DEX route could have matched the winning bot's price (the "competitive
share"), and how much paper profit that would have meant per year. Pre-registered rule: under 5% competitive or under $5K/yr → dead;
at least 10% and $15K/yr → worth building a real filler (speed still untested).
