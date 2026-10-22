-- Таблица пользователей (администраторы, врачи, пациенты)
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,             -- Уникальный идентификатор пользователя 
    login VARCHAR(50) NOT NULL UNIQUE,   -- Логин для входа
    password_hash VARCHAR(255) NOT NULL, -- Хеш пароля 
    role VARCHAR(20) NOT NULL,           -- Роль: ADMIN, DOCTOR, PATIENT
    full_name VARCHAR(100) NOT NULL,     -- Полное имя пользователя
    contact_phone VARCHAR(20)            -- Контактный телефон
);

-- Профиль пациента 
CREATE TABLE patients (
    patient_id INTEGER PRIMARY KEY, -- Ссылка на user_id
    birth_date DATE NOT NULL,   -- Дата рождения
    gender VARCHAR(10),         -- Пол
    policy_number VARCHAR(50),  -- Номер полиса
    contact_phone VARCHAR(20),  -- Контактный телефон пациента
    CONSTRAINT fk_patient_user FOREIGN KEY (patient_id) REFERENCES users(user_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- Профиль врача 
CREATE TABLE doctors (
    doctor_id INTEGER PRIMARY KEY,        -- Ссылка на user_id 
    specialty VARCHAR(100) NOT NULL,  -- Специальность врача (например, «терапевт», «стоматолог»)
    shift_type VARCHAR(50),           -- Тип графика/смены врача
    CONSTRAINT fk_doctor_user FOREIGN KEY (doctor_id) REFERENCES users(user_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE schedule_periods (
    period_id INTEGER PRIMARY KEY, -- Уникальный идентификатор периода
    doctor_id INTEGER NOT NULL,    -- Врач, к которому относится период
    start_date DATE NOT NULL,  -- Дата начала периода
    end_date DATE NOT NULL,    -- Дата окончания периода
    type VARCHAR(20) NOT NULL, -- Тип периода: VACATION, TRAINING и т. п.
    CONSTRAINT fk_period_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- Рабочие смены врачей
CREATE TABLE shifts (
    shift_id INTEGER PRIMARY KEY,                -- Уникальный идентификатор смены
    doctor_id INTEGER NOT NULL,                  -- Врач, который работает в эту смену
    day_date DATE NOT NULL,                  -- Дата смены
    start_time TIME NOT NULL,                -- Время начала смены
    end_time TIME NOT NULL,                  -- Время окончания смены
    CONSTRAINT fk_shift_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
        ON UPDATE CASCADE ON DELETE CASCADE, -- Проверка: смена не может заканчиваться раньше, чем начинается
    CONSTRAINT chk_shift_time CHECK (start_time < end_time)
);

-- Записи на приём
CREATE TABLE appointments (
    appointment_id INTEGER PRIMARY KEY,      -- Уникальный идентификатор записи
    patient_id INTEGER NOT NULL,             -- Пациент, записавшийся на приём
    shift_id INTEGER NOT NULL,               -- Слот времени (смена), на которую назначена запись
    created_at TIMESTAMP DEFAULT NOW(),  -- Дата и время создания записи
    updated_at TIMESTAMP,                -- Дата и время последнего изменения записи
    status VARCHAR(20) DEFAULT 'BOOKED', -- Статус записи: BOOKED, COMPLETED и т. п.
    CONSTRAINT fk_app_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_app_shift FOREIGN KEY (shift_id) REFERENCES shifts(shift_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);
