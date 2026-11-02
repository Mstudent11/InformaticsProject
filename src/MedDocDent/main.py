
import sqlite3
from pathlib import Path
from datetime import datetime
import hashlib
from typing import Optional, List, Dict, Any

DB_NAME = "MedDocDent.odb"

# --- Подключение и инициализация ---

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if Path(DB_NAME).exists():
        print("База данных уже существует.")
        return

    conn = get_connection()
    cur = conn.cursor()

    schema_sql = """
    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY,
        login VARCHAR(50) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(20) NOT NULL CHECK (role IN ('ADMIN', 'DOCTOR', 'PATIENT')),
        name VARCHAR(100) NOT NULL,
        surname VARCHAR(100) NOT NULL,
        patronymic VARCHAR(100) NOT NULL,
        contact_phone VARCHAR(20)
    );

    CREATE TABLE patients (
        user_id INTEGER PRIMARY KEY,
        birth_date DATE NOT NULL,
        gender VARCHAR(10),
        policy_number VARCHAR(50),
        contact_phone VARCHAR(20),
        CONSTRAINT fk_patient_user FOREIGN KEY (user_id) REFERENCES users(user_id)
            ON UPDATE CASCADE ON DELETE CASCADE
    );

    CREATE TABLE doctors (
        user_id INTEGER PRIMARY KEY,
        specialty VARCHAR(100) NOT NULL,
        shift_type VARCHAR(50),
        CONSTRAINT fk_doctor_user FOREIGN KEY (user_id) REFERENCES users(user_id)
            ON UPDATE CASCADE ON DELETE CASCADE
    );

    CREATE TABLE schedule_periods (
        period_id INTEGER PRIMARY KEY,
        doctor_id INTEGER NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        type VARCHAR(20) NOT NULL,
        CONSTRAINT fk_period_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(user_id)
            ON UPDATE CASCADE ON DELETE CASCADE,
        CONSTRAINT chk_period_dates CHECK (start_date <= end_date)
    );

    CREATE TABLE shifts (
        shift_id INTEGER PRIMARY KEY,
        doctor_id INTEGER NOT NULL,
        day_date DATE NOT NULL,
        start_time VARCHAR(8) NOT NULL,
        end_time VARCHAR(8) NOT NULL,
        CONSTRAINT fk_shift_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(user_id)
            ON UPDATE CASCADE ON DELETE CASCADE,
        CONSTRAINT chk_shift_time CHECK (start_time < end_time)
    );

    CREATE TABLE appointments (
        appointment_id INTEGER PRIMARY KEY,
        patient_id INTEGER NOT NULL,
        shift_id INTEGER NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP,
        status VARCHAR(20) NOT NULL DEFAULT 'BOOKED',
        CONSTRAINT fk_app_patient FOREIGN KEY (patient_id) REFERENCES patients(user_id)
            ON UPDATE CASCADE ON DELETE CASCADE,
        CONSTRAINT fk_app_shift FOREIGN KEY (shift_id) REFERENCES shifts(shift_id)
            ON UPDATE CASCADE ON DELETE CASCADE
    );
    """

    cur.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("База данных создана.")

# --- DAO ---

def authenticate(login: str, password_hash: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM users WHERE login = ? AND password_hash = ?",
            (login, password_hash)
        )
        row = cur.fetchone()
        return dict(row) if row else None

def create_user(login: str, password_hash: str, role: str, name: str, surname: str,
                patronymic: str, contact_phone: Optional[str]) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users (login, password_hash, role, name, surname, patronymic, contact_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (login, password_hash, role, name, surname, patronymic, contact_phone)
        )
        conn.commit()
        return cur.lastrowid

def create_patient(user_id: int, birth_date: str, gender: Optional[str],
                   policy_number: Optional[str], contact_phone: Optional[str]):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO patients (user_id, birth_date, gender, policy_number, contact_phone)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, birth_date, gender, policy_number, contact_phone)
        )
        conn.commit()

def create_doctor(user_id: int, specialty: str, shift_type: Optional[str]):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO doctors (user_id, specialty, shift_type)
            VALUES (?, ?, ?)
            """,
            (user_id, specialty, shift_type)
        )
        conn.commit()

def list_doctors_and_shifts() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT u.name, u.surname, d.specialty, s.day_date, s.start_time, s.end_time
            FROM doctors d
            JOIN users u ON d.user_id = u.user_id
            LEFT JOIN shifts s ON d.user_id = s.doctor_id
            ORDER BY u.surname, s.day_date, s.start_time
        """)
        return [dict(row) for row in cur.fetchall()]

