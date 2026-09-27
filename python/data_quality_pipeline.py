from pathlib import Path

import pandas as pd


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "retail_transactions.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed"


# =========================================================
# CONFIGURATION
# =========================================================

VALID_REGIONS = {
    "North",
    "South",
    "East",
    "West",
    "Central",
}

VALID_PAYMENT_METHODS = {
    "Credit Card",
    "Debit Card",
    "UPI",
    "Net Banking",
    "Cash",
}

VALID_STATUSES = {
    "Completed",
    "Pending",
    "Cancelled",
    "Refunded",
}

DATA_CUTOFF_DATE = pd.Timestamp("2026-09-26")


# =========================================================
# LOAD DATA
# =========================================================

print("=" * 70)
print("DATA QUALITY VALIDATION PIPELINE")
print("=" * 70)

print("\nLoading raw dataset...")

df = pd.read_csv(RAW_DATA_PATH)

print(f"Records loaded: {len(df):,}")
print(f"Columns loaded: {len(df.columns)}")


# =========================================================
# PREPARE DATA
# =========================================================

df["transaction_date"] = pd.to_datetime(
    df["transaction_date"],
    errors="coerce",
)


# =========================================================
# CREATE EXCEPTION STORAGE
# =========================================================

exceptions = []


def add_exception(
    row,
    rule,
    severity,
    field,
    description,
):
    """
    Add a data-quality exception to the exception list.
    """

    exceptions.append(
        {
            "transaction_id": row["transaction_id"],
            "customer_id": row["customer_id"],
            "transaction_date": row["transaction_date"],
            "region": row["region"],
            "source_system": row["source_system"],
            "exception_rule": rule,
            "severity": severity,
            "affected_field": field,
            "description": description,
            "status": "Open",
        }
    )


# =========================================================
# RULE 1 — MISSING CUSTOMER ID
# =========================================================

print("\nRunning Rule 1: Missing Customer ID")

missing_customer = df["customer_id"].isna()

for _, row in df[missing_customer].iterrows():

    add_exception(
        row=row,
        rule="Missing Customer ID",
        severity="High",
        field="customer_id",
        description="Customer ID is missing.",
    )

print(f"Exceptions found: {missing_customer.sum():,}")


# =========================================================
# RULE 2 — DUPLICATE TRANSACTION
# =========================================================

print("\nRunning Rule 2: Duplicate Transaction")

duplicate_transaction = df.duplicated(
    subset=["transaction_id"],
    keep=False,
)

for _, row in df[duplicate_transaction].iterrows():

    add_exception(
        row=row,
        rule="Duplicate Transaction",
        severity="Medium",
        field="transaction_id",
        description="Transaction ID appears more than once.",
    )

print(f"Exceptions found: {duplicate_transaction.sum():,}")


# =========================================================
# RULE 3 — INVALID REGION
# =========================================================

print("\nRunning Rule 3: Invalid Region")

invalid_region = ~df["region"].isin(VALID_REGIONS)

for _, row in df[invalid_region].iterrows():

    add_exception(
        row=row,
        rule="Invalid Region",
        severity="Medium",
        field="region",
        description="Region is not part of the approved region list.",
    )

print(f"Exceptions found: {invalid_region.sum():,}")


# =========================================================
# RULE 4 — NEGATIVE SALES AMOUNT
# =========================================================

print("\nRunning Rule 4: Negative Sales Amount")

negative_sales = df["sales_amount"] < 0

for _, row in df[negative_sales].iterrows():

    add_exception(
        row=row,
        rule="Negative Sales Amount",
        severity="High",
        field="sales_amount",
        description="Sales amount cannot be negative.",
    )

print(f"Exceptions found: {negative_sales.sum():,}")


# =========================================================
# RULE 5 — INVALID QUANTITY
# =========================================================

print("\nRunning Rule 5: Invalid Quantity")

invalid_quantity = df["quantity"] <= 0

for _, row in df[invalid_quantity].iterrows():

    add_exception(
        row=row,
        rule="Invalid Quantity",
        severity="High",
        field="quantity",
        description="Transaction quantity must be greater than zero.",
    )

print(f"Exceptions found: {invalid_quantity.sum():,}")


