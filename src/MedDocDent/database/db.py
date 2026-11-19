from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "MedDocDent.db"

# Таблицы, к которым разрешён универсальный доступ (просмотр + будущая выгрузка)
ALLOWED_TABLES = (
    "users", "patients", "doctors", "schedule_periods", "shifts", "appointments",
)

# Связи таблиц: таблица -> {внешний ключ: (связанная таблица, её первичный ключ)}
# Понадобится для вложения связанных данных при экспорте в JSON/XML/YAML
TABLE_RELATIONS = {
    "patients": {"user_id": ("users", "user_id")},
    "doctors": {"user_id": ("users", "user_id")},
    "schedule_periods": {"doctor_id": ("doctors", "user_id")},
    "shifts": {"doctor_id": ("doctors", "user_id")},
    "appointments": {
        "patient_id": ("patients", "user_id"),
        "shift_id": ("shifts", "shift_id"),
    },
}


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
        print(f"[init_db] Пропущено: {e}")
    finally:
        conn.close()


def get_all_rows(table_name: str) -> list[tuple]:
    """Универсальная выборка всех строк таблицы.

    Основа для просмотра таблиц и будущего модуля экспорта:
    изменение структуры данных не требует переработки логики.
    """
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Недопустимая таблица: {table_name}")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    conn.close()
    return rows

'''from pathlib import Path
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
        conn.close()'''



