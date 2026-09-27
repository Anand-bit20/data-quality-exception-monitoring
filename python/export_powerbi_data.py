import sqlite3
from pathlib import Path
import pandas as pd


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "sql" / "data_quality.db"
POWERBI_DIR = BASE_DIR / "powerbi"

POWERBI_DIR.mkdir(exist_ok=True)


# Connect to SQLite
conn = sqlite3.connect(DB_PATH)


# SQL views to export
views = [
    "vw_quality_summary",
    "vw_source_quality",
    "vw_exception_analysis",
    "vw_exception_by_source",
    "vw_exception_by_region",
    "vw_monthly_exceptions",
    "vw_exception_severity",
    "vw_exception_details"
]


print("=" * 60)
print("Exporting SQL views for Power BI")
print("=" * 60)


for view in views:

    query = f"SELECT * FROM {view}"

    df = pd.read_sql_query(query, conn)

    output_file = POWERBI_DIR / f"{view}.csv"

    df.to_csv(output_file, index=False)

    print(f"{view:<30} {len(df):>6} rows")


conn.close()


print("\nPower BI files created successfully.")
print(f"Location: {POWERBI_DIR}")