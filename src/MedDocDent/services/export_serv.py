import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml  # pip install pyyaml

from database.db import get_connection, ALLOWED_TABLES, TABLE_RELATIONS
from services.access_control import AccessControl

OUT_DIR = Path(__file__).resolve().parent.parent / "out"
MAX_DEPTH = 4
EXCLUDED_FIELDS = {"password_hash"}  # хеши паролей в выгрузку не попадают


def list_tables() -> list[str]:
    """Список таблиц, доступных для экспорта."""
    return list(ALLOWED_TABLES)


def _get_columns_and_rows(table_name: str):
    """SELECT * с автоматически определёнными именами колонок.

    Код универсален: при изменении структуры таблицы ничего править не нужно.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    columns = [d[0] for d in cur.description]
    rows = [dict(zip(columns, row)) for row in cur.fetchall()]
    conn.close()
    return columns, rows


def _fetch_related(table_name: str, fk_column: str, value):
    """Связанные строки по внешнему ключу — согласно карте TABLE_RELATIONS."""
    related_table, related_pk = TABLE_RELATIONS[table_name][fk_column]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        f"SELECT * FROM {related_table} WHERE {related_pk} = ?", (value,)
    )
    cols = [d[0] for d in cur.description]
    related_rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    conn.close()
    return related_table, related_rows


def build_record(table_name: str, row: dict, depth: int = 0) -> dict:
    """Вкладывает связанные данные в запись (JSON/XML/YAML).

    По карте TABLE_RELATIONS для каждого внешнего ключа подтягивается
    связанная строка и рекурсивно обрабатывается так же. Глубина ограничена
    на случай, если связи в БД когда-нибудь замкнутся в цикл.
    """
    if depth >= MAX_DEPTH or table_name not in TABLE_RELATIONS:
        return {k: v for k, v in row.items() if k not in EXCLUDED_FIELDS}

    record = {k: v for k, v in row.items() if k not in EXCLUDED_FIELDS}

    for fk_column, (related_table, _related_pk) in TABLE_RELATIONS[table_name].items():
        value = record.get(fk_column)
        if value is None:
            continue

        related_table, related_rows = _fetch_related(table_name, fk_column, value)
        if not related_rows:
            continue

        # Вложение под именем связанной таблицы: appointments -> {patients: {...}, shifts: {...}}
        record[related_table] = build_record(related_table, related_rows[0], depth + 1)

    return record


def _flatten(record: dict, prefix: str = "") -> dict:
    """Разворачивает вложенные словари в плоские колонки вида patients.name."""
    flat = {}
    for key, value in record.items():
        full_key = f"{prefix}{key}"
        if isinstance(value, dict):
            flat.update(_flatten(value, prefix=f"{full_key}."))
        else:
            flat[full_key] = value
    return flat


def _add_xml(parent, data: dict):
    for key, value in data.items():
        if isinstance(value, dict):
            child = ET.SubElement(parent, key)
            _add_xml(child, value)
        else:
            child = ET.SubElement(parent, key)
            child.text = "" if value is None else str(value)


def export_table(table_name: str) -> Path:
    """Экспорт таблицы в data.json, data.csv, data.xml, data.yaml в папку out.

    Возвращает путь к папке с файлами.
    """
    
    '''if not AccessControl.can_export(table_name):  # проверка роли делается в меню
        raise PermissionError("Экспорт доступен только администратору")'''
    
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Недопустимая таблица: {table_name}")

    _columns, rows = _get_columns_and_rows(table_name)
    records = [build_record(table_name, r) for r in rows]

    OUT_DIR.mkdir(exist_ok=True)  # папка создаётся автоматически, если её нет

    # ---- JSON ----
    with open(OUT_DIR / "data.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2, default=str)

    # ---- CSV (вложенные данные объединяются в одной строке: patients.name и т. п.) ----
    flat_rows = [_flatten(r) for r in records]
    fieldnames = []
    for flat in flat_rows:
        for key in flat:
            if key not in fieldnames:
                fieldnames.append(key)
    with open(OUT_DIR / "data.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, restval="")
        writer.writeheader()
        writer.writerows(flat_rows)

    # ---- XML ----
    root = ET.Element(table_name)
    for rec in records:
        row_el = ET.SubElement(root, "row")
        _add_xml(row_el, rec)
    ET.ElementTree(root).write(
        OUT_DIR / "data.xml", encoding="utf-8", xml_declaration=True
    )

    # ---- YAML ----
    with open(OUT_DIR / "data.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(
            records, f, allow_unicode=True, sort_keys=False, default_flow_style=False
        )

    return OUT_DIR