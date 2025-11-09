# Personal Financial Command Dashboard — **Technical Blueprint (Hybrid: Local-first + Cloud Sync)**

**Version:** 1.0  
**Date:** 2025-10-06  
**Owner:** Gaz (South Africa)  
**Target Users:** Non-finance individuals who want _simple, visual, automated_ money management.

---

## 0) Executive Summary

A local-first personal finance dashboard with optional cloud sync. Runs offline on a laptop/desktop (LAN) and syncs to Google Sheets/Drive when online. Data capture supports CSV imports, manual entries, and receipt OCR (SnapSlip-style). The system automates categorization, budgeting (50/30/20 default), savings goals, debt payoff, and forecasting. AI helpers provide plain-language insights, warnings, and “what-if” analysis (via LM Studio local models).

---

## 1) Product Goals & Success Criteria

**Primary Goals**
- Give users a single-pane-of-glass view of income, expenses, savings, debt and goals.
- Work flawlessly offline; sync automatically when online.
- Be understandable for non-financial users; minimize jargon.
- Automate repetitive tasks: imports, categorization, monthly rollovers, reports.

**Success Criteria (KPIs)**
- Setup < 20 minutes on Windows/Mac.
- Weekly review < 10 minutes.
- 95%+ auto-categorization accuracy after 2 weeks of use.
- “Time-to-first-report” < 5 minutes (sample data shipped).
- Net worth and savings goal tracking accurate within 1% of data sources.

---

## 2) System Requirements

**Local Runtime**
- Python 3.11+ (FastAPI or Flask)
- Node 18+ (Vite/React) _or_ pure HTML+JS build
- SQLite (default) with option to switch to DuckDB/Postgres

**Optional Cloud**
- Google Sheets & Drive API (service account / OAuth)
- Email/Push for weekly reports (SMTP or Pushover/Telegram bot)

**AI (Optional)**
- LM Studio local model (e.g., `qwen/qwen3-4b-thinking-2507`)
- OpenAI-compatible endpoint (local) for insights and planning

**OS**
- Windows 10+, macOS 12+, Linux modern distro

---

## 3) Architecture Overview

```
Local App (Offline-first)
┌─────────────────────────────────────────────────────────┐
│ Frontend (React/HTML) ←→ Backend API (FastAPI/Flask)   │
│                          │                              │
│                          ├─ DB Layer (SQLite)          │
│                          │   └─ /data/*.db             │
│                          │                              │
│                          ├─ Importers (CSV/Receipts)   │
│                          ├─ AI Insights (LM Studio)    │
│                          └─ Jobs Scheduler (APScheduler)│
└─────────────────────────────────────────────────────────┘
             │                  ▲
             ▼                  │
    Cloud Sync Adapter (when online)
             │
     Google Sheets / Drive
```

**Key Principles**
- **Local-first:** All core features work offline.
- **Event-sourced-ish:** Keep raw transaction history; derive summaries.
- **Idempotent sync:** Cloud sync never duplicates data.
- **Composable modules:** Importers, categorizer, reports are pluggable.

---

## 4) Data Model (Core Entities)

### 4.1 Entity Diagram (Logical)
```
User ──1─*── Account ──1─*── Transaction ──*─1── Category
                     └─1─*── Budget
User ──1─*── Goal (SavingsGoal)
User ──1─*── Debt (Liability)
ReportSnapshot (monthly) ⇐ derived from Transactions/Budgets
Settings (global, per user)
```

### 4.2 Tables / Schemas (SQLite)

#### `users`
- id (PK, uuid)
- name (text)
- currency (text, default: "ZAR")
- locale (text, default: "en-ZA")
- created_at (datetime)

#### `accounts`
- id (PK, uuid)
- user_id (FK users.id)
- name (text) — e.g., “Bills”, “Savings”, “Investments”
- type (text: "bank"|"cash"|"investment"|"virtual")
- opening_balance (numeric)
- is_active (bool)
- created_at (datetime)

#### `categories`
- id (PK, uuid)
- user_id (FK users.id)
- name (text) — e.g., “Rent”, “Groceries”
- group (text: "needs"|"wants"|"savings"|"debt"|"income")
- color (text) — hex
- is_system (bool) — defaults provided
- created_at (datetime)

