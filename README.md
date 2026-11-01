# CrudeCompass


> Detect. Decide. Replace.
> A tool that warns an oil buyer about supply disruptions, shows the cheapest safe action, and suggests a legal replacement crude.

This README is for **our team of four**. Read it fully once, then use it as the rulebook. If something here is unclear, tell Arun and we will fix the README.

---

## 1. What are we building? (in plain words)

India imports most of its crude oil, and it travels through a few narrow sea lanes. When something goes wrong (a storm, a war, sanctions, a supplier cut), buyers hear late and lose money.

CrudeCompass does three things:

1. **Detect:** gives a route a risk score (0 to 100) and explains why, using real weather and real news data.
2. **Decide:** compares *waiting* with *rerouting* and shows the cost per barrel and the break-even delay (how many days of waiting make rerouting cheaper).
3. **Replace:** if a crude grade becomes too risky, suggests the cheapest blend of other grades that a refinery can run, after a sanctions check.

## 2. Our target (40 days, final date about 10 December 2026)

A **working demo on a laptop** (and a free public link if time allows) for **one corridor**:

- Route 1: Red Sea / Suez
- Route 2 (alternative): around the Cape of Good Hope
- One disrupted crude grade (for example Arab Light) and its replacement blend

**Keep it small. A small demo that works beats a big demo that breaks.**

### Real data vs assumed data

| Real (fetched live from the internet) | Assumed (we write it in CSV files) |
|---|---|
| Weather and sea state from **Open-Meteo** | Crude properties (API gravity, sulphur), approximate public values |
| News volume and tone from **GDELT** | Freight, insurance and ship hire rates |
| Later, if time allows: prices (EIA), USD/INR (FRED), sanctions list (OFAC) | Supplier list and capacities, refinery limits, seasonal history |

Every assumed number goes into `docs/assumptions.md` with a note on where it came from. When a judge asks "where did this number come from?", we always have an answer.

### Not now (we will do these later)
Industry-style folders, automated tests on GitHub, PostgreSQL, Docker, live ship tracking, user logins, machine learning.

---

## 3. Repo layout (flat and simple)

```
crudeCompass/
├── README.md          this file
├── .gitignore         files Git must never upload
├── .env.example       names of API keys (no real keys!)
├── requirements.txt   Python libraries we use
├── app.py             the Streamlit dashboard
├── db.py              create tables, load CSVs, read and write data
├── fetch_weather.py   real Open-Meteo data
├── fetch_news.py      real GDELT data
├── risk.py            risk score with reasons
├── cost.py            wait vs reroute, break-even
├── optimizer.py       replacement blend
├── compliance.py      sanctions check
├── data/              CSV files (routes, ports, assays, suppliers...) and saved sample API replies
└── docs/              contracts.md, assumptions.md, notes
```

**Golden rule: one file, one owner.** Only the owner edits a file. If you need a change in someone else's file, ask them or open a pull request for them to review.

## 4. Who owns what

| Member | Name | Owns | Main job |
|---|---|---|---|
| **A** | Arun | `db.py`, `app.py` (layout), `data/`, repo, deployment | Database, seed data, stubs, dashboard shell, joining everything together, final demo |
| **B** | Manthan | `fetch_weather.py`, `fetch_news.py` | Real Open-Meteo and GDELT data turned into 0 to 100 signals |
| **C** | Shivam | `risk.py`, `cost.py` | Risk score with reasons, wait vs reroute cost, break-even |
| **D** | kaif | `optimizer.py`, `compliance.py`, dashboard widgets | Replacement blend, sanctions check, map and what-if controls |

