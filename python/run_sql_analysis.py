import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "sql" / "data_quality.db"
SQL_PATH = BASE_DIR / "sql" / "analysis_queries.sql"


conn = sqlite3.connect(DB_PATH)

sql_script = SQL_PATH.read_text(encoding="utf-8")

# Split the SQL file into individual queries
queries = [
    query.strip()
    for query in sql_script.split(";")
    if query.strip()
]


for i, query in enumerate(queries, start=1):

    cursor = conn.execute(query)

    columns = [description[0] for description in cursor.description]

    rows = cursor.fetchall()

    print("\n" + "=" * 70)
    print(f"QUERY {i}")
    print("=" * 70)

    print(" | ".join(columns))
    print("-" * 70)

    for row in rows[:20]:
        print(" | ".join(str(value) for value in row))

    if len(rows) > 20:
        print(f"\n... {len(rows) - 20} more rows")


conn.close()

print("\nSQL analysis completed successfully.")