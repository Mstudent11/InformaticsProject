import sqlite3

from src.MedDocDent.database.db import get_connection
from src.MedDocDent.models.appointment import Appointment


def _row_to_appointment(row) -> Appointment:
    return Appointment(
        appointment_id=row[0],
        patient_id=row[1],
        shift_id=row[2],
        created_at=row[3],
        updated_at=row[4],
        status=row[5],
    )


def create(patient_id: int, shift_id: int, status: str = 'BOOKED') -> int:
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO appointments(patient_id, shift_id, status)
            VALUES (?, ?, ?)
        """, (patient_id, shift_id, status))

        conn.commit()
        appointment_id = cur.lastrowid
    except sqlite3.IntegrityError as e:
        conn.close()
        raise Exception(f"Не удалось создать запись: {e}")

    conn.close()
    return appointment_id


def get_by_id(appointment_id: int) -> Appointment | None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT appointment_id, patient_id, shift_id, created_at, updated_at, status
        FROM appointments
        WHERE appointment_id = ?
    """, (appointment_id,))

    row = cur.fetchone()
    conn.close()
    return _row_to_appointment(row) if row else None


def get_by_patient(patient_id: int):
    """Записи пациента с данными врача и смены — для меню бронирований.

    Возвращает кортежи: (appointment_id, status, created_at,
    doctor_name, doctor_surname, doctor_patronymic, specialty,
    day_date, start_time, end_time)
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT a.appointment_id, a.status, a.created_at,
               u.name, u.surname, u.patronymic, d.specialty,
               s.day_date, s.start_time, s.end_time
        FROM appointments a
        JOIN shifts s ON a.shift_id = s.shift_id
        JOIN doctors d ON s.doctor_id = d.user_id
        JOIN users u ON d.user_id = u.user_id
        WHERE a.patient_id = ?
        ORDER BY s.day_date, s.start_time
    """, (patient_id,))

    rows = cur.fetchall()
    conn.close()
    return rows


def get_by_shift(shift_id: int) -> list[Appointment]:
    """Записи по смене — используется админом при редактировании расписания."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT appointment_id, patient_id, shift_id, created_at, updated_at, status
        FROM appointments
        WHERE shift_id = ?
    """, (shift_id,))

    rows = cur.fetchall()
    conn.close()
    return [_row_to_appointment(row) for row in rows]


def update_status(appointment_id: int, status: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE appointments
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE appointment_id = ?
    """, (status, appointment_id))

    conn.commit()
    conn.close()


def delete(appointment_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM appointments WHERE appointment_id = ?", (appointment_id,))

    conn.commit()
    conn.close()