#### `transactions`
- id (PK, uuid)
- user_id (FK users.id)
- account_id (FK accounts.id)
- category_id (FK categories.id, nullable)
- date (date)
- description (text)
- amount (numeric) — positive for income, negative for expense
- currency (text)
- source (text: "manual"|"csv"|"ocr"|"api")
- external_id (text, nullable) — for de-dup/sync
- tags (json)
- created_at (datetime)
- updated_at (datetime)

#### `budgets`
- id (PK, uuid)
- user_id (FK users.id)
- month (YYYY-MM) — e.g., "2025-10"
- category_id (FK categories.id)
- planned_amount (numeric)
- created_at (datetime)

#### `goals`
- id (PK, uuid)
- user_id (FK users.id)
- name (text) — "Emergency Fund"
- target_amount (numeric)
- target_date (date, nullable)
- linked_account_id (FK accounts.id, nullable)
- created_at (datetime)

#### `debts`
- id (PK, uuid)
- user_id (FK users.id)
- name (text)
- principal (numeric)
- apr_percent (numeric)
- min_payment (numeric)
- due_day (int 1–28)
- created_at (datetime)

#### `settings`
- id (PK, uuid)
- user_id (FK users.id)
- budget_rule (json) — default 50/30/20
- auto_categorize (bool)
- sync_google (bool)
- lm_studio_url (text)
- weekly_report_day (text: "SUN"|"MON"|...)
- created_at (datetime)

#### `reports`
- id (PK, uuid)
- user_id (FK users.id)
- month (YYYY-MM)
- net_income (numeric)
- savings_rate (numeric)
- spend_by_group (json)
- notes (text)
- created_at (datetime)

---

## 5) Default Categories & Budget Rule

**Groups:** `needs`, `wants`, `savings`, `debt`, `income`

**Seed Categories**
- Needs: Rent, Groceries, Transport, Utilities, Data/Airtime
- Wants: Eating Out, Entertainment, Subscriptions
- Savings: Emergency Fund, Goals
- Debt: Credit Card, Personal Loan
- Income: Salary, Freelance

**Budget Rule (50/30/20)**
```json
{{
  "needs": 0.50,
  "wants": 0.30,
  "savings": 0.20,
  "debt": 0.00
}}
```

---

## 6) File / Folder Structure

```
financial-dashboard/
├─ frontend/                     # React or pure HTML+JS
│  ├─ index.html
│  ├─ app.jsx                    # main app shell
│  ├─ components/
│  │  ├─ OverviewCards.jsx
│  │  ├─ BudgetBars.jsx
│  │  ├─ CashflowChart.jsx
│  │  ├─ TransactionsTable.jsx
│  │  ├─ GoalsPanel.jsx
│  │  ├─ DebtsPanel.jsx
│  │  ├─ ForecastPanel.jsx
│  │  └─ InsightsWidget.jsx
│  ├─ services/api.js
│  └─ styles.css
│
├─ backend/
│  ├─ app.py                     # FastAPI/Flask entry
│  ├─ db.py
│  ├─ models.py
│  ├─ routers/
│  │  ├─ transactions.py
│  │  ├─ budgets.py
│  │  ├─ goals.py
│  │  ├─ debts.py
│  │  ├─ reports.py
│  │  ├─ settings.py
│  │  └─ sync.py
│  ├─ services/
│  │  ├─ categorizer.py
│  │  ├─ importer_csv.py
│  │  ├─ importer_receipts.py    # OCR adapter
│  │  ├─ insights_ai.py
│  │  ├─ forecast.py
│  │  └─ sync_google.py
│  ├─ jobs/
│  │  ├─ scheduler.py
│  │  └─ weekly_report.py
│  ├─ util/
│  │  ├─ ids.py
│  │  └─ money.py
│  └─ .env.example
│
├─ data/
│  ├─ app.db
│  ├─ sample_transactions.csv
│  ├─ sample_categories.json
│  └─ sample_goals.json
│
├─ docs/
│  ├─ Financial_Dashboard_Blueprint.md
│  ├─ Setup_Instructions.md
│  └─ API_Contract.md
│
└─ scripts/
   ├─ seed.py
   └─ export_monthly_report.py
```

---

## 7) API Contract (REST, minimal)

**Base URL (local):** `http://localhost:8777/api`

### `GET /summary`
- Returns: balances, month-to-date totals, savings rate, net worth (if debts present), alerts.

