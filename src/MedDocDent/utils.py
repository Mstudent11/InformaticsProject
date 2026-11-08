def print_table(rows: list[dict], columns: list[str] | None = None):
    """Печатает список словарей как красивую таблицу в консоль."""
    if not rows:
        print("Нет доступных записей.")
        return

    # Если колонки не переданы, берём все ключи из первой строки
    if columns is None:
        columns = list(rows[0].keys())

    # Вычисляем ширину колонок
    widths = {}
    for col in columns:
        max_len = len(str(col))
        for row in rows:
            cell = str(row.get(col, ""))
            max_len = max(max_len, len(cell))
        widths[col] = max_len

    # Печатаем заголовок
    header = " | ".join(str(col).ljust(widths[col]) for col in columns)
    separator = "-+-".join("-" * widths[col] for col in columns)
    print(header)
    print(separator)

    # Печатаем строки
    for row in rows:
        line = " | ".join(str(row.get(col, "")).ljust(widths[col]) for col in columns)
        print(line)