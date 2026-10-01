# Project FORESIGHT — Demand & Inventory Forecasting for NorthBay Living

This project was built for my Zidio Development internship. It helps a
(simulated) online store called **NorthBay Living** figure out two things
every week:

1. **How much of each product will we sell next?** (a forecast)
2. **Which products need action right now?** (reorder soon, or clear
out slow stock)

**🔗 Live dashboard:** https://fsrt4qxwwq6dlt3pnwjsyr.streamlit.app/

(<img width="1915" height="870" alt="image" src="https://github.com/user-attachments/assets/c3996bcd-7171-49ed-99b0-2b2b4bf9ca6f" />
)

---

## The Problem, In Simple Words

NorthBay was planning their stock by guessing. This caused two problems
happening at the same time:

- Popular products **ran out** — lost sales.
- Unpopular products **piled up** — money stuck in unsold stock.

This project builds a system that looks at their sales history and tells
them, product by product, what to do about it.

---

## What This Project Actually Does (Step by Step)

The project is built in 6 stages, and each stage produces something real:

### Stage 1 — Clean the Data

The raw sales/product/stock data was messy (missing values, duplicate
rows, inconsistent spelling). A script fixes all of that automatically,
so the data is trustworthy before anything else happens.

**File:** `src/pipeline.py`

### Stage 2 — Understand the Data (EDA)

Before building anything fancy, I looked at the cleaned data to find real
patterns: which products sell the most, which barely sell at all, whether
seasons affect demand, and whether promotions actually help. These
findings are written up in plain language.

**Files:** `notebook/01_eda.ipynb`, `reports/eda_insight_memo.md`

**What I found:**

- A small number of products account for most of the sales; a similar
number barely sell at all (dead stock).
- Winter sales are about 30% higher than Summer sales — demand is
seasonal, not flat.
- Promotions increase sales by about 50% on average — a real, useful
signal, not noise.

| Top vs. bottom sellers | Seasonality | Promotion effect |
| :---: | :---: | :---: |
| ![Product sales distribution](docs/screenshots/02_eda_sales_distribution.png) | ![Seasonality](docs/screenshots/03_eda_seasonality.png) | ![Promo lift](docs/screenshots/04_eda_promo_lift.png) |

### Stage 3 — Predict Future Demand (Forecasting)

This is the core of the project. I built a model that predicts how many
units of each product will sell next week.

**Important: I didn't just build a model and assume it works.** I first
built the simplest possible guess — "this week will look like the same
week last year" — and used that as the bar to beat. Only after the real
model beat that simple guess did I trust it.

**Result (measured honestly, on data the model never saw during training):**

