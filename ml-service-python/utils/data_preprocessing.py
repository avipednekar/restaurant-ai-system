import pandas as pd
import numpy as np
from datetime import datetime
import os

# Define expected data paths (can be overridden)
DEFAULT_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "Datasets"
)

def load_inventory_data(filepath=None):
    if filepath is None:
        filepath = os.path.join(DEFAULT_DATA_DIR, "restaurant_inventory_100days.csv")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Inventory dataset not found at {filepath}")
        
    df = pd.read_csv(filepath)
    return df

def preprocess_inventory_data(df):
    """
    Preprocess inventory data for the optimization model.
    """
    df = df.copy()
    
    # Convert date to datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        # Extract basic time features (useful for seasonality or trends if added later)
        df['DayOfWeek'] = df['Date'].dt.dayofweek
        df['Month'] = df['Date'].dt.month
        
    # Categorical encoding (simple label encoding for now, could use OneHot)
    cat_columns = ['Category', 'Subcategory', 'Unit', 'Supplier_Name']
    
    for col in cat_columns:
        if col in df.columns:
            df[col] = df[col].astype('category').cat.codes
            
    # Drop columns that are not useful for training directly or are unique identifiers
    drop_cols = ['Date', 'Item_Name']
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore')
    
    # Target variables could be 'Waste_Percentage' or we might want to predict 'Daily_Usage'
    # We will assume we want to predict 'Waste_Percentage' based on features
    
    # Fill any remaining NaNs
    df = df.fillna(0)
    
    return df

def load_sales_data(filepath=None):
    """
    Load the Balaji Fast Food Sales dataset for demand forecasting.
    """
    if filepath is None:
        filepath = os.path.join(DEFAULT_DATA_DIR, "Balaji Fast Food Sales.csv")
        
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Sales dataset not found at {filepath}")
        
    df = pd.read_csv(filepath)
    return df

def preprocess_sales_data(df):
    """
    Preprocess sales data for the demand forecasting model.
    Goal is to predict `quantity` based on item and temporal features.
    """
    df = df.copy()
    
    # Standardize column names to lowercase with underscores
    df.columns = [c.lower().replace(' ', '_') for c in df.columns]
    
    # The date column might be in different formats, e.g., '07-03-2022' or '8/23/2022'
    if 'date' in df.columns:
        # Convert date to datetime, robust to different formats
        df['date'] = pd.to_datetime(df['date'], format='mixed', dayfirst=False)
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
    # Encode categorical features
    cat_columns = ['item_name', 'item_type', 'transaction_type', 'received_by', 'time_of_sale']
    
    # We'll save the mapping for item_name to use during prediction
    item_name_mapping = {}
    
    for col in cat_columns:
        if col in df.columns:
            if col == 'item_name':
                # Create a specific mapping for items
                unique_items = df[col].unique()
                item_name_mapping = {item: idx for idx, item in enumerate(unique_items)}
                df[col] = df[col].map(item_name_mapping)
            else:
                df[col] = df[col].astype('category').cat.codes
                
    # Select features for training (e.g., predicting quantity)
    # Exclude order_id, date, and transaction_amount (since amount depends on quantity)
    drop_cols = ['order_id', 'date', 'transaction_amount']
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore')
    
    df = df.fillna(0)
    
    return df, item_name_mapping
