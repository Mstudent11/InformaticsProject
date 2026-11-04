-- Схема базы данных клиники (SQLite)
-- Безопасно запускать повторно: существующие таблицы не трогаются.

-- Таблица пользователей (администраторы, врачи, пациенты)
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('ADMIN', 'DOCTOR', 'PATIENT')),
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    patronymic VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(20)
);

-- Профиль пациента
CREATE TABLE IF NOT EXISTS patients (
    user_id INTEGER NOT NULL UNIQUE,
    birth_date DATE NOT NULL,
    gender VARCHAR(10),
    policy_number VARCHAR(50),
    contact_phone VARCHAR(20),
    CONSTRAINT fk_patient_user FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- Профиль врача
CREATE TABLE IF NOT EXISTS doctors (
    user_id INTEGER NOT NULL UNIQUE,
    specialty VARCHAR(100) NOT NULL,
    shift_type VARCHAR(50),
    CONSTRAINT fk_doctor_user FOREIGN KEY (user_id) REFERENCES doctors(user_id) ON DELETE CASCADE
);

-- Периоды расписания (отпуск, обучение и т. п.)
CREATE TABLE IF NOT EXISTS schedule_periods (
    period_id INTEGER PRIMARY KEY,
    doctor_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    type VARCHAR(20) NOT NULL,
    CONSTRAINT fk_period_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(user_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_period_dates CHECK (start_date <= end_date)
);

-- Рабочие смены врачей
CREATE TABLE IF NOT EXISTS shifts (
    shift_id INTEGER PRIMARY KEY,
    doctor_id INTEGER NOT NULL,
    day_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    CONSTRAINT fk_shift_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(user_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_shift_time CHECK (start_time < end_time)
);

-- Записи на приём
CREATE TABLE IF NOT EXISTS appointments (
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
