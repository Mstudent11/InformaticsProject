from src.MedDocDent.database import get_connection
from src.MedDocDent.models.users import User
from typing import Optional, List

def _map_user(row) -> User:
    # Преобразует строку БД в объект User
    return User(*row)

def get_by_login(login: str) -> Optional[User]:
    """
    Получить пользователя по логину. Используется для аутентификации.
    Возвращает None, если пользователь не найден.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, login, role, name, surname, partronymic, contact_phone
        FROM users
        WHERE login = ?
    """, (login,))
    row = cur.fetchone()
    conn.close()
    return _map_user(row) if row else None

def create_user(login: str, password_hash: str, role: str, name: str, surname: str, partronymic: str, contact_phone: Optional[str]) -> int:
    """
    Создать нового пользователя. Используется администратором.
    Возвращает user_id новой записи.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users(login, password_hash, role, name, surname, partronymic, contact_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (login, password_hash, role, name, surname, partronymic, contact_phone))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def delete_user(user_id: int) -> bool:
    """
    Удалить пользователя. Используется администратором.
    Благодаря ON DELETE CASCADE удалятся также patient/doctor и связанные записи.
    Возвращает True, если строка была удалена.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted

def list_all_users() -> List[User]:
    """
    Получить список всех пользователей. Для администратора (просмотр).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, login, role, name, surname, partronymic, contact_phone
        FROM users
        ORDER BY role, surname, name
    """)
    rows = cur.fetchall()
    conn.close()
    return [_map_user(r) for r in rows]