def add_shift(doctor_user_id: int, day_date: str, start_time: str, end_time: str) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO shifts (doctor_id, day_date, start_time, end_time)
            VALUES (?, ?, ?, ?)
            """,
            (doctor_user_id, day_date, start_time, end_time)
        )
        conn.commit()
        return cur.lastrowid

def delete_shift(shift_id: int):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM shifts WHERE shift_id = ?", (shift_id,))
        conn.commit()

def book_appointment(patient_user_id: int, shift_id: int) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM appointments WHERE shift_id = ? AND status = 'BOOKED' LIMIT 1",
            (shift_id,)
        )
        if cur.fetchone():
            raise ValueError("Этот слот уже забронирован")

        cur.execute(
            """
            INSERT INTO appointments (patient_id, shift_id, status, created_at)
            VALUES (?, ?, 'BOOKED', ?)
            """,
            (patient_user_id, shift_id, datetime.now().isoformat())
        )
        conn.commit()
        return cur.lastrowid

def cancel_appointment(appointment_id: int):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE appointments SET status = 'CANCELLED' WHERE appointment_id = ?",
            (appointment_id,)
        )
        conn.commit()

def list_appointments_for_patient(patient_user_id: int) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT a.appointment_id, a.status, a.created_at,
                   s.day_date, s.start_time, s.end_time,
                   u.name AS doctor_name, u.surname AS doctor_surname, d.specialty
            FROM appointments a
            JOIN shifts s ON a.shift_id = s.shift_id
            JOIN doctors d ON s.doctor_id = d.user_id
            JOIN users u ON d.user_id = u.user_id
            WHERE a.patient_id = ?
            ORDER BY a.created_at DESC
        """, (patient_user_id,))
        return [dict(row) for row in cur.fetchall()]

def list_all_users() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users ORDER BY role, login")
        return [dict(row) for row in cur.fetchall()]

def delete_user(user_id: int):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()

def list_shifts_for_doctor(doctor_user_id: int) -> List[Dict[str, Any]]:
    """Для врача: только его смены."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT day_date, start_time, end_time
            FROM shifts
            WHERE doctor_id = ?
            ORDER BY day_date, start_time
        """, (doctor_user_id,))
        return [dict(row) for row in cur.fetchall()]

# --- Сервис авторизации и хеширования ---

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

class AuthService:
    @staticmethod
    def login(login: str, password: str) -> Optional[dict]:
        password_hash = hash_password(password)
        return authenticate(login, password_hash)

    @staticmethod
    def register_admin(name: str, surname: str, patronymic: str, login: str,
                       password: str, contact_phone: Optional[str] = None):
        password_hash = hash_password(password)
        user_id = create_user(login, password_hash, "ADMIN", name, surname,
                              patronymic, contact_phone)
        return user_id

    @staticmethod
    def register_doctor(name: str, surname: str, patronymic: str, login: str,
                        password: str, specialty: str, shift_type: Optional[str],
                        contact_phone: Optional[str] = None):
        password_hash = hash_password(password)
        user_id = create_user(login, password_hash, "DOCTOR", name, surname,
                              patronymic, contact_phone)
        create_doctor(user_id, specialty, shift_type)
        return user_id

    @staticmethod
    def register_patient(name: str, surname: str, patronymic: str, login: str,
                          password: str, birth_date: str, gender: Optional[str],
                          policy_number: Optional[str], contact_phone: Optional[str] = None):
        password_hash = hash_password(password)
        user_id = create_user(login, password_hash, "PATIENT", name, surname,
                              patronymic, contact_phone)
        create_patient(user_id, birth_date, gender, policy_number, contact_phone)
        return user_id

# --- CLI меню ---

def print_menu_common():
    print("\n--- Общее меню (все пользователи) ---")
    print("1. Посмотреть расписание врачей")
    print("0. Выйти")

def print_menu_admin():
    print("\n--- Меню администратора ---")
    print("1. Посмотреть расписание врачей")
    print("2. Добавить смену врачу")
    print("3. Удалить смену")
    print("4. Список всех пользователей")
    print("5. Добавить пользователя (пациент/врач)")
    print("6. Удалить пользователя")
    print("0. Выйти в главное меню")

def print_menu_patient():
    print("\n--- Меню пациента ---")
    print("1. Посмотреть расписание врачей")
    print("2. Записаться на приём")
    print("3. Мои записи")
    print("4. Отменить запись")
    print("0. Выйти в главное меню")

def print_menu_doctor():
    print("\n--- Меню врача ---")
    print("1. Посмотреть своё расписание")
    print("0. Выйти в главное меню")

