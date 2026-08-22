"""
FORESIGHT — synthetic data generator
Creates the 4 tables described in Appendix A of the brief:
  sales_daily, sku_master, calendar, inventory_snapshots

Deliberately includes real-world messiness (missing values, a few
duplicates, inconsistent category labels) because cleaning that is
part of the assignment.
"""

import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)  # fixed seed -> reproducible

OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
OUT_DIR.mkdir(parents=True, exist_ok=True)

N_SKUS = 200
START_DATE = pd.Timestamp("2024-01-01")
END_DATE = pd.Timestamp("2025-12-31")  # 2 years of history

CATEGORIES = {
    "Furniture": ["Chairs", "Tables", "Shelving", "Sofas"],
    "Decor": ["Wall Art", "Rugs", "Vases", "Candles"],
    "Appliances": ["Kitchen", "Cleaning", "Climate"],
    "Bedding": ["Sheets", "Pillows", "Comforters"],
}


def build_sku_master():
    rows = []
    for i in range(1, N_SKUS + 1):
        sku_id = f"SKU{i:04d}"
        category = RNG.choice(list(CATEGORIES.keys()))
        subcategory = RNG.choice(CATEGORIES[category])
        launch_offset = RNG.integers(0, (END_DATE - START_DATE).days - 30)
        launch_date = START_DATE + pd.Timedelta(days=int(launch_offset))
        unit_cost = round(RNG.uniform(5, 150), 2)
        margin = RNG.uniform(1.4, 2.6)
        list_price = round(unit_cost * margin, 2)
        rows.append([sku_id, category, subcategory, launch_date, unit_cost, list_price])

    df = pd.DataFrame(rows, columns=["sku_id", "category", "subcategory", "launch_date",
                                      "unit_cost", "list_price"])

    # inject messiness: inconsistent category capitalisation on a few rows
    messy_idx = RNG.choice(df.index, size=8, replace=False)
    df.loc[messy_idx, "category"] = df.loc[messy_idx, "category"].str.lower()

    # a couple of duplicate rows (common in real extracts)
    dupes = df.sample(3, random_state=1)
    df = pd.concat([df, dupes], ignore_index=True)

    # a few missing unit_cost values
    miss_idx = RNG.choice(df.index, size=5, replace=False)
    df.loc[miss_idx, "unit_cost"] = np.nan

    return df


def build_calendar():
    dates = pd.date_range(START_DATE, END_DATE, freq="D")
    df = pd.DataFrame({"date": dates})
    df["week"] = df["date"].dt.isocalendar().week
    df["month"] = df["date"].dt.month
    df["season"] = df["month"].map({12: "Winter", 1: "Winter", 2: "Winter",
                                     3: "Spring", 4: "Spring", 5: "Spring",
                                     6: "Summer", 7: "Summer", 8: "Summer",
                                     9: "Autumn", 10: "Autumn", 11: "Autumn"})
    # simple holiday flags (a few fixed dates per year)
    holiday_md = {(1, 1), (8, 15), (10, 2), (12, 25), (11, 12)}
    df["is_holiday"] = df["date"].apply(lambda d: (d.month, d.day) in holiday_md).astype(int)

    # promo events: sale windows a few times a year
    df["promo_event"] = None
    promo_windows = [
        ("2024-03-01", "2024-03-07", "Spring Sale"),
        ("2024-07-01", "2024-07-10", "Mid-Year Sale"),
        ("2024-11-20", "2024-11-30", "Festive Sale"),
        ("2025-03-01", "2025-03-07", "Spring Sale"),
        ("2025-07-01", "2025-07-10", "Mid-Year Sale"),
        ("2025-11-20", "2025-11-30", "Festive Sale"),
    ]
    for start, end, name in promo_windows:
        mask = (df["date"] >= start) & (df["date"] <= end)
        df.loc[mask, "promo_event"] = name

    return df


