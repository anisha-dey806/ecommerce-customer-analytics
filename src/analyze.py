"""Reproducible starter analysis for the Olist e-commerce dataset."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

def load_csv(name):
    path = DATA / name
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path.name}. Download the Olist dataset from "
            "https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce "
            "and place the CSV in the data/ directory."
        )
    return pd.read_csv(path)

def main():
    orders = load_csv("olist_orders_dataset.csv")
    items = load_csv("olist_order_items_dataset.csv")
    customers = load_csv("olist_customers_dataset.csv")
    products = load_csv("olist_products_dataset.csv")
    translation = load_csv("product_category_name_translation.csv")
    reviews = load_csv("olist_order_reviews_dataset.csv")

    # Parse date fields explicitly.
    date_cols = [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_customer_date", "order_estimated_delivery_date"
    ]
    for col in date_cols:
        if col in orders.columns:
            orders[col] = pd.to_datetime(orders[col], errors="coerce")

    # Basic data quality report.
    quality = []
    for table_name, df in [
        ("orders", orders), ("items", items), ("customers", customers),
        ("products", products), ("reviews", reviews)
    ]:
        quality.append({
            "table": table_name,
            "rows": len(df),
            "duplicate_rows": int(df.duplicated().sum()),
            "columns_with_missing_values": int(df.isna().any().sum())
        })
    pd.DataFrame(quality).to_csv(REPORTS / "data_quality_summary.csv", index=False)

    # Order-level sales: aggregate item lines before joining to orders.
    order_items = (
        items.groupby("order_id", as_index=False)
        .agg(item_sales=("price", "sum"),
             freight_value=("freight_value", "sum"),
             item_count=("order_item_id", "count"))
    )
    order_summary = orders.merge(order_items, on="order_id", how="left")
    order_summary = order_summary.merge(
        customers[["customer_id", "customer_unique_id", "customer_state"]],
        on="customer_id", how="left"
    )
    order_summary["order_value_including_freight"] = (
        order_summary["item_sales"].fillna(0) +
        order_summary["freight_value"].fillna(0)
    )
    order_summary["purchase_month"] = (
        order_summary["order_purchase_timestamp"].dt.to_period("M").astype("string")
    )

    monthly = (
        order_summary.dropna(subset=["purchase_month"])
        .groupby("purchase_month", as_index=False)
        .agg(orders=("order_id", "nunique"),
             item_sales=("item_sales", "sum"),
             customers=("customer_unique_id", "nunique"))
    )
    monthly.to_csv(REPORTS / "monthly_trends.csv", index=False)

    delivered = order_summary[
        order_summary["order_status"].eq("delivered")
    ].copy()
    delivered["delivery_days"] = (
        delivered["order_delivered_customer_date"] -
        delivered["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400
    delivered["is_late"] = (
        delivered["order_delivered_customer_date"] >
        delivered["order_estimated_delivery_date"]
    )
    delivery_summary = pd.DataFrame([{
        "delivered_orders_with_valid_delivery_days": int(delivered["delivery_days"].notna().sum()),
        "average_delivery_days": delivered["delivery_days"].mean(),
        "median_delivery_days": delivered["delivery_days"].median(),
        "orders_with_estimate_and_actual": int(delivered["is_late"].notna().sum()),
        "late_delivery_rate": delivered["is_late"].mean()
    }])
    delivery_summary.to_csv(REPORTS / "delivery_summary.csv", index=False)

    # Category sales. Translate Portuguese category names where possible.
    product_categories = products.merge(
        translation, on="product_category_name", how="left"
    )
    category_items = items.merge(
        product_categories[["product_id", "product_category_name_english"]],
        on="product_id", how="left"
    )
    category_sales = (
        category_items.groupby("product_category_name_english", dropna=False, as_index=False)
        .agg(item_sales=("price", "sum"),
             items_sold=("order_item_id", "count"))
        .sort_values("item_sales", ascending=False)
    )
    category_sales.to_csv(REPORTS / "category_sales.csv", index=False)

    # Repeat-purchase analysis uses customer_unique_id to identify customers
    # across multiple customer_id records.
    customer_orders = (
        order_summary.dropna(subset=["customer_unique_id"])
        .groupby("customer_unique_id", as_index=False)
        .agg(distinct_orders=("order_id", "nunique"))
    )
    customer_orders["is_repeat_customer"] = customer_orders["distinct_orders"] > 1
    repeat_summary = pd.DataFrame([{
        "unique_customers": len(customer_orders),
        "repeat_customers": int(customer_orders["is_repeat_customer"].sum()),
        "repeat_customer_rate": customer_orders["is_repeat_customer"].mean()
    }])
    repeat_summary.to_csv(REPORTS / "repeat_customer_summary.csv", index=False)

    # Save a monthly trend plot for use in the report/dashboard.
    if not monthly.empty:
        sns.set_theme()
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(monthly["purchase_month"], monthly["orders"], marker="o")
        ax.set_title("Monthly Order Volume")
        ax.set_xlabel("Purchase month")
        ax.set_ylabel("Unique orders")
        ax.tick_params(axis="x", rotation=60)
        fig.tight_layout()
        fig.savefig(REPORTS / "monthly_order_volume.png", dpi=160)
        plt.close(fig)

    print(f"Analysis complete. Review generated files in: {REPORTS}")
    print("Validate the metrics and document findings before publishing conclusions.")

if __name__ == "__main__":
    main()
