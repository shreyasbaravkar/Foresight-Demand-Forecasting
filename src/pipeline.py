"""
FORESIGHT — data pipeline (Deliverable D1)

Ingests the 4 raw extracts, validates them, cleans known issues, and
produces one analysis-ready dataset joining sales + product + calendar
info at the (date, sku_id) grain.

Run: python3 src/pipeline.py
Output: data/processed/analysis_ready.csv
        data/processed/inventory_snapshots_clean.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------- 1. INGEST ----------
def load_raw():
    sku_master = pd.read_csv(RAW_DIR / "sku_master.csv", parse_dates=["launch_date"])
    calendar = pd.read_csv(RAW_DIR / "calendar.csv", parse_dates=["date"])
    sales_daily = pd.read_csv(RAW_DIR / "sales_daily.csv", parse_dates=["date"])
    inventory = pd.read_csv(RAW_DIR / "inventory_snapshots.csv", parse_dates=["date"])
    return sku_master, calendar, sales_daily, inventory


# ---------- 2. VALIDATE ----------
def profile(df, name):
    """Print a quick data-quality snapshot. This is what a data scientist
    checks before deciding how to clean — never clean blind."""
    print(f"\n--- {name} ---")
    print(f"rows: {len(df):,} | duplicate rows: {df.duplicated().sum():,}")
    nulls = df.isna().sum()
    nulls = nulls[nulls > 0]
    if len(nulls):
        print("nulls per column:\n", nulls.to_string())
    else:
        print("no nulls")


# ---------- 3. CLEAN ----------
def clean_sku_master(df):
    """
    Decisions & rationale:
    - Drop exact duplicate rows (same SKU listed twice is a data entry error).
    - Standardize category text casing ('furniture' -> 'Furniture') so the
      same category doesn't get split into two groups during analysis.
    - Fill missing unit_cost with the median cost *within the same category*
      (more accurate than a single global median, since costs vary a lot
      by category).
    """
    df = df.drop_duplicates().copy()
    df["category"] = df["category"].str.strip().str.title()
    df["subcategory"] = df["subcategory"].str.strip().str.title()

    df["unit_cost"] = df.groupby("category")["unit_cost"].transform(
        lambda s: s.fillna(s.median())
    )
    return df


def clean_sales_daily(df):
    """
    Decisions & rationale:
    - Drop exact duplicate rows (same SKU + date + units repeated = export glitch).
    - Missing units_sold: fill with 0 rather than dropping the row. Dropping
      would silently remove a day from that SKU's history and distort a
      time series model (it would look like a gap that never existed).
      We also keep a flag column so this assumption is auditable, not hidden.
    - Negative units_sold (if any) are clipped to 0 -- can't sell negative
      units; likely a returns/adjustment artifact outside our scope.
    """
    df = df.drop_duplicates().copy()

    df["units_sold_was_missing"] = df["units_sold"].isna().astype(int)
    df["units_sold"] = df["units_sold"].fillna(0)
    df["units_sold"] = df["units_sold"].clip(lower=0)

    return df


def clean_calendar(df):
    df = df.drop_duplicates(subset=["date"]).copy()
    # "No Promo" instead of the string "None" -- pandas re-reads a literal
    # "None" from CSV as a null again, which silently undoes this fillna
    # the next time the file is loaded. Use an unambiguous label instead.
    df["promo_event"] = df["promo_event"].fillna("No Promo")
    return df


def clean_inventory(df):
    df = df.drop_duplicates().copy()
    # negative stock isn't physically possible
    df["on_hand_units"] = df["on_hand_units"].clip(lower=0)
    df["on_order_units"] = df["on_order_units"].clip(lower=0)
    return df


# ---------- 4. UNIFY ----------
def build_analysis_ready(sku_master, calendar, sales_daily):
    """
    Join sales_daily (fact table) with sku_master and calendar (dimensions)
    on their keys, exactly as the star schema in the brief (Fig. 2) describes:
      sales_daily.sku_id  -> sku_master.sku_id
      sales_daily.date    -> calendar.date
    """
    df = sales_daily.merge(sku_master, on="sku_id", how="left")
    df = df.merge(calendar, on="date", how="left")

    # sanity check: every sales row should now have a category (no orphan SKUs)
    unmatched = df["category"].isna().sum()
    if unmatched:
        print(f"WARNING: {unmatched} sales rows didn't match a sku_master record")

    df = df.sort_values(["sku_id", "date"]).reset_index(drop=True)
    return df


def main():
    print("Loading raw extracts...")
    sku_master, calendar, sales_daily, inventory = load_raw()

    print("\n=== BEFORE CLEANING: data-quality profile ===")
    profile(sku_master, "sku_master")
    profile(sales_daily, "sales_daily")
    profile(calendar, "calendar")
    profile(inventory, "inventory_snapshots")

    print("\nCleaning...")
    sku_master_c = clean_sku_master(sku_master)
    sales_daily_c = clean_sales_daily(sales_daily)
    calendar_c = clean_calendar(calendar)
    inventory_c = clean_inventory(inventory)

    print("\n=== AFTER CLEANING: data-quality profile ===")
    profile(sku_master_c, "sku_master (clean)")
    profile(sales_daily_c, "sales_daily (clean)")

    print("\nJoining into analysis-ready dataset...")
    analysis_ready = build_analysis_ready(sku_master_c, calendar_c, sales_daily_c)

    out_path = OUT_DIR / "analysis_ready.csv"
    analysis_ready.to_csv(out_path, index=False)
    inventory_c.to_csv(OUT_DIR / "inventory_snapshots_clean.csv", index=False)

    print(f"\nDone.")
    print(f"  {out_path}  ({len(analysis_ready):,} rows, {analysis_ready.shape[1]} columns)")
    print(f"  {OUT_DIR / 'inventory_snapshots_clean.csv'}  ({len(inventory_c):,} rows)")


if __name__ == "__main__":
    main()
