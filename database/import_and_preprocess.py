"""
import_and_preprocess.py
========================
Phase 1 - Data Architecture & Preprocessing Pipeline

This script:
1. Reads the 3 provided CSV datasets
2. Cleans, normalizes, and standardizes data
3. Engineers ML features (day_of_week, is_weekend, lag features, etc.)
4. Loads BOM mapping from bom_mapping.csv
5. Inserts all data into MySQL tables via SQLAlchemy

Usage:
    python import_and_preprocess.py

Prerequisites:
    - MySQL running with `restaurant_ai_db` database created (run schema.sql first)
    - pip install pandas numpy sqlalchemy pymysql python-dotenv
"""

import os
import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_PORT = os.getenv("MYSQL_PORT", "3306")
DB_NAME = os.getenv("MYSQL_DB", "restaurant_ai_db")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Dataset paths (relative to this script)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATASETS_DIR = PROJECT_ROOT.parent / "Datasets"

SALES_DATA_CSV = DATASETS_DIR / "9. Sales-Data-Analysis.csv"
BALAJI_CSV = DATASETS_DIR / "Balaji Fast Food Sales.csv"
INVENTORY_CSV = DATASETS_DIR / "restaurant_inventory_100days.csv"
BOM_CSV = SCRIPT_DIR / "bom_mapping.csv"


def get_engine():
    """Create and return a SQLAlchemy engine."""
    engine = create_engine(DATABASE_URL, echo=False)
    # Test connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("[OK] Database connection established.")
    return engine


# ============================================================
# STEP 1: CLEAN & LOAD SALES DATA (9. Sales-Data-Analysis.csv)
# ============================================================
def clean_sales_data(filepath: Path) -> pd.DataFrame:
    """
    Clean the Western Fast Food sales data.
    - Standardize date format to YYYY-MM-DD
    - Clean whitespace in columns
    - Resolve decimal quantities -> integer
    """
    print(f"\n[1/6] Loading Sales Data: {filepath.name}")
    df = pd.read_csv(filepath)

    # Strip whitespace from all string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # Standardize date: DD-MM-YYYY -> YYYY-MM-DD
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", dayfirst=True)

    # Quantity is float (e.g. 573.07) — these appear to be revenue figures
    # Price * Quantity should = Revenue, but Quantity column has large decimal values
    # Based on analysis, the "Quantity" column actually represents revenue/sales amount
    # We'll rename to clarify and compute actual unit count
    df.rename(columns={"Quantity": "Revenue"}, inplace=True)
    df["Revenue"] = df["Revenue"].round(2)

    # Compute approximate unit quantity from Revenue / Price
    df["EstimatedQty"] = (df["Revenue"] / df["Price"]).round().astype(int)
    df["EstimatedQty"] = df["EstimatedQty"].clip(lower=1)

    # Clean Purchase Type and Payment Method
    df["Purchase Type"] = df["Purchase Type"].str.strip()
    df["Payment Method"] = df["Payment Method"].str.strip()
    df["Manager"] = df["Manager"].str.strip()

    print(f"   -> {len(df)} records loaded. Date range: {df['Date'].min()} to {df['Date'].max()}")
    return df


# ============================================================
# STEP 2: CLEAN & LOAD BALAJI FAST FOOD SALES
# ============================================================
def clean_balaji_data(filepath: Path) -> pd.DataFrame:
    """
    Clean the Indian Fast Food (Balaji) sales data.
    - Standardize mixed date formats
    - Impute missing transaction_type values
    - Map time_of_sale to standardized periods
    """
    print(f"\n[2/6] Loading Balaji Sales Data: {filepath.name}")
    df = pd.read_csv(filepath)

    # Strip whitespace
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # Standardize date - mixed formats: DD-MM-YYYY and M/DD/YYYY
    df["date"] = pd.to_datetime(df["date"], format="mixed", dayfirst=True)

    # Impute missing transaction_type with the mode
    mode_txn = df["transaction_type"].mode()[0] if not df["transaction_type"].mode().empty else "Cash"
    df["transaction_type"] = df["transaction_type"].fillna(mode_txn)

    # Impute missing received_by
    df["received_by"] = df["received_by"].fillna("Unknown")

    # Standardize time_of_sale values
    time_map = {
        "Morning": "Morning",
        "Afternoon": "Afternoon",
        "Evening": "Evening",
        "Night": "Night",
        "Midnight": "Midnight",
    }
    df["time_of_sale"] = df["time_of_sale"].map(time_map).fillna("Unknown")

    print(f"   -> {len(df)} records loaded. Date range: {df['date'].min()} to {df['date'].max()}")
    return df


