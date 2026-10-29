from src.MedDocDent.database import get_connection
from src.MedDocDent.models import SchedulePeriod
from typing import List, Optional

def _map_period(row) -> SchedulePeriod:
    # Преобразует строку БД в объект SchedulePeriod
    return SchedulePeriod(*row)

def get_by_id(period_id: int) -> Optional[SchedulePeriod]:
    """
    Получить период по ID. Для админа (просмотр/редактирование).
    Возвращает None, если не найден.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT period_id, doctor_id, start_date, end_date, type
        FROM schedule_periods
        WHERE period_id = ?
    """, (period_id,))
    row = cur.fetchone()
    conn.close()
    return _map_period(row) if row else None

def list_all() -> List[SchedulePeriod]:
    """
    Получить все периоды. Для админа (контроль загруженности/недоступности врачей).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT period_id, doctor_id, start_date, end_date, type
        FROM schedule_periods
        ORDER BY start_date, doctor_id
    """)
    rows = cur.fetchall()
    conn.close()
    return [_map_period(r) for r in rows]

def list_by_doctor(doctor_id: int) -> List[SchedulePeriod]:
    """
    Получить периоды конкретного врача. Для админа и самого врача (просмотр отпусков/обучения).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT period_id, doctor_id, start_date, end_date, type
        FROM schedule_periods
        WHERE doctor_id = ?
        ORDER BY start_date
    """, (doctor_id,))
    rows = cur.fetchall()
    conn.close()
    return [_map_period(r) for r in rows]

def create(doctor_id: int, start_date: str, end_date: str, period_type: str) -> int:
    """
    Создать новый период (отпуск, обучение и т. п.). Только для админа.
    Даты передаются как строки в формате YYYY-MM-DD.
    Возвращает period_id новой записи.
    """
    # Проверка: start_date <= end_date уже есть в БД через CHECK, но можно добавить валидацию в коде
    if start_date > end_date:
        raise ValueError("start_date не может быть позже end_date")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO schedule_periods(doctor_id, start_date, end_date, type)
        VALUES (?, ?, ?, ?)
    """, (doctor_id, start_date, end_date, period_type))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def update(
    period_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period_type: Optional[str] = None
) -> bool:
    """
    Частично обновить период (любое подмножество полей). Только для админа.
    Возвращает True, если обновление произошло.
    """
    parts = []
    values = []

    if start_date is not None:
        parts.append("start_date = ?")
        values.append(start_date)
    if end_date is not None:
        parts.append("end_date = ?")
        values.append(end_date)
    if period_type is not None:
        parts.append("type = ?")
        values.append(period_type)

    if not parts:
        return False

    values.append(period_id)
    query = f"UPDATE schedule_periods SET {', '.join(parts)} WHERE period_id = ?"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, values)
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated

def delete(period_id: int) -> bool:
    """
    Удалить период. Только для админа.
    Возвращает True, если удаление произошло.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM schedule_periods WHERE period_id = ?", (period_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted