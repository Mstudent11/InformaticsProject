> INSERT INTO shifts (shift_id, doctor_id, day_date, start_time, end_time) VALUES ('1', '1', '2026-11-02', '10', '18');

> INSERT INTO users (login, password_hash, role, name, surname, patronymic, contact_phone) VALUES ('CBA', '1234565', 'ADMIN', 'admin1', '', '','8xxxxxxxxxx');

> INSERT INTO users (login, password_hash, role, name, surname, patronymic, contact_phone) VALUES ('abc', '1234', 'PATIENT', 'Ivan', 'Ivanov', 'Ivanovich','8yxxxxxxxxx');

> INSERT INTO users (login, password_hash, role, name, surname, patronymic, contact_phone) VALUES ('abcd', '12345', 'PATIENT', 'Boris', 'Petrov', 'Ivanovich','8zxxxxxxxxx');  
Выполнено, изменения сохранены.

> INSERT INTO users (login, password_hash, role, name, surname, patronymic, contact_phone) VALUES ('abcde', '123456', 'PATIENT', 'Andrew', 'Sidorov', 'Antonovich','8xyxxxxxxxx');
Выполнено, изменения сохранены.

> INSERT INTO users (login, password_hash, role, name, surname, patronymic, contact_phone) VALUES ('ABC', '4321', 'DOCTOR', 'Semen', 'Lobanov', 'Ivanovich','8xzxxxxxxxx');       
Выполнено, изменения сохранены.

> INSERT INTO users (login, password_hash, role, name, surname, patronymic, contact_phone) VALUES ('ABCD', '54321', 'DOCTOR', 'Boris', 'Levin', 'Semenovich','8xxyxxxxxxx');
Выполнено, изменения сохранены.

> INSERT INTO users (login, password_hash, role, name, surname, patronymic, contact_phone) VALUES ('ABCDE', '654321', 'DOCTOR', 'Gleb', 'Romanenko', 'Romanovich','8xxzxxxxxxx');
Выполнено, изменения сохранены.

> INSERT INTO patients  (user_id, birth_date, gender, policy_number, contact_phone) VALUES ('2', '01.01.00', 'Мужской', '1xxxxxxxxx','8yxxxxxxxxx');
Выполнено, изменения сохранены.

> INSERT INTO patients  (user_id, birth_date, gender, policy_number, contact_phone) VALUES ('3', '02.01.00', 'Мужской', '2xxxxxxxxx','8zxxxxxxxxx');
Выполнено, изменения сохранены.

> INSERT INTO patients  (user_id, birth_date, gender, policy_number, contact_phone) VALUES ('4', '03.01.00', 'Мужской', '3xxxxxxxxx','8xyxxxxxxxx');
Выполнено, изменения сохранены.

> INSERT INTO doctors (user_id, specialty, shift_type) VALUES ('5', 'Стоматолог-терапевт', '1');
Выполнено, изменения сохранены.

> INSERT INTO doctors (user_id, specialty, shift_type) VALUES ('6', 'Стоматолог-хирург', '2');  
Выполнено, изменения сохранены.

> INSERT INTO doctors (user_id, specialty, shift_type) VALUES ('7', 'Стоматолог-ортопед', '3');
Выполнено, изменения сохранены.

> INSERT INTO shifts (doctor_id, day_date, start_time, end_time) VALUES (1, 2026-11-02, 10:00:00, 18:00:00);

> INSERT INTO appointments (patient_id, shift_id, created_at, updated_at, status)  VALUES (2, 1, '2026-10-29 10:00:00', NULL, 'BOOKED');

