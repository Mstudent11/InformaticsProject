from database.db import get_connection
from models.patients import Patient



def get_all_rows(self):
    """Возвращает все строки таблицы patients (для отображения списка)."""
    conn = self.get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM patients"
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return rows


def _row_to_patient(row) -> Patient:
    return Patient(
        user_id=row[0],
        birth_date=row[1],
        gender=row[2],
        policy_number=row[3],
        contact_phone=row[4],
    )


def create(user_id: int, birth_date: str, gender: str = None,
           policy_number: str = None, contact_phone: str = None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO patients(user_id, birth_date, gender, policy_number, contact_phone)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, birth_date, gender, policy_number, contact_phone))

    conn.commit()
    conn.close()


def get_by_user_id(user_id: int) -> Patient | None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, birth_date, gender, policy_number, contact_phone
        FROM patients
        WHERE user_id = ?
    """, (user_id,))

    row = cur.fetchone()
    conn.close()
    return _row_to_patient(row) if row else None


def update(user_id: int, birth_date: str = None, gender: str = None,
           policy_number: str = None, contact_phone: str = None):
    conn = get_connection()
    cur = conn.cursor()

    fields = []
    params = []

    if birth_date is not None:
        fields.append("birth_date = ?")
        params.append(birth_date)
    if gender is not None:
        fields.append("gender = ?")
        params.append(gender)
    if policy_number is not None:
        fields.append("policy_number = ?")
        params.append(policy_number)
    if contact_phone is not None:
        fields.append("contact_phone = ?")
        params.append(contact_phone)

    if not fields:
        conn.close()
        return

    params.append(user_id)
    cur.execute(f"UPDATE patients SET {', '.join(fields)} WHERE user_id = ?", params)

    conn.commit()
    conn.close()


'''def delete(user_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM patients WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()'''

def get_all_rows() -> list[tuple]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients")
    rows = cur.fetchall()
    conn.close()
    return rows