# Project FORESIGHT — Demand & Inventory Forecasting for NorthBay Living

This project was built for my Zidio Development internship. It helps a
(simulated) online store called **NorthBay Living** figure out two things
every week:

1. **How much of each product will we sell next?** (a forecast)
2. **Which products need action right now?** (reorder soon, or clear
   out slow stock)

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

The project is built in 4 stages, and each stage produces something real:

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

### Stage 3 — Predict Future Demand (Forecasting)
This is the core of the project. I built a model that predicts how many
units of each product will sell next week.

**Important: I didn't just build a model and assume it works.** I first
built the simplest possible guess — "this week will look like the same
week last year" — and used that as the bar to beat. Only after the real
model beat that simple guess did I trust it.

**Result (measured honestly, on data the model never saw during training):**
| Approach | Error (WAPE — lower is better) |
|---|---|
| Simple guess (last year's pattern) | 21.9% |
| Our model | **20.5%** |

The model wins, but the improvement is modest and I report that honestly
rather than exaggerating it.

**File:** `notebook/02_forecast.ipynb`

### Stage 4 — Turn Predictions Into Action (Risk Scoring)
A forecast alone doesn't tell anyone what to do. So each product is
scored on two things:
- **Will it run out soon?** (Stockout risk)
- **Do we have way more than we'll sell?** (Overstock risk)

Based on those two scores, every product gets sorted into one of four
simple categories:

| Category | Meaning | What to do |
|---|---|---|
| 🟢 Healthy | Stock matches demand | Nothing — leave it alone |
| 🔴 Reorder Now | Will likely run out | Order more stock soon |
| 🔵 Markdown / Clear | Way too much stock | Discount it or clear it out |
| 🟣 Watch / Volatile | Risky on both sides | Look at it manually |

**What we found:** Out of 203 products — 109 are healthy, 71 need
reordering (about **$1.74M in sales at risk** if ignored), and 23 are
overstocked (about **$539K locked up in unsold stock**).

**File:** `notebook/03_risk_scoring.ipynb`

### Stage 5 — Make It Usable (Dashboard)
All of the above lives in code and notebooks — useless to a non-technical
person. So I built a simple website (a dashboard) where anyone can:
- Filter products by category or risk type
- See a chart of which products are risky
- See a ready-made action list, sorted by dollar impact

**File:** `app/dashboard.py`
**Live link:** *(add your Streamlit Cloud URL here)*

### Stage 6 — Explain It To Non-Technical People
Finally, I put together a short slide deck for the Head of Operations
and Finance — leading with the dollar impact, explaining what the system
does, and being upfront about what it can't do yet.

**File:** `FORESIGHT_Executive_Readout.pptx`

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
    figures/               <- saved charts
  src/
    generate_data.py   <- creates the sample dataset
    pipeline.py         <- cleans and joins the data
  app/
    dashboard.py        <- the live dashboard (Streamlit)
  requirements.txt      <- list of packages needed to run this project
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

---

## Tools Used

Python, pandas, numpy, scikit-learn (for the forecasting model),
matplotlib (for charts), Streamlit (for the dashboard), Git/GitHub
(for version control).

---

*Built by Shreyas Baravkar for the Zidio Development internship —
Project FORESIGHT, Data Science & Analytics track.*
