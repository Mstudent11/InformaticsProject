import sqlite3

DB_NAME = "MedDocDent.db"

conn = sqlite3.connect(DB_NAME)
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

print("База открыта. Вводите SQL-запросы (пустая строка — выход):")
while True:
    query = input("\n> ").strip()
    if not query:
        break
    try:
        cur.execute(query)
        if query.strip().upper().startswith("SELECT"):
            for row in cur.fetchall():
                print(row)
        else:
            conn.commit()
            print("Выполнено, изменения сохранены.")
    except Exception as e:
        print("Ошибка:", e)

conn.close()
#> INSERT INTO users (login, password_hash, role, name, surname, patronymic) VALUES ('petrov', 'hash', 'DOCTOR', 'Пётр', 'Петров', 'Петрович');
#>  SELECT * FROM users; 