from src.MedDocDent.database.db import get_connection
from src.MedDocDent.models.users import User

VALID_ROLES = ('ADMIN', 'DOCTOR', 'PATIENT')


def _row_to_user(row) -> User:
    return User(
        user_id=row[0],
        login=row[1],
        password_hash=row[2],
        role=row[3],
        name=row[4],
        surname=row[5],
        patronymic=row[6],
        contact_phone=row[7],
    )


def create(login: str, password_hash: str, role: str,
           name: str, surname: str, patronymic: str,
           contact_phone: str = None) -> int:
    if role not in VALID_ROLES:
        raise ValueError(f"Недопустимая роль: {role}")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users(login, password_hash, role, name, surname, patronymic, contact_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (login, password_hash, role, name, surname, patronymic, contact_phone))

    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id


def get_by_id(user_id: int) -> User | None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, login, password_hash, role, name, surname, patronymic, contact_phone
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    row = cur.fetchone()
    conn.close()
    return _row_to_user(row) if row else None


def get_by_login(login: str) -> User | None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, login, password_hash, role, name, surname, patronymic, contact_phone
        FROM users
        WHERE login = ?
    """, (login,))

    row = cur.fetchone()
    conn.close()
    return _row_to_user(row) if row else None


def get_doctors_list():
    """Список врачей с ФИО и специальностью."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT u.user_id, u.name, u.surname, u.patronymic, u.contact_phone,
               d.specialty, d.shift_type
        FROM users u
        JOIN doctors d ON u.user_id = d.user_id
        ORDER BY d.specialty, u.surname
    """)

    rows = cur.fetchall()
    conn.close()
    return rows   # кортежи: (user_id, name, surname, patronymic, contact_phone, specialty, shift_type)


def update(user_id: int, name: str = None, surname: str = None,
           patronymic: str = None, contact_phone: str = None,
           password_hash: str = None):
    conn = get_connection()
    cur = conn.cursor()

    fields = []
    params = []

    if name is not None:
        fields.append("name = ?")
        params.append(name)
    if surname is not None:
        fields.append("surname = ?")
        params.append(surname)
    if patronymic is not None:
        fields.append("patronymic = ?")
        params.append(patronymic)
    if contact_phone is not None:
        fields.append("contact_phone = ?")
        params.append(contact_phone)
    if password_hash is not None:
        fields.append("password_hash = ?")
        params.append(password_hash)

    if not fields:
        conn.close()
        return

    params.append(user_id)
    cur.execute(f"UPDATE users SET {', '.join(fields)} WHERE user_id = ?", params)

    conn.commit()
    conn.close()


def delete(user_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()