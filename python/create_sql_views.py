import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "sql" / "data_quality.db"
SQL_PATH = BASE_DIR / "sql" / "create_views.sql"


conn = sqlite3.connect(DB_PATH)

sql_script = SQL_PATH.read_text(encoding="utf-8")

conn.executescript(sql_script)

conn.commit()


views = conn.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'view'
    ORDER BY name
""").fetchall()


print("=" * 60)
print("SQL views created successfully")
print("=" * 60)

for view in views:
    print(view[0])

conn.close()

