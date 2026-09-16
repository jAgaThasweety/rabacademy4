from pathlib import Path
import re

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


DATA_FILE = Path(__file__).with_name("clean_dataset.csv")

st.set_page_config(page_title="Retail Business Intelligence Dashboard", page_icon="R", layout="wide", initial_sidebar_state="expanded")


def normalize_name(value):
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def detect_columns(frame):
    aliases = {
        "revenue": ["calculatedsales", "sales", "revenue", "totalsales", "amount", "netsales", "saleamount"],
        "date": ["orderdate", "date", "transactiondate", "invoicedate", "salesdate"],
        "order_id": ["orderid", "order", "invoiceid", "transactionid", "ordernumber"],
        "customer_id": ["customerid", "customer_id", "customer", "customername", "clientid", "client"],
        "customer_segment": ["customersegment", "customer_segment", "segment"],
        "quantity": ["quantity", "qty", "units", "unitssold", "unitsold"],
        "price": ["unitprice", "unit_price", "price", "sellingprice", "unitcost"],
        "category": ["category", "productcategory", "productgroup"],
        "subcategory": ["subcategory", "subcategory", "productsubcategory"],
        "product": ["product", "productname", "item", "itemname", "sku"],
        "region": ["region", "territory", "salesregion"],
        "state": ["state", "province", "county"],
        "city": ["city", "town"],
        "payment_status": ["paymentstatus", "payment_status", "status"],
        "discount": ["discountpct", "discount_pct", "discount", "discountpercent", "discountrate"],
        "profit": ["profit", "grossprofit", "netprofit", "margin"],
        "marketing_spend": ["marketingspend", "marketingcost", "advertisingcost", "acquisitioncost", "adspend"],
        "acquired_customer": ["newcustomer", "newcustomers", "acquiredcustomer", "acquiredcustomers", "acquisitiondate"],
        "churn_date": ["churndate", "canceldate", "terminationdate", "inactivedate"],
        "latitude": ["latitude", "lat"],
        "longitude": ["longitude", "lon", "lng"],
    }
    normalized = {normalize_name(column): column for column in frame.columns}
    detected = {}
    for key, candidates in aliases.items():
        for candidate in candidates:
            match = normalized.get(normalize_name(candidate))
            if match:
                detected[key] = match
                break
    return detected


@st.cache_data(show_spinner=False)
def load_data(path):
    frame = pd.read_csv(path)
    return frame, detect_columns(frame)


def clean_data(frame, columns):
    data = frame.copy()
    if columns.get("date"):
        data["__date"] = pd.to_datetime(data[columns["date"]], errors="coerce")
        data["__year"] = data["__date"].dt.year.astype("Int64")
        data["__month"] = data["__date"].dt.month.astype("Int64")
        data["__month_name"] = data["__date"].dt.strftime("%B")
        data["__quarter"] = data["__date"].dt.quarter.astype("Int64")
    for derived_key, source in (
        ("__year", "order_date_year"),
        ("__month", "order_date_month"),
        ("__month_name", "order_date_month_name"),
        ("__quarter", "order_date_quarter"),
    ):
        if source in data.columns:
            data[derived_key] = data[source]
    for key in ("revenue", "quantity", "price", "discount", "profit", "marketing_spend"):
        if columns.get(key):
            data[columns[key]] = pd.to_numeric(data[columns[key]], errors="coerce")
    return data


