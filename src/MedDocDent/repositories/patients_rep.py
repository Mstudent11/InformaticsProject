from src.MedDocDent.database import get_connection
from src.MedDocDent.models.patients import Patient
from typing import Optional

def _map_patient(row) -> Patient:
    return Patient(*row)

def get_by_user_id(user_id: int) -> Optional[Patient]:
    """
    Получить профиль пациента по user_id (который одновременно patient_id).
    Возвращает None, если профиль не найден.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT patient_id, birth_date, gender, policy_number, contact_phone
        FROM patients
        WHERE patient_id = ?
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    return _map_patient(row) if row else None