def build_sales_daily(sku_master, calendar):
    sku_ids = sku_master["sku_id"].unique()
    n_days = len(calendar)

    # assign each SKU a "popularity" tier -> base demand level
    popularity = RNG.choice(["best_seller", "steady", "slow_mover", "dead_stock"],
                             size=len(sku_ids), p=[0.15, 0.45, 0.25, 0.15])
    base_demand_map = {"best_seller": 25, "steady": 10, "slow_mover": 3, "dead_stock": 0.5}

    calendar_idx = calendar.set_index("date")
    all_rows = []

    for sku_id, pop in zip(sku_ids, popularity):
        base = base_demand_map[pop]
        # weekly seasonality: weekends higher
        weekday_mult = calendar["date"].dt.dayofweek.map(
            {0: 0.9, 1: 0.9, 2: 0.95, 3: 1.0, 4: 1.1, 5: 1.4, 6: 1.3}
        ).values
        # yearly seasonality (winter/festive boost for home goods)
        season_mult = calendar["season"].map(
            {"Winter": 1.2, "Spring": 1.0, "Summer": 0.85, "Autumn": 1.05}
        ).values
        promo_mult = np.where(calendar["promo_event"].notna(), 1.6, 1.0)
        holiday_mult = np.where(calendar["is_holiday"] == 1, 1.3, 1.0)

        trend = np.linspace(1.0, RNG.uniform(0.85, 1.25), n_days)  # slow drift up/down
        noise = RNG.normal(1.0, 0.25, n_days).clip(0.1, None)

        demand = base * weekday_mult * season_mult * promo_mult * holiday_mult * trend * noise
        units_sold = RNG.poisson(np.clip(demand, 0, None))

        price = sku_master.loc[sku_master["sku_id"] == sku_id, "list_price"].values[0]
        unit_price = np.where(calendar["promo_event"].notna(), round(price * 0.8, 2), price)
        revenue = units_sold * unit_price
        promo_flag = (calendar["promo_event"].notna()).astype(int).values

        sku_df = pd.DataFrame({
            "date": calendar["date"].values,
            "sku_id": sku_id,
            "units_sold": units_sold,
            "revenue": np.round(revenue, 2),
            "unit_price": unit_price,
            "promo_flag": promo_flag,
        })
        all_rows.append(sku_df)

    df = pd.concat(all_rows, ignore_index=True)

    # messiness: some missing units_sold (simulate export gaps)
    miss_idx = RNG.choice(df.index, size=200, replace=False)
    df.loc[miss_idx, "units_sold"] = np.nan

    # a handful of exact duplicate rows
    dupes = df.sample(15, random_state=2)
    df = pd.concat([df, dupes], ignore_index=True)

    return df


def build_inventory_snapshots(sku_master, calendar):
    # weekly snapshots (Mondays) rather than daily, per "periodic stock position"
    snap_dates = calendar[calendar["date"].dt.dayofweek == 0]["date"]
    rows = []
    for sku_id in sku_master["sku_id"].unique():
        on_hand = RNG.integers(20, 300)
        lead_time = int(RNG.integers(7, 30))
        reorder_point = int(RNG.integers(15, 60))
        for d in snap_dates:
            # random walk on stock level
            change = RNG.integers(-40, 25)
            on_hand = max(0, on_hand + change)
            on_order = RNG.integers(0, 50) if RNG.random() < 0.3 else 0
            rows.append([d, sku_id, on_hand, on_order, lead_time, reorder_point])

    df = pd.DataFrame(rows, columns=["date", "sku_id", "on_hand_units", "on_order_units",
                                      "lead_time_days", "reorder_point"])
    return df


def main():
    print("Generating sku_master...")
    sku_master = build_sku_master()
    print("Generating calendar...")
    calendar = build_calendar()
    print("Generating sales_daily (this takes a few seconds)...")
    sales_daily = build_sales_daily(sku_master, calendar)
    print("Generating inventory_snapshots...")
    inventory_snapshots = build_inventory_snapshots(sku_master, calendar)

    sku_master.to_csv(OUT_DIR / "sku_master.csv", index=False)
    calendar.to_csv(OUT_DIR / "calendar.csv", index=False)
    sales_daily.to_csv(OUT_DIR / "sales_daily.csv", index=False)
    inventory_snapshots.to_csv(OUT_DIR / "inventory_snapshots.csv", index=False)

    print("\nDone. Files written to:", OUT_DIR)
    for f in ["sku_master.csv", "calendar.csv", "sales_daily.csv", "inventory_snapshots.csv"]:
        path = OUT_DIR / f
        n_rows = sum(1 for _ in open(path)) - 1
        print(f"  {f}: {n_rows:,} rows")


if __name__ == "__main__":
    main()
