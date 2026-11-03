from db import get_connection

conn = get_connection()
cur = conn.cursor()

# Добавляем пользователя
cur.execute(
    "INSERT INTO users (user_id, login, password_hash, role, name, surname, patronymic, contact_phone) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
    (1, "ivanov", "sha256:abcd...", "PATIENT", "Иван", "Иванов", "Иванович", "+7 900 000-00-00"),
)
cur.execute(
    "INSERT INTO patients (user_id, birth_date, gender, policy_number) VALUES (?, ?, ?, ?)",
    (1, "1990-05-14", "мужской", "5500 1234 56"),
)

conn.commit()

# Проверяем: записи пациентов с ФИО пользователя
cur.execute("""
    SELECT u.name, u.surname, p.birth_date
    FROM patients p
    JOIN users u ON u.user_id = p.user_id
""")
for row in cur.fetchall():
    print(row)

conn.close()