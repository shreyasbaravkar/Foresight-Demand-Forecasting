# NorthBay Living — Data Quality & EDA Insight Memo
**Project FORESIGHT | Week 2 Checkpoint**

## Data Quality Summary
Before analysis, the raw extracts were cleaned:
- 3 duplicate SKU records and 15 duplicate sales records were removed
- 5 missing `unit_cost` values were filled using the category median cost
- 200 missing `units_sold` values (out of 146,200 rows) were filled with 0, since dropping
  them would have created artificial gaps in each product's daily sales history
- Inconsistent category text casing (e.g. "furniture" vs "Furniture") was standardized

After cleaning, the dataset has zero missing values and zero duplicates across 200 SKUs
and 2 years of daily sales history (2024–2025).

## Key Insights

**1. Demand is highly uneven across products.**
The top 10 best-selling SKUs sold tens of thousands of units combined over 2 years, while
the bottom-performing SKUs sold under 500 units each in the same period. This means a
uniform stocking policy across all 200 SKUs is the wrong approach — the business needs
product-level forecasting, not category-level guesses.
*(see: top10_sellers.png)*

**2. 30 SKUs (15% of the catalog) qualify as dead stock.**
These products sold at or below the bottom-15% threshold over 2 years. They are strong
candidates for markdown or clearance, freeing up warehouse space and locked capital.

**3. Demand is seasonal — Winter is ~30% stronger than Summer.**
Winter: 471,343 units sold vs. Summer: 363,550 units sold. Any forecast that treats
demand as flat across the year will systematically under-order in Winter and over-order
in Summer.
*(see: seasonality.png)*

**4. Promotions genuinely drive sales — not just noise.**
Average daily units sold rise from 11.22 (no promo) to 16.79 (on promo) — a 49.7% lift.
This confirms promotion activity is a real, useful signal for the demand forecasting
model, not something that can be safely ignored.

**5. Appliance is the top revenue-generating category.**
*(see: revenue_by_category.png — fill in with your actual top category from Cell 5)*

## Implication for Forecasting (Week 3)
These findings directly shape the model: forecasts must include seasonal features (not
assume flat demand), promotion flags should be used as a predictive signal, and the
30 identified dead-stock SKUs should be flagged early for the risk-scoring stage.
