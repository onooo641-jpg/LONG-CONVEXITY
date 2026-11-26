# UniswapX quoter application — draft (not sent; Jx decides)

**Where it goes:** Uniswap Labs' UniswapX quoter / filler intake (the "become a quoter" form linked from the UniswapX docs, or the
UniswapX team's contact listed there). Fill in the bracketed parts. Keep it short; they mostly want to know you can quote reliably.

---

**Subject:** UniswapX quoter application — Arbitrum (and Base)

Hi UniswapX team,

We'd like to join the UniswapX RFQ quoter set on Arbitrum (and later Base).

- **Who we are:** [team / company name], a small quantitative team based in Malaysia. Contact: [name, email, Telegram].
- **What we've built:** a quoting engine that prices UniswapX orders against on-chain liquidity via DEX-aggregator routes and fills
  atomically through an executor contract (no inventory needed to start). We ran it in shadow mode for 36 hours on live Arbitrum orders
  (2026-11-24/26): on 153 filled orders our quote matched or beat the winning quote on 51% of them, with a median gap of 0.4 bps.
- **Reliability:** we will only quote what we can fill atomically, so fades should be rare; we're happy to start with a low size limit
  and the usual beta period.
- **Infrastructure:** quote server [region / provider], filler wallet [address], executor contract [address, once deployed].
- **Pairs and size:** majors and stables first (ETH, WBTC, ARB, USDC, USDT), typical order sizes $1K–$100K.

Happy to share our shadow-mode logs or run a test period on your side.

Thanks,
[name]

---

**Before sending (checklist):**
1. Decide whether to apply as an individual or a company (the form may ask; CoW needed a company, UniswapX may not).
2. A filler wallet with a little ETH on Arbitrum for gas.
3. Be ready to deploy the executor contract and quote server if they reply yes (est. 1–2 weeks of build; not started).
4. Expect questions on latency: our 36-hour test measured price, not speed.