# ============================================================
# STEP 3: CLEAN & LOAD INVENTORY DATA
# ============================================================
def clean_inventory_data(filepath: Path) -> pd.DataFrame:
    """
    Clean the 100-day restaurant inventory data.
    - Parse dates
    - Validate numeric ranges
    """
    print(f"\n[3/6] Loading Inventory Data: {filepath.name}")
    df = pd.read_csv(filepath)

    df["Date"] = pd.to_datetime(df["Date"])

    # Ensure numeric columns are clean
    numeric_cols = [
        "Current_Stock", "Reorder_Level", "Daily_Usage",
        "Lead_Time", "Price_per_Unit", "Seasonal_Factor", "Waste_Percentage",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Clip waste percentage to 0-100
    df["Waste_Percentage"] = df["Waste_Percentage"].clip(0, 100)

    # Clip seasonal factor to reasonable range
    df["Seasonal_Factor"] = df["Seasonal_Factor"].clip(0.5, 2.0)

    print(f"   -> {len(df)} records loaded. Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"   -> {df['Item_Name'].nunique()} unique ingredients tracked")
    return df


# ============================================================
# STEP 4: LOAD BOM MAPPING
# ============================================================
def load_bom_mapping(filepath: Path) -> pd.DataFrame:
    """Load the Bill of Materials mapping CSV."""
    print(f"\n[4/6] Loading BOM Mapping: {filepath.name}")
    df = pd.read_csv(filepath)
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    print(f"   -> {len(df)} ingredient mappings for {df['RecipeName'].nunique()} menu items")
    return df


# ============================================================
# STEP 5: FEATURE ENGINEERING
# ============================================================
def engineer_features(sales_df: pd.DataFrame, source: str) -> pd.DataFrame:
    """
    Engineer ML features from a sales dataframe.
    Adds: day_of_week, is_weekend, month, lag features, rolling averages.
    """
    print(f"\n[5/6] Engineering features for {source}...")

    if source == "sales_data":
        date_col, item_col, qty_col, price_col = "Date", "Product", "EstimatedQty", "Price"
    else:
        date_col, item_col, qty_col, price_col = "date", "item_name", "quantity", "item_price"

    features_list = []
    for item_name, group in sales_df.groupby(item_col):
        g = group.sort_values(date_col).copy()

        # Aggregate daily sales per item
        daily = g.groupby(date_col).agg(
            quantity_sold=(qty_col, "sum"),
            revenue=(qty_col, lambda x: (x * g.loc[x.index, price_col]).sum()) if source != "sales_data"
            else (qty_col, "sum"),
        ).reset_index()

        if source == "sales_data":
            daily["revenue"] = g.groupby(date_col)["Revenue"].sum().values

        daily.rename(columns={date_col: "sale_date"}, inplace=True)
        daily["item_name"] = item_name
        daily["price"] = g[price_col].iloc[0]

        # Temporal features
        daily["day_of_week"] = daily["sale_date"].dt.dayofweek
        daily["is_weekend"] = daily["day_of_week"].isin([5, 6]).astype(int)
        daily["month"] = daily["sale_date"].dt.month

        # Lag features
        daily["lag_1_day"] = daily["quantity_sold"].shift(1)
        daily["lag_7_day"] = daily["quantity_sold"].shift(7)

        # Rolling average
        daily["rolling_avg_7"] = daily["quantity_sold"].rolling(window=7, min_periods=1).mean().round(2)

        # Festival flag (placeholder - will be filled from festivals table later)
        daily["is_festival"] = False

        features_list.append(daily)

    result = pd.concat(features_list, ignore_index=True)
    print(f"   -> {len(result)} feature records generated for {result['item_name'].nunique()} items")
    return result


# ============================================================
# STEP 6: INSERT INTO DATABASE
# ============================================================
def insert_menu_items(engine, sales_df, balaji_df):
    """Insert unique menu items from both datasets."""
    print("\n[6/6] Inserting into database...")

    # Collect unique items from Sales Data
    items_sales = sales_df[["Product", "Price"]].drop_duplicates("Product")
    items_sales.columns = ["item_name", "price"]
    items_sales["category"] = "Western Fast Food"
    items_sales["item_type"] = items_sales["item_name"]
    items_sales["subcategory"] = None
    items_sales["is_available"] = True

    # Collect unique items from Balaji
    items_balaji = balaji_df[["item_name", "item_type", "item_price"]].drop_duplicates("item_name")
    items_balaji.columns = ["item_name", "item_type", "price"]
    items_balaji["category"] = "Indian Fast Food"
    items_balaji["subcategory"] = None
    items_balaji["is_available"] = True

    all_items = pd.concat([items_sales, items_balaji], ignore_index=True)
    all_items = all_items.drop_duplicates("item_name")

    all_items[["item_name", "category", "subcategory", "item_type", "price", "is_available"]].to_sql(
        "menu_items", engine, if_exists="append", index=False
    )
    print(f"   -> Inserted {len(all_items)} menu items")
    return all_items


def insert_orders_sales_data(engine, df: pd.DataFrame):
    """Insert orders from the Western Sales Data."""
    orders_data = []
    order_items_data = []

    # Get menu item ID mapping
    with engine.connect() as conn:
        menu_items = pd.read_sql("SELECT id, item_name FROM menu_items", conn)
    item_id_map = dict(zip(menu_items["item_name"], menu_items["id"]))

    for _, row in df.iterrows():
        orders_data.append({
            "order_date": row["Date"].strftime("%Y-%m-%d"),
            "time_of_sale": None,
            "total_amount": round(float(row["Revenue"]), 2),
            "payment_method": row["Payment Method"],
            "purchase_type": row["Purchase Type"],
            "manager_name": row["Manager"],
            "city": row["City"],
        })

    orders_df = pd.DataFrame(orders_data)
    orders_df.to_sql("orders", engine, if_exists="append", index=False)

    # Get order IDs for order_items
    with engine.connect() as conn:
        order_ids = pd.read_sql("SELECT id FROM orders ORDER BY id", conn)

    start_id = order_ids["id"].iloc[-len(df)]
    for i, (_, row) in enumerate(df.iterrows()):
        menu_id = item_id_map.get(row["Product"])
        if menu_id:
            order_items_data.append({
                "order_id": int(start_id + i),
                "menu_item_id": int(menu_id),
                "quantity": int(row["EstimatedQty"]),
                "unit_price": float(row["Price"]),
                "subtotal": round(float(row["Revenue"]), 2),
            })

    if order_items_data:
        pd.DataFrame(order_items_data).to_sql("order_items", engine, if_exists="append", index=False)
    print(f"   -> Inserted {len(orders_data)} orders (Sales Data)")


def insert_orders_balaji(engine, df: pd.DataFrame):
    """Insert orders from the Balaji Fast Food Data."""
    with engine.connect() as conn:
        menu_items = pd.read_sql("SELECT id, item_name FROM menu_items", conn)
    item_id_map = dict(zip(menu_items["item_name"], menu_items["id"]))

    orders_data = []
    order_items_data = []

    for _, row in df.iterrows():
        orders_data.append({
            "order_date": row["date"].strftime("%Y-%m-%d"),
            "time_of_sale": row["time_of_sale"],
            "total_amount": float(row["transaction_amount"]),
            "payment_method": row["transaction_type"],
            "purchase_type": "In-store",
            "manager_name": row.get("received_by", None),
        })

    orders_df = pd.DataFrame(orders_data)
    orders_df.to_sql("orders", engine, if_exists="append", index=False)

    with engine.connect() as conn:
        order_ids = pd.read_sql("SELECT id FROM orders ORDER BY id", conn)

    start_id = order_ids["id"].iloc[-len(df)]
    for i, (_, row) in enumerate(df.iterrows()):
        menu_id = item_id_map.get(row["item_name"])
        if menu_id:
            order_items_data.append({
                "order_id": int(start_id + i),
                "menu_item_id": int(menu_id),
                "quantity": int(row["quantity"]),
                "unit_price": float(row["item_price"]),
                "subtotal": float(row["transaction_amount"]),
            })

    if order_items_data:
        pd.DataFrame(order_items_data).to_sql("order_items", engine, if_exists="append", index=False)
    print(f"   -> Inserted {len(orders_data)} orders (Balaji Data)")


def insert_inventory(engine, df: pd.DataFrame):
    """Insert inventory records."""
    inv_data = df.rename(columns={
        "Date": "record_date",
        "Item_ID": "item_id",
        "Item_Name": "item_name",
        "Category": "category",
        "Subcategory": "subcategory",
        "Unit": "unit",
        "Current_Stock": "current_stock",
        "Reorder_Level": "reorder_level",
        "Daily_Usage": "daily_usage",
        "Lead_Time": "lead_time_days",
        "Price_per_Unit": "price_per_unit",
        "Supplier_Name": "supplier_name",
        "Seasonal_Factor": "seasonal_factor",
        "Waste_Percentage": "waste_pct",
    })

    inv_data.to_sql("inventory", engine, if_exists="append", index=False)
    print(f"   -> Inserted {len(inv_data)} inventory records")


def insert_bom(engine, bom_df: pd.DataFrame):
    """Insert BOM recipe mappings."""
    with engine.connect() as conn:
        menu_items = pd.read_sql("SELECT id, item_name FROM menu_items", conn)
    item_id_map = dict(zip(menu_items["item_name"], menu_items["id"]))

    bom_records = []
    for _, row in bom_df.iterrows():
        menu_id = item_id_map.get(row["RecipeName"])
        if menu_id:
            bom_records.append({
                "menu_item_id": int(menu_id),
                "ingredient_name": row["IngredientName"],
                "quantity_needed": float(row["Quantity"]),
                "unit": row["Unit"],
                "ingredient_category": row["IngredientCategory"],
            })

    if bom_records:
        pd.DataFrame(bom_records).to_sql("recipe_master", engine, if_exists="append", index=False)
    print(f"   -> Inserted {len(bom_records)} BOM recipe mappings")


def insert_ml_features(engine, features_df: pd.DataFrame):
    """Insert ML feature records."""
    with engine.connect() as conn:
        menu_items = pd.read_sql("SELECT id, item_name FROM menu_items", conn)
    item_id_map = dict(zip(menu_items["item_name"], menu_items["id"]))

    records = []
    for _, row in features_df.iterrows():
        menu_id = item_id_map.get(row["item_name"])
        if menu_id:
            records.append({
                "menu_item_id": int(menu_id),
                "sale_date": row["sale_date"].strftime("%Y-%m-%d"),
                "day_of_week": int(row["day_of_week"]),
                "is_weekend": bool(row["is_weekend"]),
                "month": int(row["month"]),
                "quantity_sold": int(row["quantity_sold"]),
                "revenue": float(row.get("revenue", 0)),
                "lag_1_day": int(row["lag_1_day"]) if pd.notna(row["lag_1_day"]) else None,
                "lag_7_day": int(row["lag_7_day"]) if pd.notna(row["lag_7_day"]) else None,
                "rolling_avg_7": float(row["rolling_avg_7"]) if pd.notna(row["rolling_avg_7"]) else None,
                "is_festival": bool(row["is_festival"]),
                "price": float(row["price"]),
            })

    if records:
        pd.DataFrame(records).to_sql("ml_features", engine, if_exists="append", index=False)
    print(f"   -> Inserted {len(records)} ML feature records")


# ============================================================
# MAIN PIPELINE
# ============================================================
def main():
    print("=" * 60)
    print("RESTAURANT AI SYSTEM - DATA PREPROCESSING PIPELINE")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Verify files exist
    for f in [SALES_DATA_CSV, BALAJI_CSV, INVENTORY_CSV, BOM_CSV]:
        if not f.exists():
            print(f"[ERROR] File not found: {f}")
            sys.exit(1)

    # Step 1-4: Clean & Load datasets
    sales_df = clean_sales_data(SALES_DATA_CSV)
    balaji_df = clean_balaji_data(BALAJI_CSV)
    inventory_df = clean_inventory_data(INVENTORY_CSV)
    bom_df = load_bom_mapping(BOM_CSV)

    # Step 5: Feature Engineering
    features_sales = engineer_features(sales_df, "sales_data")
    features_balaji = engineer_features(balaji_df, "balaji")

    # Step 6: Insert into database
    engine = get_engine()

    insert_menu_items(engine, sales_df, balaji_df)
    insert_orders_sales_data(engine, sales_df)
    insert_orders_balaji(engine, balaji_df)
    insert_inventory(engine, inventory_df)
    insert_bom(engine, bom_df)

    # Combine features and insert
    all_features = pd.concat([features_sales, features_balaji], ignore_index=True)
    insert_ml_features(engine, all_features)

    # Verification
    print("\n" + "=" * 60)
    print("VERIFICATION - Table Row Counts")
    print("=" * 60)
    with engine.connect() as conn:
        tables = ["menu_items", "orders", "order_items", "inventory", "recipe_master", "ml_features"]
        for table in tables:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"   {table:20s} -> {count:,} rows")

    print(f"\n[DONE] Pipeline completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