def apply_filters(data, columns):
    filtered = data.copy()
    with st.sidebar:
        st.header("Filters")
        if "__year" in filtered:
            years = sorted(filtered["__year"].dropna().unique().tolist())
            selected_years = st.multiselect("Year", years, default=years)
            if selected_years:
                filtered = filtered[filtered["__year"].isin(selected_years)]
        if "__month" in filtered:
            selected_months = st.multiselect("Month", list(range(1, 13)), default=list(range(1, 13)), format_func=lambda value: pd.Timestamp(2024, value, 1).strftime("%B"))
            if selected_months:
                filtered = filtered[filtered["__month"].isin(selected_months)]
        for key, label in (("category", "Category"), ("customer_segment", "Customer Segment"), ("city", "City"), ("payment_status", "Payment Status"), ("subcategory", "Sub-category"), ("region", "Region"), ("state", "State")):
            source = columns.get(key)
            if source:
                values = sorted(filtered[source].dropna().astype(str).unique().tolist())
                selected = st.multiselect(label, values, default=values)
                if selected:
                    filtered = filtered[filtered[source].astype(str).isin(selected)]
        if "__date" in filtered and filtered["__date"].notna().any():
            valid_dates = filtered["__date"].dropna()
            date_range = st.date_input("Date range", (valid_dates.min().date(), valid_dates.max().date()))
            if isinstance(date_range, tuple) and len(date_range) == 2:
                filtered = filtered[filtered["__date"].dt.date.between(date_range[0], date_range[1])]
        st.divider()
        if st.button("Refresh data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    return filtered


def money(value):
    return "Not Available" if pd.isna(value) else f"${value:,.2f}"


def number(value):
    return "Not Available" if pd.isna(value) else f"{value:,.0f}"


def percent(value):
    return "Not Available" if pd.isna(value) else f"{value:,.2f}%"


def calculate_kpis(data, columns):
    revenue = data[columns["revenue"]].sum(min_count=1) if columns.get("revenue") else np.nan
    orders = data[columns["order_id"]].nunique() if columns.get("order_id") else len(data) if not data.empty else np.nan
    customers = data[columns["customer_id"]].nunique() if columns.get("customer_id") else np.nan
    segments = data[columns["customer_segment"]].nunique() if columns.get("customer_segment") else np.nan
    quantity = data[columns["quantity"]].sum(min_count=1) if columns.get("quantity") else np.nan
    profit = data[columns["profit"]].sum(min_count=1) if columns.get("profit") else np.nan
    unit_price = data[columns["price"]].mean() if columns.get("price") else np.nan
    discount = data[columns["discount"]].mean() if columns.get("discount") else np.nan
    return {
        "revenue": revenue,
        "orders": orders,
        "customers": customers,
        "segments": segments,
        "aov": revenue / orders if pd.notna(revenue) and orders else np.nan,
        "quantity": quantity,
        "profit": profit,
        "margin": profit / revenue * 100 if pd.notna(profit) and revenue else np.nan,
        "unit_price": unit_price,
        "discount": discount,
    }


def chart_empty(title, message="No data available for this view"):
    fig = px.scatter(title=title)
    fig.update_layout(template="plotly_white", annotations=[{"text": message, "showarrow": False, "xref": "paper", "yref": "paper", "x": 0.5, "y": 0.5}])
    return fig


def create_revenue_chart(data, columns):
    if not columns.get("revenue"):
        return chart_empty("Revenue Trend", "Revenue column not detected")
    if "__date" in data and data["__date"].notna().any():
        trend = data.dropna(subset=["__date"]).set_index("__date")[columns["revenue"]].resample("MS").sum().reset_index()
        fig = px.area(trend, x="__date", y=columns["revenue"], title="Revenue Trend", labels={"__date": "Date", columns["revenue"]: "Revenue"})
    else:
        trend = data.groupby(data.index // max(1, len(data) // 12))[columns["revenue"]].sum().reset_index(names="Period")
        fig = px.area(trend, x="Period", y=columns["revenue"], title="Revenue Trend")
    fig.update_traces(hovertemplate="%{x}<br>Revenue: $%{y:,.2f}<extra></extra>")
    return fig


def create_category_chart(data, columns):
    field = columns.get("category")
    if not field or not columns.get("revenue"):
        return chart_empty("Revenue by Category", "Category or revenue column not detected")
    grouped = data.groupby(field, dropna=False)[columns["revenue"]].sum().reset_index().sort_values(columns["revenue"], ascending=True)
    return px.bar(grouped, x=columns["revenue"], y=field, orientation="h", title="Revenue by Category", text_auto=".2s")


def create_region_chart(data, columns):
    field = columns.get("region") or columns.get("state") or columns.get("city")
    if not field or not columns.get("revenue"):
        return chart_empty("Revenue by Region", "Geographic or revenue column not detected")
    grouped = data.groupby(field, dropna=False)[columns["revenue"]].sum().reset_index().sort_values(columns["revenue"], ascending=True)
    return px.bar(grouped, x=columns["revenue"], y=field, orientation="h", title=f"Revenue by {field}", text_auto=".2s")


def create_geographic_chart(data, columns):
    field = columns.get("state") or columns.get("city") or columns.get("region")
    if not field or not columns.get("revenue"):
        return chart_empty("Geographic Performance", "State, city, region, or revenue data is unavailable")
    grouped = data.groupby(field, dropna=False)[columns["revenue"]].sum().reset_index().sort_values(columns["revenue"], ascending=False).head(20)
    return px.bar(grouped, x=field, y=columns["revenue"], title=f"Geographic Performance by {field}", text_auto=".2s")


def create_customer_chart(data, columns):
    field = columns.get("customer_segment")
    if not field or not columns.get("revenue"):
        return chart_empty("Customer Segment Analysis", "Customer segment or revenue data is unavailable")
    grouped = data.groupby(field, dropna=False)[columns["revenue"]].sum().reset_index().sort_values(columns["revenue"], ascending=True)
    return px.bar(grouped, x=columns["revenue"], y=field, orientation="h", title="Revenue by Customer Segment", text_auto=".2s")


def create_top_items_chart(data, columns):
    field = columns.get("product") or columns.get("subcategory") or columns.get("category")
    if not field or not columns.get("revenue"):
        return chart_empty("Top 10 Products / Sub-categories", "Product, sub-category, or revenue data is unavailable")
    grouped = data.groupby(field, dropna=False)[columns["revenue"]].sum().reset_index().nlargest(10, columns["revenue"]).sort_values(columns["revenue"])
    return px.bar(grouped, x=columns["revenue"], y=field, orientation="h", title=f"Top 10 {field}", text_auto=".2s")


def style_chart(fig):
    fig.update_layout(template="plotly_white", height=380, margin=dict(l=20, r=20, t=55, b=20), legend_title_text="")
    return fig


def main():
    st.markdown("""
    <style>
    .stApp { background: #f5f7fa; }
    [data-testid="stSidebar"] { background: #102a43; }
    [data-testid="stSidebar"] * { color: #f5f7fa; }
    .dashboard-title { font-size: 2.3rem; font-weight: 750; color: #102a43; margin-bottom: 0; }
    .dashboard-subtitle { color: #52606d; margin-top: 0.2rem; margin-bottom: 1.5rem; }
    div[data-testid="stMetric"] { background: white; border: 1px solid #d9e2ec; border-radius: 8px; padding: 14px 16px; box-shadow: 0 2px 8px rgba(16,42,67,.05); }
    h2, h3 { color: #102a43; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="dashboard-title">Retail Business Intelligence Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Interactive Sales, Customer & Regional Performance Analysis</div>', unsafe_allow_html=True)

    if not DATA_FILE.exists():
        st.error(f"clean_dataset.csv was not found. Place it in the same folder as app.py: {DATA_FILE}")
        st.stop()
    try:
        raw, columns = load_data(str(DATA_FILE))
        data = clean_data(raw, columns)
    except Exception as error:
        st.error(f"The dataset could not be loaded safely: {error}")
        st.stop()
    if not columns.get("revenue"):
        st.error("A revenue field was not detected. Expected calculated_sales or another recognized sales field.")
        st.info("Detected columns: " + ", ".join(map(str, raw.columns)))
        st.stop()

    filtered = apply_filters(data, columns)
    kpis = calculate_kpis(filtered, columns)
    st.caption(f"Showing {len(filtered):,} of {len(data):,} records | Detected fields: {', '.join(columns.values())}")

    first_row = st.columns(4)
    customer_label = "Total Customers" if columns.get("customer_id") else "Customer Segments"
    customer_value = number(kpis["customers"]) if columns.get("customer_id") else number(kpis["segments"])
    for column, label, value in zip(first_row, ["Total Revenue", "Total Orders", customer_label, "Average Order Value"], [money(kpis["revenue"]), number(kpis["orders"]), customer_value, money(kpis["aov"])]):
        column.metric(label, value)
    second_row = st.columns(4)
    for column, label, value in zip(second_row, ["Units Sold", "Average Unit Price", "Average Discount", "Total Profit"], [number(kpis["quantity"]), money(kpis["unit_price"]), percent(kpis["discount"]), money(kpis["profit"])]):
        column.metric(label, value)

    if not columns.get("customer_id"):
        st.info("Individual customer IDs are unavailable; Customer Segments is shown instead.")
    status_left, status_right = st.columns(2)
    with status_left:
        st.warning("CAC\n\nNot Available — acquisition cost data is not present")
    with status_right:
        st.warning("Churn Rate\n\nNot Available — customer lifecycle data is not present")

    st.subheader("Performance Overview")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(style_chart(create_revenue_chart(filtered, columns)), use_container_width=True)
    with right:
        st.plotly_chart(style_chart(create_category_chart(filtered, columns)), use_container_width=True)

    st.subheader("Regional and Customer Performance")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(style_chart(create_region_chart(filtered, columns)), use_container_width=True)
    with right:
        st.plotly_chart(style_chart(create_geographic_chart(filtered, columns)), use_container_width=True)

    st.subheader("Drill-down Analysis")
    drill_left, drill_right = st.columns(2)
    with drill_left:
        if columns.get("category"):
            category = st.selectbox("Category drill-down", ["All"] + sorted(filtered[columns["category"]].dropna().astype(str).unique().tolist()))
            drill_data = filtered if category == "All" else filtered[filtered[columns["category"]].astype(str) == category]
            drill_field = columns.get("subcategory") or columns.get("product") or columns.get("category")
            if drill_field and columns.get("revenue"):
                grouped = drill_data.groupby(drill_field)[columns["revenue"]].sum().reset_index().sort_values(columns["revenue"], ascending=False)
                st.plotly_chart(style_chart(px.bar(grouped, x=drill_field, y=columns["revenue"], title="Category to Sub-category")), use_container_width=True)
        else:
            st.info("Category drill-down unavailable.")
    with drill_right:
        geo_field = columns.get("region") or columns.get("state") or columns.get("city")
        if geo_field and columns.get("revenue"):
            grouped = filtered.groupby(geo_field)[columns["revenue"]].sum().reset_index().sort_values(columns["revenue"], ascending=False)
            st.plotly_chart(style_chart(px.bar(grouped, x=geo_field, y=columns["revenue"], title="Geographic Drill-down")), use_container_width=True)
        else:
            st.info("Geographic drill-down unavailable.")

    st.subheader("Customer and Order Analysis")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(style_chart(create_customer_chart(filtered, columns)), use_container_width=True)
    with right:
        st.plotly_chart(style_chart(create_top_items_chart(filtered, columns)), use_container_width=True)

    if columns.get("date"):
        st.subheader("Time Drill-down: Year to Month")
        monthly = filtered.dropna(subset=["__date"]).groupby(["__year", "__month", "__month_name"])[columns["revenue"]].sum().reset_index()
        if not monthly.empty:
            st.plotly_chart(style_chart(px.line(monthly, x="__month_name", y=columns["revenue"], color="__year", markers=True, title="Monthly Revenue by Year", category_orders={"__month_name": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]})), use_container_width=True)
        else:
            st.info("No valid dates remain after filtering.")
    else:
        st.info("Date information unavailable; time-based visualizations cannot be calculated.")


if __name__ == "__main__":
    main()