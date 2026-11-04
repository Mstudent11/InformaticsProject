from database.db import get_connection
from models.schedule_periods import SchedulePeriod

VALID_TYPES = ('VACATION', 'TRAINING', 'SICK_LEAVE', 'DAY_OFF')


def _row_to_period(row) -> SchedulePeriod:
    return SchedulePeriod(
        period_id=row[0],
        doctor_id=row[1],
        start_date=row[2],
        end_date=row[3],
        type=row[4],
    )


def create(doctor_id: int, start_date: str, end_date: str, type: str) -> int:
    if type not in VALID_TYPES:
        raise ValueError(f"Недопустимый тип периода: {type}")
    if start_date > end_date:
        raise ValueError("Дата начала не может быть позже даты окончания")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO schedule_periods(doctor_id, start_date, end_date, type)
        VALUES (?, ?, ?, ?)
    """, (doctor_id, start_date, end_date, type))

    conn.commit()
    period_id = cur.lastrowid
    conn.close()
    return period_id


def get_by_id(period_id: int) -> SchedulePeriod | None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT period_id, doctor_id, start_date, end_date, type
        FROM schedule_periods
        WHERE period_id = ?
    """, (period_id,))

    row = cur.fetchone()
    conn.close()
    return _row_to_period(row) if row else None


def get_by_doctor(doctor_id: int) -> list[SchedulePeriod]:
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
    return [_row_to_period(row) for row in rows]


def delete(period_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM schedule_periods WHERE period_id = ?", (period_id,))

    conn.commit()
    conn.close()