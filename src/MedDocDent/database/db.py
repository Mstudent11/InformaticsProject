from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "MedDocDent.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Создаёт таблицы, если их ещё нет. Повторный запуск безопасен."""
    conn = get_connection()
    try:
        with open(BASE_DIR / "schema.sql", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    except sqlite3.OperationalError as e:
        # таблицы уже существуют — это нормальная ситуация
        print(f"[init_db] Пропущено: {e}")
    finally:
        conn.close()

