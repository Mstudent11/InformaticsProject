from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "MedDocDent.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Создаёт таблицы, если их ещё нет.

    Использует CREATE TABLE без DROP, чтобы данные не стирались
    при каждом запуске.
    statements нужно только для ручного пересоздания.
    """
    conn = get_connection()
    with open(BASE_DIR / "schema.sql", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
