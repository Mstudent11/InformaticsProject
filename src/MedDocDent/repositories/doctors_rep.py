from src.MedDocDent.database.db import get_connection
from src.MedDocDent.models.doctors import Doctor


def _row_to_doctor(row) -> Doctor:
    return Doctor(
        user_id=row[0],
        specialty=row[1],
        shift_type=row[2],
    )


def create(user_id: int, specialty: str, shift_type: str = None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO doctors(user_id, specialty, shift_type)
        VALUES (?, ?, ?)
    """, (user_id, specialty, shift_type))

    conn.commit()
    conn.close()


def get_by_user_id(user_id: int) -> Doctor | None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, specialty, shift_type
        FROM doctors
        WHERE user_id = ?
    """, (user_id,))

    row = cur.fetchone()
    conn.close()
    return _row_to_doctor(row) if row else None


def get_all():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, specialty, shift_type
        FROM doctors
        ORDER BY specialty
    """)

    rows = cur.fetchall()
    conn.close()
    return [_row_to_doctor(row) for row in rows]


def update(user_id: int, specialty: str = None, shift_type: str = None):
    conn = get_connection()
    cur = conn.cursor()

    fields = []
    params = []

    if specialty is not None:
        fields.append("specialty = ?")
        params.append(specialty)
    if shift_type is not None:
        fields.append("shift_type = ?")
        params.append(shift_type)

    if not fields:
        conn.close()
        return

    params.append(user_id)
    cur.execute(f"UPDATE doctors SET {', '.join(fields)} WHERE user_id = ?", params)

    conn.commit()
    conn.close()


def delete(user_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM doctors WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()