### `GET /transactions?from=YYYY-MM-DD&to=YYYY-MM-DD&category_id=`
- Returns paginated transactions.

### `POST /transactions`
- Body: `{{date, amount, description, account_id, category_id?}}`

### `POST /import/csv`
- Multipart upload. Dedup by `(user_id, account_id, date, amount, description)` hash.

### `POST /categorize/run`
- Runs categorizer on uncategorized transactions.

### `GET /budgets/:month`
- Returns planned vs actual per category.

### `POST /budgets/:month`
- Upsert planned budgets.

### `GET /goals`
- List goals with progress.

### `POST /goals`
- Create/update goal.

### `GET /debts`
- List debts with payoff projections (avalanche).

### `POST /debts`
- Create/update debt.

### `GET /forecast/:month`
- Predict balance and overspend risk.

### `POST /reports/monthly/:YYYY-MM/generate`
- Generate + store monthly report snapshot.

### `POST /sync/google/run`
- Push/pull to Google Sheets/Drive if enabled.

---

## 8) Frontend Components (React)

- **OverviewCards**: KPIs: total balance, savings %, surplus, net worth.
- **BudgetBars**: Group bars (needs/wants/savings/debt) + category breakdown.
- **CashflowChart**: Line/area chart MTD.
- **TransactionsTable**: Filterable, CSV import button, quick-edit categories.
- **GoalsPanel**: Progress bars, ETA, “Boost Plan” calculator.
- **DebtsPanel**: Avalanche vs Snowball toggles, payoff timeline.
- **ForecastPanel**: Next month surplus, risk indicators, scenario slider.
- **InsightsWidget**: AI text feed: “You’re 12% under groceries YoY.”

**State Management:** lightweight (React Query or simple context + SWR).  
**Charts:** Recharts or Chart.js.  
**Offline Cache:** IndexedDB via `idb-keyval` if needed.

---

## 9) Core Services (Backend)

### 9.1 Categorizer
- Rules:
  - Merchant match (regex list)
  - Amount heuristics (recurring detection)
  - Description keywords
  - User-corrected memory (active learning, per user)
- Confidence score; low-confidence → “Needs review” queue.

### 9.2 Forecast
- Methods:
  - Rolling 3-month average for each category
  - Known recurring (rent, subscriptions) first
  - Monte-Carlo-lite jitter (±5–10%) for warnings
- Output: projected totals, risk flags (overspend probability).

### 9.3 Insights (AI)
- Prompts built from aggregated stats.
- Examples:
  - “Top 3 spending increases vs last month”
  - “Which category can I cut R300 without pain?”
  - “ETA to R15,000 emergency fund?”

### 9.4 Sync (Google)
- Sheets: `Transactions`, `Budgets`, `Goals`, `Debts`
- Idempotent: hash row id; upsert only changed rows.
- Conflict resolution: “local wins” by default (configurable).

---

## 10) Jobs & Automation

- **Weekly (SUN 17:00)**: Generate “Week-in-Review”; prompt AI summary; email/send.
- **Monthly (1st 08:00)**: Rollover budgets; generate monthly report.
- **Daily (19:00)**: Run categorizer on new transactions; check overspend alerts.
- **On-Import**: Deduplicate → categorize → recompute summaries → emit UI event.

Scheduler: APScheduler (background thread).

---

## 11) Security, Privacy, Backups

- Local DB encrypted at rest (use SQLCipher option) — optional.
- API auth: local JWT (single-user) or OS-loopback only (127.0.0.1).
- Backups: nightly copy of `app.db` to `/backups/YYYY-MM/` (keep 90 days).
- PII minimal; do not store full card numbers, only merchant names.
- Cloud sync uses least privilege service account; never upload raw DB.

---

## 12) Configuration (.env.example)

```
APP_PORT=8777
APP_HOST=127.0.0.1
APP_SECRET=change-me

CURRENCY=ZAR
LOCALE=en-ZA

USE_GOOGLE_SYNC=true
GOOGLE_CREDENTIALS_JSON=./secrets/google.json
GOOGLE_SHEETS_SPREADSHEET_ID=
GOOGLE_DRIVE_FOLDER_ID=

LM_STUDIO_URL=http://127.0.0.1:1234/v1
AI_MODEL=qwen/qwen3-4b-thinking-2507

WEEKLY_REPORT_DAY=SUN
WEEKLY_REPORT_HOUR=17
```