Review pairs (check each other's pull requests): **A with B**, **C with D**.

---

## 5. The contracts (the most important part)

A **contract** is an agreement: the function's name, what goes in, and the *shape* of what comes out. Everyone writes code against these. Arun will create **stubs** (fake answers with the right shape) in each file by **6 November**, so nobody waits for anybody. When you finish the real version, keep the **same name and the same output keys**.

**Do not change a contract alone.** Tell the team in the chat first, then update `docs/contracts.md`.

```python
# fetch_weather.py  (Member B)
get_weather_signal(route_id: str) -> dict
# {"value": 70,                 # 0 (calm) to 100 (very dangerous)
#  "detail": "wave height 4.2 m near waypoint 2",
#  "source_url": "https://...", "fetched_at": "2026-11-15T10:00:00Z",
#  "from_cache": False}

# fetch_news.py  (Member B)
get_news_signal(route_id: str) -> dict
# {"value": 55,                 # 0 (quiet) to 100 (many negative stories)
#  "detail": "story volume 3x normal, tone negative",
#  "source_url": "https://...", "fetched_at": "...", "from_cache": False}

# risk.py  (Member C)
score_route(route_id: str) -> dict
# {"route_id": "red_sea", "score": 82,           # 0 to 100
#  "reasons": [{"label": "Storm ahead", "points": 35},
#              {"label": "Port strike news", "points": 30},
#              {"label": "Seasonal queue", "points": 17}],
#  "confidence": "medium"}                       # "low", "medium" or "high"

# cost.py  (Member C)
compare_options(route_id: str, cargo_bbl: int, delay_days: float) -> dict
# {"wait_cost_per_bbl": 0.10, "reroute_extra_cost_per_bbl": 0.084,
#  "break_even_days": 4.2, "cheaper_option": "reroute",
#  "reroute_win_probability": None,              # a number 0 to 1 once simulation exists
#  "inr_per_usd": 83.0}

# optimizer.py  (Member D)
recommend_blend(disrupted_grade: str, limits: dict) -> dict
# {"blend": [{"grade": "Oman Export", "share": 0.6},
#            {"grade": "Bonny Light", "share": 0.4}],
#  "api": 33.0, "sulphur_pct": 0.9, "cost_per_bbl": 80.5,
#  "within_limits": True, "excluded": ["Supplier B (flagged)"]}

# compliance.py  (Member D)
screen(name: str) -> dict
# {"name": "Supplier A", "status": "cleared",    # "cleared" or "flagged"
#  "match": None, "match_score": 12, "source": "OFAC sanctions list"}
```

The risk score combines the signals like this: `risk = w1*news + w2*weather + w3*history`, where `w1`, `w2`, `w3` are weights that Member C stores in one clear place at the top of `risk.py`.

---

## 6. Set up on your laptop

```bash
git clone https://github.com/<owner>/crudeCompass.git
cd crudeCompass

# create a virtual environment (a private box of libraries for this project)
python -m venv .venv

# turn it on
#   Windows:       .venv\Scripts\activate
#   macOS / Linux: source .venv/bin/activate

pip install -r requirements.txt

# make your own secrets file (never commit it)
cp .env.example .env        # on Windows: copy .env.example .env

# run the dashboard
streamlit run app.py
```

Everyone uses the **same Python version** (agree on one, for example 3.11, and write it here: **[version]**).

## 7. How we use Git (every day)

```bash
git checkout main
git pull                              # get everyone's latest work
git checkout -b b-openmeteo-fetch     # your own branch, name starts with your letter
# ... work, then ...
git add .
git commit -m "Fetch wave height for one waypoint"
git push -u origin b-openmeteo-fetch
```

Then open a **pull request** on GitHub. The review partner reads it, runs it if possible, and merges. After a merge, everyone runs `git pull` on `main`.

**Rules**
1. Never work directly on `main`. `main` must always run.
2. Run `git pull` before you start each day.
3. Small commits with clear messages.
4. **Never commit `.env`, API keys, passwords or `.db` files.** If it happens, tell Arun immediately. The key must be cancelled and replaced; deleting the file is not enough.
5. One file, one owner.
6. Stuck for more than 2 hours? Ask the team.

## 8. Milestones

| Date | What must be true |
|---|---|
| 4 Nov | Tables and seed CSVs are ready (Arun) |
| 6 Nov | Stubs for all contracts are in the repo (Arun) |
| 8 Nov | Streamlit page shows stub answers |
| 13 Nov | First real weather and news values saved (Member B) |
| 15 Nov | Risk, cost, blend and sanctions functions work on seed data |
| **22 Nov** | **Milestone 1: one route works end to end on the dashboard with real weather and news** |
| 29 Nov | More routes, reasons, confidence, what-if controls |
| 6 Dec | Cleanup, README, deployed link |
| 7 Dec | **Feature freeze. No new features after this.** |
| 10 Dec | Final demo |

If we fall behind, we **cut features, not quality**. The must-have list is in section 2.

## 9. API notes (read before you code)

- Check each API's own documentation for limits, terms and parameters before writing code. Do not trust anyone's memory, including this README.
- As far as we know, **GDELT** throttles quick repeat requests and its easy search covers only about the last few months. Pause between requests and **cache** the results.
- Always save `source_url` and `fetched_at` with each real value. That is our proof of where the data came from.
- If an API fails, use the last saved result (set `from_cache` to `True`). The demo must never crash because the internet failed.
- Keep small saved sample replies in `data/` so we can test and demo offline.

## 10. Words you will hear

| Word | Meaning |
|---|---|
| **Stub** | A placeholder function with the right name and a fake answer in the right shape |
| **Contract** | The agreed name, inputs and output shape of a function |
| **Seed data** | Starting sample rows (CSV files) we load into the database once |
| **Schema** | The design of the database tables |
| **Branch** | Your own working copy of the project |
| **Pull request (PR)** | "Please review my branch and merge it into `main`" |
| **Demurrage** | The daily cost of a ship waiting idle |
| **Chokepoint** | A narrow sea passage that many ships must use |
| **Break-even delay** | The waiting time at which rerouting becomes cheaper than waiting |

## 11. Definition of "done" for any task

- It runs from a clean clone (nobody needs anything from your laptop).
- It follows the contract.
- Any assumed number is written in `docs/assumptions.md`.
- No secrets are committed.
- A teammate reviewed it.

---

*Team: Arun, [B], [C], [D]. Last updated: [date].*
