
import os
import json
import csv
import yaml
from xml.etree import ElementTree as ET
from pathlib import Path
import sqlite3

# ================= КОНФИГУРАЦИЯ (меняй только здесь) =================
DB_PATH = "MedDocDent.db"
OUTPUT_DIR = "out"

# Основная таблица (откуда берём данные)
MAIN_TABLE = "users"
MAIN_PK = "user_id"

# Связанная таблица (профиль: patients или doctors)
RELATED_TABLE = "patients"  # поставь "doctors", если нужно выгрузить врачей

# Условие JOIN
JOIN_CONDITION = "users.user_id = patients.user_id"  # для doctors: "users.user_id = doctors.user_id"

# Поля основной таблицы для экспорта
MAIN_FIELDS = [
    "user_id",
    "login",
    "role",
    "name",
    "surname",
    "patronymic",
    "contact_phone"
]

# Поля связанной таблицы для экспорта (будут вложены)
RELATED_FIELDS = [
    "birth_date",
    "gender",
    "policy_number",
    "contact_phone"
]  # для doctors используй: ["specialty", "shift_type"]
# =====================================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # доступ к колонкам по имени
    return conn

def fetch_joined_data():
    """
    Выполняет SELECT с JOIN и возвращает список словарей.
    Для JSON/XML/YAML: основная запись + вложенный объект profile.
    Для CSV: плоская строка (все поля подряд).
    """
    conn = get_connection()
    cur = conn.cursor()

    # Формируем SELECT: все нужные поля из MAIN_FIELDS и RELATED_FIELDS
    main_cols = ", ".join([f"{MAIN_TABLE}.{col}" for col in MAIN_FIELDS])
    rel_cols = ", ".join([f"{RELATED_TABLE}.{col}" for col in RELATED_FIELDS])

    query = f"""
        SELECT {main_cols}, {rel_cols}
        FROM {MAIN_TABLE}
        LEFT JOIN {RELATED_TABLE} ON {JOIN_CONDITION}
    """

    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    records = []
    for row in rows:
        record = {}
        # Заполняем основную часть
        for col in MAIN_FIELDS:
            record[col] = row[f"{MAIN_TABLE}.{col}"]

        # Вложенная часть (профиль)
        profile = {}
        for col in RELATED_FIELDS:
            profile[col] = row[f"{RELATED_TABLE}.{col}"]
        record["profile"] = profile

        records.append(record)

    return records

def ensure_output_dir():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def write_json(records):
    path = Path(OUTPUT_DIR) / "data.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def write_csv(records):
    """CSV — плоский формат: все поля в одной строке."""
    path = Path(OUTPUT_DIR) / "data.csv"
    if not records:
        return

    # Заголовки: сначала поля основной таблицы, затем поля профиля
    fieldnames = MAIN_FIELDS + [f"profile.{col}" for col in RELATED_FIELDS]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            row = {**rec}
            # «распаковываем» профиль в плоский словарь
            for col in RELATED_FIELDS:
                row[f"profile.{col}"] = rec["profile"][col]
            writer.writerow(row)

def write_xml(records):
    root = ET.Element("records")
    for rec in records:
        elem = ET.SubElement(root, "record")
        # Основная часть
        for col in MAIN_FIELDS:
            ET.SubElement(elem, col).text = str(rec[col]) if rec[col] is not None else ""
        # Профиль (вложенный)
        prof_elem = ET.SubElement(elem, "profile")
        for col in RELATED_FIELDS:
            ET.SubElement(prof_elem, col).text = (
                str(rec["profile"][col]) if rec["profile"][col] is not None else ""
            )

    tree = ET.ElementTree(root)
    path = Path(OUTPUT_DIR) / "data.xml"
    ET.indent(tree, space="  ", level=0)
    tree.write(path, encoding="utf-8", xml_declaration=True)

def write_yaml(records):
    path = Path(OUTPUT_DIR) / "data.yaml"
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(records, f, allow_unicode=True, sort_keys=False)

def main():
    ensure_output_dir()
    records = fetch_joined_data()
    write_json(records)
    write_csv(records)
    write_xml(records)
    write_yaml(records)
    print(f"Данные экспортированы в папку: {Path(OUTPUT_DIR).absolute()}")
    print(f"Всего записей: {len(records)}")

if __name__ == "__main__":
    main()