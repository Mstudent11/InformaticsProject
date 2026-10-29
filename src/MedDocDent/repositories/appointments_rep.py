from src.MedDocDent.database import get_connection
from src.MedDocDent.models.appointment import Appointment
from datetime import datetime
from typing import List, Optional

def _map_appointment(row) -> Appointment:
    return Appointment(*row)

def create(patient_id: int, shift_id: int) -> int:
    """
    Создать запись на приём. Для пациента.
    Статус по умолчанию — BOOKED.
    Возвращает appointment_id.
    """
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.now().isoformat()
    cur.execute("""
        INSERT INTO appointments(patient_id, shift_id, created_at, status)
        VALUES (?, ?, ?, 'BOOKED')
    """, (patient_id, shift_id, now))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def cancel(appointment_id: int) -> bool:
    """
    Отменить запись. Для пациента (если статус BOOKED).
    Устанавливает статус CANCELLED и обновляет updated_at.
    Возвращает True, если отмена прошла.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE appointments
        SET status = 'CANCELLED', updated_at = CURRENT_TIMESTAMP
        WHERE appointment_id = ? AND status = 'BOOKED'
    """, (appointment_id,))
    conn.commit()
    cancelled = cur.rowcount > 0
    conn.close()
    return cancelled

def get_by_patient_id(patient_id: int) -> List[Appointment]:
    """
    Получить все записи пациента. Для пациента (история/отмена).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT appointment_id, patient_id, shift_id, created_at, updated_at, status
        FROM appointments
        WHERE patient_id = ?
        ORDER BY created_at DESC
    """, (patient_id,))
    rows = cur.fetchall()
    conn.close()
    return [_map_appointment(r) for r in rows]

def get_by_shift_id(shift_id: int) -> List[Appointment]:
    """
    Получить все записи на конкретную смену. Для администратора/врача (контроль загрузки).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT appointment_id, patient_id, shift_id, created_at, updated_at, status
        FROM appointments
        WHERE shift_id = ?
        ORDER BY created_at
    """, (shift_id,))
    rows = cur.fetchall()
    conn.close()
    return [_map_appointment(r) for r in rows]

def mark_completed(appointment_id: int) -> bool:
    """
    Пометить запись как завершённую. Только для администратора/врача.
    Возвращает True, если статус изменён.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE appointments
        SET status = 'COMPLETED', updated_at = CURRENT_TIMESTAMP
        WHERE appointment_id = ?""")