---

## 13) Sample Data & Seeds

- `data/sample_transactions.csv` (30 days mixed income/expense)
- `data/sample_categories.json` (default set + colors)
- `data/sample_goals.json` (Emergency Fund, Car Deposit)

Run:
```bash
python scripts/seed.py
```

---

## 14) Developer Tasks (MVP Checklist)

**Backend**
- [ ] Define models & migrations
- [ ] CRUD for transactions/budgets/goals/debts
- [ ] CSV importer with dedup
- [ ] Categorizer v1 (rules + memory)
- [ ] Forecast v1 + report snapshot
- [ ] Google sync adapter

**Frontend**
- [ ] Overview + KPIs
- [ ] Transactions table + filters + import
- [ ] Budget bars + edit planned
- [ ] Goals + progress + ETA
- [ ] Debts + payoff plan
- [ ] Forecast + insights widget

**Ops**
- [ ] .env scaffolding
- [ ] Scheduler (weekly/monthly/daily)
- [ ] Backup rotation
- [ ] Packaging for local run (one-liner script)

---

## 15) Example Prompts (AI Insights)

**Spend Change**
> “Compare this month-to-date vs the same period last month by category. Summarize top 3 increases and reasons based on merchant names. Output short bullet insights, include suggested caps.”

**Goal Planner**
> “Given Emergency Fund target R15,000 with R1,200/month contributions, compute ETA and suggest a boost plan to hit it 2 months earlier with minimal lifestyle impact.”

**Cut Finder**
> “Scan subscriptions and low-utility categories. Recommend R300–R600 in cuts with least disruption.”

---

## 16) Pseudocode Snippets

**Categorizer (simplified):**
```python
def categorize(tx, rules, memory):
    # priority: memory > merchant-rule > keyword > fallback
    if tx.external_id in memory: 
        return memory[tx.external_id]
    for rule in rules.merchants:
        if rule.regex.search(tx.description):
            return rule.category_id, 0.95
    for kw, cat in rules.keywords.items():
        if kw in tx.description.lower():
            return cat, 0.7
    return rules.default, 0.4  # needs review
```

**Forecast (rolling-average):**
```python
def forecast_month(transactions, month):
    hist = group_by_category(last_n_months(transactions, 3))
    recurring = detect_recurring(hist)
    proj = {c: avg(hist[c]) for c in hist}
    proj.update(recurring)  # override with known amounts
    risk = {c: jitter_risk(proj[c]) for c in proj}
    return proj, risk
```

**Google Sync (upsert):**
```python
def upsert_sheet(sheet, rows):
    for r in rows:
        key = r["hash_id"]
        if not sheet.exists(key) or sheet.changed(key, r):
            sheet.write(r)
```

---

## 17) UX Notes (Non-Technical)

- Language: simple (“Money in/out”), hide financial jargon.
- Visuals: progress bars, traffic-light budgets, friendly alerts.
- Defaults: 50/30/20 but editable per user.
- One-click “Add Expense” with smart suggestions.
- Mobile-responsive dashboard for quick checks.

---

## 18) Roadmap (Post-MVP)

- v1.1: Debt Snowball visualization; import bank OFX; multi-currency
- v1.2: Tax snapshot (estimate); scenario sandbox
- v1.3: Business Mode (separate namespaces); invoices overview
- v1.4: Mobile PWA; voice capture; receipt OCR baked-in

---

## 19) One-Liner Local Run (Dev)

```bash
# Backend (FastAPI example)
python -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn sqlalchemy pydantic apscheduler python-dotenv
uvicorn backend.app:app --host 127.0.0.1 --port 8777 --reload
```

```bash
# Frontend (Vite + React example)
npm create vite@latest frontend -- --template react
cd frontend && npm install && npm run dev
```

---

## 20) Acceptance Criteria (MVP Demo)

- Import CSV → transactions populate → categorizer runs → budgets update.
- Overview shows: total balance, savings rate, surplus, net worth.
- Create a Goal → see progress + ETA.
- Generate monthly report PDF/MD with top insights.
- Toggle “Offline Mode” and still fully usable.
- Reconnect online → run Google sync → no duplicates.

---

**End of Blueprint**  
