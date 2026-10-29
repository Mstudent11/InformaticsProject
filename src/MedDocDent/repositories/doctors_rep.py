from src.MedDocDent.database import get_connection
from src.MedDocDent.models.doctors import Doctor
from typing import List, Optional

def _map_doctor(row) -> Doctor:
    return Doctor(*row)

def get_by_user_id(user_id: int) -> Optional[Doctor]:
    """
    Получить профиль врача по user_id (который одновременно doctor_id).
    Возвращает None, если профиль не найден.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT doctor_id, specialty, shift_type
        FROM doctors
        WHERE doctor_id = ?
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    return _map_doctor(row) if row else None

def list_all_doctors() -> List[Doctor]:
    """
    Получить полный список врачей. Для админа и пациента (просмотр специалистов).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT doctor_id, specialty, shift_type
        FROM doctors
        ORDER BY specialty, doctor_id
    """)
    rows = cur.fetchall()
    conn.close()
    return [_map_doctor(r) for r in rows]