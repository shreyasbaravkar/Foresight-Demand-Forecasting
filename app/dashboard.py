import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="FORESIGHT — NorthBay Living", layout="wide")

# ---- Load data ----
@st.cache_data
def load_data():
    risk_df = pd.read_csv("data/processed/risk_scores.csv")
    return risk_df

risk_df = load_data()

# ---- Header ----
st.title("📦 FORESIGHT — Demand & Inventory Dashboard")
st.caption("NorthBay Living | Planning view for Operations")

# ---- Sidebar filters ----
st.sidebar.header("Filters")
categories = st.sidebar.multiselect(
    "Category",
    options=sorted(risk_df["category"].dropna().unique()),
    default=sorted(risk_df["category"].dropna().unique())
)

zones = st.sidebar.multiselect(
    "Risk Zone",
    options=risk_df["risk_zone"].unique(),
    default=risk_df["risk_zone"].unique()
)

filtered = risk_df[
    risk_df["category"].isin(categories) &
    risk_df["risk_zone"].isin(zones)
]

# ---- KPI row ----
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total SKUs shown", len(filtered))
col2.metric("Reorder Now", (filtered["risk_zone"] == "Reorder Now").sum())
col3.metric("Markdown / Clear", (filtered["risk_zone"] == "Markdown / Clear").sum())
col4.metric("Revenue at Risk", f"${filtered['stockout_value_at_risk'].sum():,.0f}")

st.divider()

# ---- Decisioning grid chart ----
st.subheader("Stockout vs Overstock Risk — All SKUs")
fig = px.scatter(
    filtered,
    x="overstock_risk",
    y="stockout_risk",
    color="risk_zone",
    size="list_price",
    hover_data=["sku_id", "category", "expected_weekly_demand", "on_hand_units"],
    labels={"overstock_risk": "Overstock Risk", "stockout_risk": "Stockout Risk"},
    color_discrete_map={
        "Reorder Now": "#e03131",
        "Markdown / Clear": "#4C6EF5",
        "Watch / Volatile": "#f08c00",
        "Healthy": "#2f9e44",
    }
)
fig.add_hline(y=0.5, line_dash="dash", line_color="gray")
fig.add_vline(x=0.5, line_dash="dash", line_color="gray")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---- Prioritised action list ----
st.subheader("Prioritised Action List")
action_list = filtered[filtered["risk_zone"] != "Healthy"].copy()
action_list = action_list.sort_values("stockout_value_at_risk", ascending=False)

st.dataframe(
    action_list[["sku_id", "category", "risk_zone", "on_hand_units",
                 "expected_weekly_demand", "stockout_risk", "overstock_risk",
                 "stockout_value_at_risk", "overstock_value_at_risk"]],
    use_container_width=True,
    hide_index=True
)

if len(action_list) == 0:
    st.info("No SKUs need action with the current filters — everything is healthy.")