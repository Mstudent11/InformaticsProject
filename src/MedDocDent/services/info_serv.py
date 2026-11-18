from database.db import get_connection
from services.access_control import AccessControl


def get_doctor_full_info(actor_role: str, actor_id, doctor_id: int):
    """Полная информация о враче: профиль, смены, периоды.

    ADMIN и PATIENT — любой врач; DOCTOR — только свои данные.
    Возвращает список блоков (title, headers, rows) или None.
    """
    allowed = (
        actor_role == "ADMIN"
        or actor_role == "PATIENT"
        or (actor_role == "DOCTOR" and actor_id == doctor_id)
    )
    if not allowed:
        raise PermissionError("Нет прав на просмотр информации о враче")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT u.user_id, u.login, u.name, u.surname, u.patronymic, u.contact_phone,
               d.specialty, d.shift_type
        FROM users u
        JOIN doctors d ON u.user_id = d.user_id
        WHERE u.user_id = ?
    """, (doctor_id,))
    doc = cur.fetchone()
    if doc is None:
        conn.close()
        return None

    blocks = [(
        "Профиль врача",
        ["User ID", "Логин", "Имя", "Фамилия", "Отчество", "Телефон", "Специальность", "График"],
        [doc],
    )]

    cur.execute("""
        SELECT shift_id, day_date, start_time, end_time
        FROM shifts WHERE doctor_id = ? ORDER BY day_date, start_time
    """, (doctor_id,))
    blocks.append(("Смены врача", ["Shift ID", "Дата", "Начало", "Конец"], cur.fetchall()))

    cur.execute("""
        SELECT period_id, type, start_date, end_date
        FROM schedule_periods WHERE doctor_id = ? ORDER BY start_date
    """, (doctor_id,))
    blocks.append(("Периоды врача", ["Period ID", "Тип", "Начало", "Конец"], cur.fetchall()))

    conn.close()
    return blocks


def get_patient_full_info(actor_role: str, actor_id, patient_id: int):
    """Полная информация о пациенте: профиль и его записи.

    ADMIN — любой пациент; PATIENT — только свои данные. Возвращает блоки или None.
    """
    if not (actor_role == "ADMIN" or (actor_role == "PATIENT" and actor_id == patient_id)):
        raise PermissionError("Нет прав на просмотр информации о пациенте")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT u.user_id, u.login, u.name, u.surname, u.patronymic, u.contact_phone,
               p.birth_date, p.gender, p.policy_number
        FROM users u
        JOIN patients p ON u.user_id = p.user_id
        WHERE u.user_id = ?
    """, (patient_id,))
    pat = cur.fetchone()
    if pat is None:
        conn.close()
        return None

    blocks = [(
        "Профиль пациента",
        ["User ID", "Логин", "Имя", "Фамилия", "Отчество", "Телефон", "Дата рождения", "Пол", "Полис"],
        [pat],
    )]

    cur.execute("""
        SELECT a.appointment_id, a.status, a.created_at,
               s.day_date, s.start_time, s.end_time,
               du.surname, du.name, d.specialty
        FROM appointments a
        JOIN shifts s ON a.shift_id = s.shift_id
        JOIN doctors d ON s.doctor_id = d.user_id
        JOIN users du ON d.user_id = du.user_id
        WHERE a.patient_id = ?
        ORDER BY s.day_date, s.start_time
    """, (patient_id,))
    blocks.append((
        "Записи пациента",
        ["App. ID", "Статус", "Создано", "Дата", "Начало", "Конец", "Фамилия врача", "Имя врача", "Специальность"],
        cur.fetchall(),
    ))

    conn.close()
    return blocks


def get_appointment_full_info(actor_role: str, actor_id, appointment_id: int):
    """Полная информация о записи: запись + пациент + смена + врач.

    ADMIN — все; PATIENT — только своя; DOCTOR — только записи на свои смены.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT a.appointment_id, a.status, a.created_at, a.updated_at,
               pu.user_id, pu.surname, pu.name, p.birth_date, p.policy_number,
               s.shift_id, s.day_date, s.start_time, s.end_time,
               du.user_id, du.surname, du.name, d.specialty
        FROM appointments a
        JOIN patients p ON a.patient_id = p.user_id
        JOIN users pu ON p.user_id = pu.user_id
        JOIN shifts s ON a.shift_id = s.shift_id
        JOIN doctors d ON s.doctor_id = d.user_id
        JOIN users du ON d.user_id = du.user_id
        WHERE a.appointment_id = ?
    """, (appointment_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return None

    (app_id, status, created_at, updated_at,
     pat_id, pat_surname, pat_name, birth_date, policy,
     shift_id, day, start, end,
     doc_id, doc_surname, doc_name, specialty) = row

    allowed = (
        actor_role == "ADMIN"
        or (actor_role == "PATIENT" and actor_id == pat_id)
        or (actor_role == "DOCTOR" and actor_id == doc_id)
    )
    if not allowed:
        raise PermissionError("Нет прав на просмотр этой записи")

    return [
        ("Запись на приём",
         ["App. ID", "Статус", "Создано", "Обновлено"],
         [(app_id, status, created_at, updated_at or "—")]),
        ("Пациент",
         ["User ID", "Фамилия", "Имя", "Дата рождения", "Полис"],
         [(pat_id, pat_surname, pat_name, birth_date, policy or "—")]),
        ("Смена и врач",
         ["Shift ID", "Дата", "Начало", "Конец", "Врач", "Специальность"],
         [(shift_id, day, start, end, f"{doc_surname} {doc_name}", specialty)]),
    ]


def get_shift_full_info(actor_role: str, actor_id, shift_id: int):
    """Информация о смене: смена + врач. Для ADMIN и DOCTOR — ещё записи на смену."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT s.shift_id, s.day_date, s.start_time, s.end_time,
               du.user_id, du.name, du.surname, du.patronymic, d.specialty
        FROM shifts s
        JOIN doctors d ON s.doctor_id = d.user_id
        JOIN users du ON d.user_id = du.user_id
        WHERE s.shift_id = ?
    """, (shift_id,))
    shift = cur.fetchone()
    if shift is None:
        conn.close()
        return None

    if actor_role == "DOCTOR" and actor_id != shift[4]:
        conn.close()
        raise PermissionError("Врач может просматривать только свои смены")

    blocks = [(
        "Смена",
        ["Shift ID", "Дата", "Начало", "Конец", "Врач", "Специальность"],
        [(shift[0], shift[1], shift[2], shift[3], f"{shift[6]} {shift[5]} {shift[7]}", shift[8])],
    )]

    if actor_role in ("ADMIN", "DOCTOR"):
        cur.execute("""
            SELECT a.appointment_id, pu.surname, pu.name, a.status, a.created_at
            FROM appointments a
            JOIN patients p ON a.patient_id = p.user_id
            JOIN users pu ON p.user_id = pu.user_id
            WHERE a.shift_id = ?
            ORDER BY a.appointment_id
        """, (shift_id,))
        blocks.append((
            "Записи на смену",
            ["App. ID", "Фамилия пациента", "Имя пациента", "Статус", "Создано"],
            cur.fetchall(),
        ))

    conn.close()
    return blocks