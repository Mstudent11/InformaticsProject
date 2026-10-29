from src.MedDocDent.database import get_connection
from src.MedDocDent.models.shifts import Shift
from typing import List, Optional
from datetime import datetime

def _map_shift(row) -> Shift:
    return Shift(*row)

def get_all() -> List[Shift]:
    """
    Получить все смены (всё расписание). Доступно всем пользователям.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT shift_id, doctor_id, day_date, start_time, end_time
        FROM shifts
        ORDER BY day_date, start_time
    """)
    rows = cur.fetchall()
    conn.close()
    return [_map_shift(r) for r in rows]

def get_by_doctor_id(doctor_id: int) -> List[Shift]:
    """
    Получить смены конкретного врача. Для врача (своё расписание) и админа.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT shift_id, doctor_id, day_date, start_time, end_time
        FROM shifts
        WHERE doctor_id = ?
        ORDER BY day_date, start_time
    """, (doctor_id,))
    rows = cur.fetchall()
    conn.close()
    return [_map_shift(r) for r in rows]

def create(doctor_id: int, day_date: str, start_time: str, end_time: str) -> int:
    """
    Добавить новую смену. Только для администратора.
    day_date и время передаются как строки в формате YYYY-MM-DD и HH:MM:SS.
    Возвращает shift_id новой смены.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO shifts(doctor_id, day_date, start_time, end_time)
        VALUES (?, ?, ?, ?)
    """, (doctor_id, day_date, start_time, end_time))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def update(shift_id: int, day_date: Optional[str], start_time: Optional[str], end_time: Optional[str]) -> bool:
    """
    Частично обновить смену (любое подмножество полей). Только для администратора.
    Возвращает True, если обновление произошло.
    """
    parts = []
    values = []

    if day_date is not None:
        parts.append("day_date = ?")
        values.append(day_date)
    if start_time is not None:
        parts.append("start_time = ?")
        values.append(start_time)
    if end_time is not None:
        parts.append("end_time = ?")
        values.append(end_time)

    if not parts:
        return False

    values.append(shift_id)
    query = f"UPDATE shifts SET {', '.join(parts)} WHERE shift_id = ?"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, values)
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated

def delete(shift_id: int) -> bool:
    """
    Удалить смену. Только для администратора.
    Перед удалением желательно проверить, нет ли активных записей на этот слот.
    Возвращает True, если удаление произошло.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM shifts WHERE shift_id = ?", (shift_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted