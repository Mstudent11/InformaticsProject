from pathlib import Path
import sqlite3

DB_NAME = "MedDocDent.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

if not SCHEMA_PATH.exists():
    raise FileNotFoundError(f"Не найден schema.sql по пути {SCHEMA_PATH}")

with SCHEMA_PATH.open(encoding="utf-8") as f:
    schema = f.read()

conn = sqlite3.connect(DB_NAME)
conn.execute("PRAGMA foreign_keys = ON;")
try:
    conn.executescript(schema)
    conn.commit()
    print(f"База {DB_NAME} успешно создана.")
except sqlite3.Error as e:
    print("Ошибка при создании схемы:", e)
    raise
finally:
    conn.close()