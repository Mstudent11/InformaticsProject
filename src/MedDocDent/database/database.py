import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR / "schema.sql"
DB_PATH = BASE_DIR / "MedDocDent.db"

def create_database():
    DB_PATH.unlink(missing_ok=True)  # удаляем старую БД, если есть

    with open(SCHEMA_PATH, encoding="utf-8") as f:
        sql_script = f.read()

    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(sql_script)
        conn.commit()

    print("База данных app.db создана заново")

if __name__ == "__main__":
    create_database()