def run_cli():
    init_db()

    while True:
        print("\n=== Клиника: вход в систему ===")
        print("1. Войти")
        print("2. Зарегистрироваться (только администратор создаёт остальных)")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            login = input("Логин: ").strip()
            password = input("Пароль: ").strip()
            user = AuthService.login(login, password)
            if not user:
                print("Неверный логин или пароль.")
                continue

            role = user["role"]
            print(f"Вы вошли как {role} ({user['name']} {user['surname']})")

            while True:
                if role == "ADMIN":
                    print_menu_admin()
                    sub = input("Действие: ").strip()
                    if sub == "0": break
                    elif sub == "1":
                        rows = list_doctors_and_shifts()
                        for r in rows:
                            print(r)
                    elif sub == "2":
                        doc_id = int(input("user_id врача: "))
                        day = input("Дата смены (YYYY-MM-DD): ").strip()
                        start = input("Начало (HH:MM): ").strip() + ":00"
                        end = input("Конец (HH:MM): ").strip() + ":00"
                        add_shift(doc_id, day, start, end)
                        print("Смена добавлена.")
                    elif sub == "3":
                        sid = int(input("shift_id для удаления: "))
                        delete_shift(sid)
                        print("Смена удалена.")
                    elif sub == "4":
                        users = list_all_users()
                        for u in users:
                            print(u)
                    elif sub == "5":
                        r = input("Роль (DOCTOR/PATIENT): ").strip().upper()
                        if r not in ("DOCTOR", "PATIENT"):
                            print("Неверная роль.")
                            continue
                        name = input("Имя: ").strip()
                        surname = input("Фамилия: ").strip()
                        patronymic = input("Отчество: ").strip()
                        login = input("Логин: ").strip()
                        password = input("Пароль: ").strip()
                        phone = input("Телефон (можно оставить пустым): ").strip() or None
                        if r == "DOCTOR":
                            specialty = input("Специальность: ").strip()
                            shift_type = input("Тип смены (можно оставить пустым): ").strip() or None
                            AuthService.register_doctor(name, surname, patronymic, login, password, specialty, shift_type, phone)
                            print("Врач добавлен.")
                        else:
                            birth_date = input("Дата рождения (YYYY-MM-DD): ").strip()
                            gender = input("Пол (можно оставить пустым): ").strip() or None
                            policy = input("Номер полиса (можно оставить пустым): ").strip() or None
                            phone_pat = input("Телефон пациента (можно оставить пустым): ").strip() or None
                            AuthService.register_patient(name, surname, patronymic, login, password, birth_date, gender, policy, phone_pat)
                            print("Пациент добавлен.")
                    elif sub == "6":
                        uid = int(input("user_id для удаления: "))
                        delete_user(uid)
                        print("Пользователь удалён.")
                    else:
                        print("Неверная команда.")

                elif role == "PATIENT":
                    print_menu_patient()
                    sub = input("Действие: ").strip()
                    if sub == "0": break
                    elif sub == "1":
                        rows = list_doctors_and_shifts()
                        for r in rows:
                            print(r)
                    elif sub == "2":
                        # Запись на приём: сначала покажем смены, чтобы пациент мог выбрать shift_id
                        print("Доступные смены (врач, дата, время):")
                        shifts = list_doctors_and_shifts()
                        for s in shifts:
                            if s["day_date"]:
                                print(f"{s['name']} {s['surname']}, {s['specialty']} — {s['day_date']} {s['start_time']}–{s['end_time']}")
                        try:
                            shift_id = int(input("Введите shift_id для записи: ").strip())
                            book_appointment(user["user_id"], shift_id)
                            print("Запись успешно создана.")
                        except ValueError as e:
                            print(f"Ошибка: {e}")
                    elif sub == "3":
                        appts = list_appointments_for_patient(user["user_id"])
                        if not appts:
                            print("У вас нет записей.")
                        else:
                            for a in appts:
                                print(a)
                    elif sub == "4":
                        try:
                            aid = int(input("Введите appointment_id для отмены: ").strip())
                            cancel_appointment(aid)
                            print("Запись отменена (статус изменён на CANCELLED).")
                        except Exception as e:
                            print(f"Ошибка отмены: {e}")
                    else:
                        print("Неверная команда.")

                elif role == "DOCTOR":
                    print_menu_doctor()
                    sub = input("Действие: ").strip()
                    if sub == "0": break
                    elif sub == "1":
                        doc_shifts = list_shifts_for_doctor(user["user_id"])
                        if not doc_shifts:
                            print("Смен пока нет.")
                        else:
                            for s in doc_shifts:
                                print(s)
                    else:
                        print("Неверная команда.")

        elif choice == "2":
            # Регистрация: разрешаем создать только админа (остальных создаёт админ)
            print("\n--- Регистрация администратора (только один первый пользователь) ---")
            name = input("Имя: ").strip()
            surname = input("Фамилия: ").strip()
            patronymic = input("Отчество: ").strip()
            login = input("Логин: ").strip()
            password = input("Пароль: ").strip()
            phone = input("Телефон (можно оставить пустым): ").strip() or None

            try:
                uid = AuthService.register_admin(name, surname, patronymic, login, password, phone)
                print(f"Администратор создан. user_id = {uid}")
            except sqlite3.IntegrityError:
                print("Такой логин уже существует.")
            except Exception as e:
                print(f"Ошибка регистрации: {e}")

        else:
            print("Неверная команда.")

    print("До свидания!")


if __name__ == "__main__":
    run_cli()