# =========================================================
# RULE 6 — FUTURE TRANSACTION DATE
# =========================================================

print("\nRunning Rule 6: Future Transaction Date")

future_transaction = df["transaction_date"] > DATA_CUTOFF_DATE

for _, row in df[future_transaction].iterrows():

    add_exception(
        row=row,
        rule="Future Transaction Date",
        severity="Medium",
        field="transaction_date",
        description="Transaction date occurs after the data cutoff date.",
    )

print(f"Exceptions found: {future_transaction.sum():,}")


# =========================================================
# RULE 7 — MISSING PAYMENT METHOD
# =========================================================

print("\nRunning Rule 7: Missing Payment Method")

missing_payment = df["payment_method"].isna()

for _, row in df[missing_payment].iterrows():

    add_exception(
        row=row,
        rule="Missing Payment Method",
        severity="Medium",
        field="payment_method",
        description="Payment method is missing.",
    )

print(f"Exceptions found: {missing_payment.sum():,}")


# =========================================================
# RULE 8 — INVALID TRANSACTION STATUS
# =========================================================

print("\nRunning Rule 8: Invalid Transaction Status")

invalid_status = ~df["transaction_status"].isin(VALID_STATUSES)

for _, row in df[invalid_status].iterrows():

    add_exception(
        row=row,
        rule="Invalid Transaction Status",
        severity="Medium",
        field="transaction_status",
        description="Transaction status is not an approved status.",
    )

print(f"Exceptions found: {invalid_status.sum():,}")


# =========================================================
# CREATE EXCEPTION DATAFRAME
# =========================================================

exceptions_df = pd.DataFrame(exceptions)


# =========================================================
# CREATE RECORD-LEVEL QUALITY STATUS
# =========================================================

exception_transaction_ids = set(
    exceptions_df["transaction_id"]
)

df["data_quality_status"] = df["transaction_id"].apply(
    lambda x: "Exception"
    if x in exception_transaction_ids
    else "Valid"
)


# =========================================================
# CALCULATE QUALITY METRICS
# =========================================================

total_records = len(df)

valid_records = (
    df["data_quality_status"] == "Valid"
).sum()

exception_records = (
    df["data_quality_status"] == "Exception"
).sum()

quality_score = round(
    (valid_records / total_records) * 100,
    2,
)


# =========================================================
# SAVE PROCESSED DATA
# =========================================================

PROCESSED_DATA_PATH.mkdir(
    parents=True,
    exist_ok=True,
)

cleaned_data_path = (
    PROCESSED_DATA_PATH / "validated_transactions.csv"
)

exceptions_path = (
    PROCESSED_DATA_PATH / "data_quality_exceptions.csv"
)

metrics_path = (
    PROCESSED_DATA_PATH / "data_quality_summary.csv"
)


df.to_csv(
    cleaned_data_path,
    index=False,
)

exceptions_df.to_csv(
    exceptions_path,
    index=False,
)


# =========================================================
# CREATE SUMMARY TABLE
# =========================================================

summary = pd.DataFrame(
    {
        "metric": [
            "Total Records",
            "Valid Records",
            "Exception Records",
            "Quality Score",
            "Total Exceptions",
        ],
        "value": [
            total_records,
            valid_records,
            exception_records,
            quality_score,
            len(exceptions_df),
        ],
    }
)

summary.to_csv(
    metrics_path,
    index=False,
)


# =========================================================
# PRINT RESULTS
# =========================================================

print("\n" + "=" * 70)
print("DATA QUALITY VALIDATION COMPLETED")
print("=" * 70)

print(f"\nTotal records       : {total_records:,}")
print(f"Valid records       : {valid_records:,}")
print(f"Exception records   : {exception_records:,}")
print(f"Total exceptions    : {len(exceptions_df):,}")
print(f"Data quality score  : {quality_score}%")

print("\nExceptions by rule:")

print(
    exceptions_df["exception_rule"]
    .value_counts()
    .to_string()
)

print("\nExceptions by severity:")

print(
    exceptions_df["severity"]
    .value_counts()
    .to_string()
)

print("\nOutput files:")

print(f" - {cleaned_data_path}")
print(f" - {exceptions_path}")
print(f" - {metrics_path}")

print("\n" + "=" * 70)