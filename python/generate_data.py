import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

NUM_RECORDS = 5000
RANDOM_SEED = 42

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "retail_transactions.csv"


# ---------------------------------------------------------
# Reference data
# ---------------------------------------------------------

regions = [
    "North",
    "South",
    "East",
    "West",
    "Central",
]

product_categories = [
    "Electronics",
    "Home & Kitchen",
    "Clothing",
    "Grocery",
    "Sports",
    "Beauty",
]

payment_methods = [
    "Credit Card",
    "Debit Card",
    "UPI",
    "Net Banking",
    "Cash",
]

source_systems = [
    "CRM",
    "E-Commerce",
    "POS",
    "Mobile App",
    "Partner Portal",
]

transaction_statuses = [
    "Completed",
    "Pending",
    "Cancelled",
    "Refunded",
]


# ---------------------------------------------------------
# Generate clean base dataset
# ---------------------------------------------------------

start_date = datetime(2025, 1, 1)
end_date = datetime(2026, 9, 26)

date_range_days = (end_date - start_date).days

records = []

for i in range(1, NUM_RECORDS + 1):

    transaction_date = start_date + timedelta(
        days=random.randint(0, date_range_days)
    )

    quantity = random.randint(1, 8)

    unit_price = round(random.uniform(100, 15000), 2)

    sales_amount = round(quantity * unit_price, 2)

    record = {
        "transaction_id": f"TXN{i:06d}",
        "customer_id": f"CUST{random.randint(10001, 19999)}",
        "transaction_date": transaction_date.strftime("%Y-%m-%d"),
        "region": random.choice(regions),
        "product_category": random.choice(product_categories),
        "sales_amount": sales_amount,
        "quantity": quantity,
        "payment_method": random.choice(payment_methods),
        "source_system": random.choice(source_systems),
        "transaction_status": random.choice(transaction_statuses),
    }

    records.append(record)


df = pd.DataFrame(records)


# ---------------------------------------------------------
# Introduce intentional data-quality issues
# ---------------------------------------------------------

# 1. Missing customer IDs
missing_customer_indices = np.random.choice(
    df.index,
    size=100,
    replace=False,
)

df.loc[missing_customer_indices, "customer_id"] = None


# 2. Missing payment methods
missing_payment_indices = np.random.choice(
    df.index,
    size=80,
    replace=False,
)

df.loc[missing_payment_indices, "payment_method"] = None


# 3. Invalid regions
invalid_region_indices = np.random.choice(
    df.index,
    size=50,
    replace=False,
)

df.loc[invalid_region_indices, "region"] = np.random.choice(
    ["Unknown", "N/A", "Invalid"],
    size=len(invalid_region_indices),
)


# 4. Negative sales amounts
negative_amount_indices = np.random.choice(
    df.index,
    size=40,
    replace=False,
)

df.loc[negative_amount_indices, "sales_amount"] *= -1


# 5. Zero quantities
zero_quantity_indices = np.random.choice(
    df.index,
    size=35,
    replace=False,
)

df.loc[zero_quantity_indices, "quantity"] = 0


# 6. Future transaction dates
future_date_indices = np.random.choice(
    df.index,
    size=30,
    replace=False,
)

future_dates = [
    datetime(2027, 1, 1) + timedelta(days=random.randint(0, 365))
    for _ in range(len(future_date_indices))
]

df.loc[future_date_indices, "transaction_date"] = [
    date.strftime("%Y-%m-%d") for date in future_dates
]


# 7. Invalid transaction statuses
invalid_status_indices = np.random.choice(
    df.index,
    size=25,
    replace=False,
)

df.loc[invalid_status_indices, "transaction_status"] = np.random.choice(
    ["Unknown", "Invalid", "ERROR"],
    size=len(invalid_status_indices),
)


# 8. Duplicate transactions
duplicate_indices = np.random.choice(
    df.index,
    size=75,
    replace=False,
)

duplicates = df.loc[duplicate_indices].copy()

df = pd.concat(
    [df, duplicates],
    ignore_index=True,
)


# ---------------------------------------------------------
# Shuffle records
# ---------------------------------------------------------

df = df.sample(
    frac=1,
    random_state=RANDOM_SEED,
).reset_index(drop=True)


# ---------------------------------------------------------
# Save dataset
# ---------------------------------------------------------

RAW_DATA_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

df.to_csv(
    RAW_DATA_PATH,
    index=False,
)


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

print("=" * 60)
print("DATASET GENERATION COMPLETED")
print("=" * 60)

print(f"Records created : {len(df):,}")
print(f"Columns         : {len(df.columns)}")
print(f"Output file     : {RAW_DATA_PATH}")

print("\nColumns:")
for column in df.columns:
    print(f" - {column}")

print("\nMissing values:")
print(df.isna().sum())

print("\nDataset preview:")
print(df.head())

print("=" * 60)