from database.db import get_connection
from models.shifts import Shift


def _row_to_shift(row) -> Shift:
    return Shift(
        shift_id=row[0],
        doctor_id=row[1],
        day_date=row[2],
        start_time=row[3],
        end_time=row[4],
    )


def create(doctor_id: int, day_date: str, start_time: str, end_time: str) -> int:
    if start_time >= end_time:
        raise ValueError("Смена не может заканчиваться раньше, чем начинается")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO shifts(doctor_id, day_date, start_time, end_time)
        VALUES (?, ?, ?, ?)
    """, (doctor_id, day_date, start_time, end_time))

    conn.commit()
    shift_id = cur.lastrowid
    conn.close()
    return shift_id


def get_by_id(shift_id: int) -> Shift | None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT shift_id, doctor_id, day_date, start_time, end_time
        FROM shifts
        WHERE shift_id = ?
    """, (shift_id,))

    row = cur.fetchone()
    conn.close()
    return _row_to_shift(row) if row else None


def get_doctor_schedule(doctor_id: int) -> list[Shift]:
    """Расписание конкретного врача."""
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
    return [_row_to_shift(row) for row in rows]


def get_full_schedule():
    """Расписание всех врачей с ФИО и специальностью.

    Возвращает кортежи: (shift_id, doctor_id, name, surname, patronymic,
    specialty, day_date, start_time, end_time)
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT s.shift_id, s.doctor_id, u.name, u.surname, u.patronymic,
               d.specialty, s.day_date, s.start_time, s.end_time
        FROM shifts s
        JOIN doctors d ON s.doctor_id = d.user_id
        JOIN users u ON d.user_id = u.user_id
        ORDER BY s.day_date, s.start_time
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


def get_free_shifts():
    """Свободные смены без записей — для меню бронирований.

    Возвращает кортежи: (shift_id, doctor_id, name, surname, patronymic,
    specialty, day_date, start_time, end_time)
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT s.shift_id, s.doctor_id, u.name, u.surname, u.patronymic,
               d.specialty, s.day_date, s.start_time, s.end_time
        FROM shifts s
        JOIN doctors d ON s.doctor_id = d.user_id
        JOIN users u ON d.user_id = u.user_id
        WHERE s.shift_id NOT IN (SELECT shift_id FROM appointments)
        ORDER BY s.day_date, s.start_time
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


def update(shift_id: int, doctor_id: int = None, day_date: str = None,
           start_time: str = None, end_time: str = None):
    conn = get_connection()
    cur = conn.cursor()

    fields = []
    params = []

    if doctor_id is not None:
        fields.append("doctor_id = ?")
        params.append(doctor_id)
    if day_date is not None:
        fields.append("day_date = ?")
        params.append(day_date)
    if start_time is not None:
        fields.append("start_time = ?")
        params.append(start_time)
    if end_time is not None:
        fields.append("end_time = ?")
        params.append(end_time)

    if not fields:
        conn.close()
        return

    params.append(shift_id)
    cur.execute(f"UPDATE shifts SET {', '.join(fields)} WHERE shift_id = ?", params)

    conn.commit()
    conn.close()


def delete(shift_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM shifts WHERE shift_id = ?", (shift_id,))

    conn.commit()
    conn.close()