| Approach                           | Error (WAPE — lower is better) |
| ---------------------------------- | ------------------------------ |
| Simple guess (last year's pattern) | 21.9%                          |
| Our model                          | **20.5%**                      |

The model wins, but the improvement is modest and I report that honestly
rather than exaggerating it.

![Forecast vs actual](docs/screenshots/05_forecast_vs_actual.png)

**File:** `notebook/02_forecast.ipynb`

### Stage 4 — Turn Predictions Into Action (Risk Scoring)

A forecast alone doesn't tell anyone what to do. So each product is
scored on two things:

- **Will it run out soon?** (Stockout risk)
- **Do we have way more than we'll sell?** (Overstock risk)

Based on those two scores, every product gets sorted into one of four
simple categories:

| Category           | Meaning              | What to do                  |
| ------------------ | -------------------- | --------------------------- |
| 🟢 Healthy          | Stock matches demand | Nothing — leave it alone    |
| 🔴 Reorder Now      | Will likely run out  | Order more stock soon       |
| 🔵 Markdown / Clear | Way too much stock   | Discount it or clear it out |
| 🟣 Watch / Volatile | Risky on both sides  | Look at it manually         |

**What we found:** Out of 203 products — 109 are healthy, 71 need
reordering (about **$1.74M in sales at risk** if ignored), and 23 are
overstocked (about **$539K locked up in unsold stock**).

![Risk quadrant](docs/screenshots/06_risk_quadrant.png)

**File:** `notebook/03_risk_scoring.ipynb`

### Stage 5 — Make It Usable (Dashboard)

All of the above lives in code and notebooks — useless to a non-technical
person. So I built a simple website (a dashboard) where anyone can:

- Filter products by category or risk type
- See a chart of which products are risky
- See a ready-made action list, sorted by dollar impact

**File:** `app/dashboard.py`
**Live link:** https://fsrt4qxwwq6dlt3pnwjsyr.streamlit.app/

| Filters & KPIs | Risk chart | Action list |
| :---: | :---: | :---: |
| ![Filters and KPIs](<img width="295" height="637" alt="image" src="https://github.com/user-attachments/assets/3dd2b54f-36d3-44eb-959a-0ed7e4bdc100" />)
| ![Risk chart](<img width="1566" height="572" alt="image" src="https://github.com/user-attachments/assets/5583df9c-51bf-4f98-bbd8-82a28d972287" />)
| ![Action list](<img width="1597" height="567" alt="image" src="https://github.com/user-attachments/assets/bc13f869-4989-4fcb-b1c8-38109b61fa19" />) |

### Stage 6 — Explain It To Non-Technical People

Finally, I put together a short slide deck for the Head of Operations
and Finance — leading with the dollar impact, explaining what the system
does, and being upfront about what it can't do yet.

**File:** `FORESIGHT_Executive_Readout.pptx`

![Executive readout slide](docs/screenshots/10_executive_readout.png)

---

## How To Run This Project Yourself

You need Python installed. Then, from the project folder:

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 2. Install the required packages
pip install -r requirements.txt

# 3. Generate the raw data
python src/generate_data.py

# 4. Clean and prepare it
python src/pipeline.py

# 5. Open the notebooks (in order) to see the analysis, forecasting,
#    and risk scoring:
#    notebook/01_eda.ipynb
#    notebook/02_forecast.ipynb
#    notebook/03_risk_scoring.ipynb

# 6. Run the dashboard
streamlit run app/dashboard.py
```

---

## Project Folder Guide

```
foresight/
  data/
    raw/            <- original (messy) data files
    processed/      <- cleaned data, ready for analysis
  notebook/
    01_eda.ipynb          <- finding patterns in the data
    02_forecast.ipynb     <- building and testing the forecast model
    03_risk_scoring.ipynb <- turning forecasts into action items
  reports/
    eda_insight_memo.md   <- written summary of key findings
    figures/              <- saved charts
  docs/
    screenshots/          <- images used in this README
  src/
    generate_data.py   <- creates the sample dataset
    pipeline.py        <- cleans and joins the data
  app/
    dashboard.py       <- the live dashboard (Streamlit)
  requirements.txt     <- list of packages needed to run this project
```

---

## Being Honest About Limitations

- The model is trained and tested on 2 years of historical data — it
should be checked again as new sales data comes in.
- Brand-new products (with little sales history) get less reliable
forecasts.
- The system doesn't place orders automatically — a person still
reviews and decides.
- Sudden, unusual spikes in demand can still catch the model off guard.
- The data is simulated, so real-world results will differ and need
re-validation on NorthBay's actual sales.

---

## Future Improvements

If I continue this project, here is what I would do next, roughly in
order of impact.

**Better forecasting**
- Try stronger models (LightGBM / XGBoost, Prophet, or a hybrid) and
compare them against the same "last year" baseline. The current gain
(21.9% → 20.5% WAPE) is modest, so there is room to improve.
- Add more features: holidays, price changes, competitor activity,
weather, and marketing calendar.
- Give a **prediction range** (e.g. "80–120 units") instead of a single
number, so risk scoring can use real uncertainty.
- Handle new products with a "cold-start" approach that borrows from
similar products in the same category.
- Do rolling-origin backtesting for a more reliable accuracy estimate.

**Smarter inventory decisions**
- Compute suggested **reorder quantities and reorder points**, using
supplier lead time, safety stock, and service-level targets, not just a
"reorder now" flag.
- Factor in holding cost, margin, and shelf life when deciding what to
mark down and by how much.
- Add what-if scenarios (e.g. "what if we run a 20% promo next month?").

**Dashboard & product**
- Add forecast charts per product (history + forecast + stock level) and
a search box.
- Add CSV/Excel export of the action list and email or Slack alerts for
high-risk items.
- Add user login and role-based views for Operations vs. Finance.
- Show a "last updated" time and data freshness warnings.

**Data & engineering**
- Connect to a real data source (database or API) instead of generated
files.
- Automate the weekly refresh (scheduled pipeline with GitHub Actions or
Airflow) and retrain the model on a schedule.
- Add model monitoring: track accuracy over time and alert on drift.
- Add unit tests for the pipeline, a CI workflow, and type
hints/linting.
- Package the code in a `Makefile` or Docker setup for one-command
reproducibility.

---

## Tools Used

Python, pandas, numpy, scikit-learn (for the forecasting model),
matplotlib (for charts), Streamlit (for the dashboard), Git/GitHub
(for version control).
