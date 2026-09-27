from pathlib import Path

import pandas as pd


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_PATH = PROJECT_ROOT / "data" / "processed"


# =========================================================
# LOAD DATA
# =========================================================

transactions_path = PROCESSED_PATH / "validated_transactions.csv"
exceptions_path = PROCESSED_PATH / "data_quality_exceptions.csv"

transactions = pd.read_csv(transactions_path)
exceptions = pd.read_csv(exceptions_path)


# =========================================================
# PREPARE DATES
# =========================================================

transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"],
    errors="coerce",
)

exceptions["transaction_date"] = pd.to_datetime(
    exceptions["transaction_date"],
    errors="coerce",
)


# =========================================================
# 1. EXCEPTIONS BY RULE
# =========================================================

exception_by_rule = (
    exceptions
    .groupby(
        ["exception_rule", "severity"],
        as_index=False,
    )
    .agg(
        exception_count=("transaction_id", "count"),
        affected_records=("transaction_id", "nunique"),
    )
    .sort_values(
        "exception_count",
        ascending=False,
    )
)

exception_by_rule.to_csv(
    PROCESSED_PATH / "exception_by_rule.csv",
    index=False,
)


# =========================================================
# 2. EXCEPTIONS BY SOURCE SYSTEM
# =========================================================

exception_by_source = (
    exceptions
    .groupby(
        "source_system",
        as_index=False,
    )
    .agg(
        exception_count=("transaction_id", "count"),
        affected_records=("transaction_id", "nunique"),
    )
    .sort_values(
        "exception_count",
        ascending=False,
    )
)

exception_by_source.to_csv(
    PROCESSED_PATH / "exception_by_source.csv",
    index=False,
)


# =========================================================
# 3. EXCEPTIONS BY REGION
# =========================================================

exception_by_region = (
    exceptions
    .groupby(
        "region",
        as_index=False,
    )
    .agg(
        exception_count=("transaction_id", "count"),
        affected_records=("transaction_id", "nunique"),
    )
    .sort_values(
        "exception_count",
        ascending=False,
    )
)

exception_by_region.to_csv(
    PROCESSED_PATH / "exception_by_region.csv",
    index=False,
)


# =========================================================
# 4. MONTHLY EXCEPTION TREND
# =========================================================

exceptions["month"] = (
    exceptions["transaction_date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_exceptions = (
    exceptions
    .groupby(
        "month",
        as_index=False,
    )
    .agg(
        exception_count=("transaction_id", "count"),
        affected_records=("transaction_id", "nunique"),
    )
    .sort_values("month")
)

monthly_exceptions.to_csv(
    PROCESSED_PATH / "monthly_exceptions.csv",
    index=False,
)


# =========================================================
# 5. SOURCE QUALITY SUMMARY
# =========================================================

total_by_source = (
    transactions
    .groupby("source_system")
    .size()
    .reset_index(name="total_records")
)

exception_by_source_summary = (
    exceptions
    .groupby("source_system")
    .size()
    .reset_index(name="exception_count")
)

source_quality = total_by_source.merge(
    exception_by_source_summary,
    on="source_system",
    how="left",
)

source_quality["exception_count"] = (
    source_quality["exception_count"]
    .fillna(0)
    .astype(int)
)

source_quality["valid_records"] = (
    source_quality["total_records"]
    - source_quality["exception_count"]
)

source_quality["quality_rate"] = (
    source_quality["valid_records"]
    / source_quality["total_records"]
    * 100
).round(2)

source_quality.to_csv(
    PROCESSED_PATH / "source_quality_summary.csv",
    index=False,
)


# =========================================================
# DISPLAY RESULTS
# =========================================================

print("=" * 70)
print("ANALYTICS TABLE GENERATION COMPLETED")
print("=" * 70)

print("\nException by Rule:")
print(exception_by_rule.to_string(index=False))

print("\nException by Source:")
print(exception_by_source.to_string(index=False))

print("\nException by Region:")
print(exception_by_region.to_string(index=False))

print("\nSource Quality:")
print(source_quality.to_string(index=False))

print("\nCreated files:")

for file in sorted(PROCESSED_PATH.glob("*.csv")):
    print(f" - {file.name}")

print("=" * 70)
