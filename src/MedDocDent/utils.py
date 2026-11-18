def print_table(title, headers, rows):
    """Выводит таблицу в консоль с выравниванием колонок."""
    print(f"\n=== {title} ===")
    if not rows:
        print("(пусто)")
        return

    if len(headers) == 0:
        return

    expected_cols = len(headers)
    for i, row in enumerate(rows):
        if len(row) != expected_cols:
            raise ValueError(
                f"Несовпадение колонок: строка {i} имеет {len(row)} колонок, "
                f"а заголовков — {expected_cols}. Строка: {row}"
            )

    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

    def format_row(row_values):
        return "|" + "|".join(f" {str(v):<{w}} " for v, w in zip(row_values, col_widths)) + "|"

    print(separator)
    print(format_row(headers))
    print(separator)
    for r in rows:
        print(format_row(r))
    print(separator)

'''def print_table(rows: list[dict], columns: list[str] | None = None):
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
        print(line)'''

