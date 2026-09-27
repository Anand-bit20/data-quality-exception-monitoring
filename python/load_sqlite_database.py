import sqlite3
from pathlib import Path
import pandas as pd


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DB_DIR = BASE_DIR / "sql"

DB_DIR.mkdir(exist_ok=True)

DB_PATH = DB_DIR / "data_quality.db"


# Input files
transactions_file = PROCESSED_DIR / "validated_transactions.csv"
exceptions_file = PROCESSED_DIR / "data_quality_exceptions.csv"


# Load CSV files
transactions_df = pd.read_csv(transactions_file)
exceptions_df = pd.read_csv(exceptions_file)


# Convert transaction date
transactions_df["transaction_date"] = pd.to_datetime(
    transactions_df["transaction_date"],
    errors="coerce"
)


exceptions_df["transaction_date"] = pd.to_datetime(
    exceptions_df["transaction_date"],
    errors="coerce"
)


# Connect to SQLite
conn = sqlite3.connect(DB_PATH)


# Load transactions table
transactions_df.to_sql(
    "transactions",
    conn,
    if_exists="replace",
    index=False
)


# Load exceptions table
exceptions_df.to_sql(
    "exceptions",
    conn,
    if_exists="replace",
    index=False
)


# Create useful indexes
conn.execute("""
CREATE INDEX IF NOT EXISTS idx_transactions_transaction_id
ON transactions(transaction_id)
""")

conn.execute("""
CREATE INDEX IF NOT EXISTS idx_transactions_source_system
ON transactions(source_system)
""")

conn.execute("""
CREATE INDEX IF NOT EXISTS idx_transactions_region
ON transactions(region)
""")

conn.execute("""
CREATE INDEX IF NOT EXISTS idx_exceptions_transaction_id
ON exceptions(transaction_id)
""")

conn.execute("""
CREATE INDEX IF NOT EXISTS idx_exceptions_exception_rule
ON exceptions(exception_rule)
""")

conn.commit()


# Verify database
transaction_count = pd.read_sql_query(
    "SELECT COUNT(*) AS count FROM transactions",
    conn
).iloc[0]["count"]

exception_count = pd.read_sql_query(
    "SELECT COUNT(*) AS count FROM exceptions",
    conn
).iloc[0]["count"]


print("=" * 50)
print("SQLite database created successfully")
print("=" * 50)

print(f"Database : {DB_PATH}")
print(f"Transactions table : {transaction_count:,} rows")
print(f"Exceptions table   : {exception_count:,} rows")

print("\nTables:")
tables = pd.read_sql_query(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
    """,
    conn
)

print(tables.to_string(index=False))

conn.close()
