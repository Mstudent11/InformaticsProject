from src.MedDocDent.services.users_serv import (
    register_patient,
    register_doctor,
    delete_user,
    get_doctors_list
)

from src.MedDocDent.services.schedule_serv import (
    get_full_schedule,
    get_doctor_schedule,
    add_shift,
    update_shift,
    delete_shift,
    add_period,
    get_doctor_periods,
    delete_period
)

from src.MedDocDent.services.appointments_serv import (
    get_free_shifts,
    create_appointment,
    get_my_appointments,
    delete_appointment
)


# -------------------------
# ОБЩЕЕ: ПРОСМОТР РАСПИСАНИЯ
# -------------------------
def view_schedule_menu(role: str):
    """Просмотр расписания врачей — доступно всем ролям."""
    while True:
        print("\n===== Расписание врачей =====")
        print("1. Всё расписание")
        print("2. Расписание конкретного врача")
        print("3. Периоды врача (отпуск/обучение)")
        print("0. Назад")

        choice = input("Выберите: ")

        if choice == "1":
            try:
                schedule = get_full_schedule(role)
                if not schedule:
                    print("\nРасписание пусто")
                    continue
                print("\nСмены:")
                for row in schedule:
                    shift_id, doctor_id, name, surname, patronymic, specialty, day, start, end = row
                    print(f"{shift_id}. {surname} {name} ({specialty}) | "
                          f"{day} {start}-{end}")
            except Exception as e:
                print(f"\nОшибка: {e}")

        elif choice == "2":
            doctors = _safe_doctors_list(role)
            if doctors is None:
                continue
            if not doctors:
                print("\nВрачей нет")
                continue
            print("\nВрачи:")
            for d in doctors:
                print(f"{d[0]}. {d[2]} {d[1]} {d[3]} ({d[5]})")

            doctor_id = input("ID врача: ")
            try:
                shifts = get_doctor_schedule(role, int(doctor_id))
                if not shifts:
                    print("\nУ этого врача нет смен")
                    continue
                for s in shifts:
                    print(f"{s.shift_id}. {s.day_date} {s.start_time}-{s.end_time}")
            except Exception as e:
                print(f"\nОшибка: {e}")

        elif choice == "3":
            doctors = _safe_doctors_list(role)
            if doctors is None:
                continue
            if not doctors:
                print("\nВрачей нет")
                continue
            print("\nВрачи:")
            for d in doctors:
                print(f"{d[0]}. {d[2]} {d[1]} {d[3]} ({d[5]})")

            doctor_id = input("ID врача: ")
            try:
                periods = get_doctor_periods(role, int(doctor_id))
                if not periods:
                    print("\nПериодов нет")
                    continue
                for p in periods:
                    print(f"{p.period_id}. {p.type}: {p.start_date} — {p.end_date}")
            except Exception as e:
                print(f"\nОшибка: {e}")

        elif choice == "0":
            break


def _safe_doctors_list(role: str):
    """Список врачей с обработкой ошибки прав (у доктора прав на список нет)."""
    try:
        return get_doctors_list(role)
    except Exception as e:
        print(f"\nОшибка: {e}")
        return None


# -------------------------
# ADMIN MENU
# -------------------------
def admin_menu(user):
    while True:
        print(f"\n===== Администратор ({user.login}) =====")
        print("1. Расписание врачей (просмотр)")
        print("2. Редактирование расписания")
        print("3. Управление пользователями")
        print("4. Список врачей")
        print("0. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            view_schedule_menu(user.role)

        elif choice == "2":
            schedule_edit_menu(user.role)

        elif choice == "3":
            users_menu(user.role)

        elif choice == "4":
            try:
                doctors = get_doctors_list(user.role)
                if not doctors:
                    print("\nВрачей нет")
                    continue
                print("\nСписок врачей:")
                for d in doctors:
                    print(f"{d[0]}. {d[2]} {d[1]} {d[3]} | {d[5]} | тел: {d[4] or '—'}")
            except Exception as e:
                print(f"\nОшибка: {e}")

        elif choice == "0":
            break


# -------------------------
# РЕДАКТИРОВАНИЕ РАСПИСАНИЯ (админ)
# -------------------------
def schedule_edit_menu(role: str):
    while True:
        print("\n===== Редактирование расписания =====")
        print("1. Добавить смену")
        print("2. Изменить смену")
        print("3. Удалить смену")
        print("4. Добавить период (отпуск/обучение)")
        print("5. Удалить период")
        print("0. Назад")

        choice = input("Выберите: ")

        if choice == "1":
            doctors = _safe_doctors_list(role)
            if not doctors:
                print("\nСначала добавьте врачей")
                continue
            for d in doctors:
                print(f"{d[0]}. {d[2]} {d[1]} ({d[5]})")

            try:
                add_shift(
                    role,
                    int(input("ID врача: ")),
                    input("Дата (ГГГГ-ММ-ДД): "),
                    input("Начало (ЧЧ:ММ): "),
                    input("Конец (ЧЧ:ММ): ")
                )
                print("Смена добавлена")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "2":
            try:
                update_shift(
                    role,
                    int(input("ID смены: ")),
                    input("Новый ID врача (Enter — не менять): ") or None,
                    input("Новая дата (Enter — не менять): ") or None,
                    input("Новое начало (Enter — не менять): ") or None,
                    input("Новый конец (Enter — не менять): ") or None
                )
                print("Смена обновлена")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "3":
            try:
                delete_shift(role, int(input("ID смены: ")))
                print("Смена удалена (её записи удалены каскадно)")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "4":
            doctors = _safe_doctors_list(role)
            if not doctors:
                print("\nСначала добавьте врачей")
                continue
            for d in doctors:
                print(f"{d[0]}. {d[2]} {d[1]} ({d[5]})")

            print("Типы периода: VACATION, TRAINING, SICK_LEAVE, DAY_OFF")
            try:
                add_period(
                    role,
                    int(input("ID врача: ")),
                    input("Начало (ГГГГ-ММ-ДД): "),
                    input("Конец (ГГГГ-ММ-ДД): "),
                    input("Тип: ").upper()
                )
                print("Период добавлен")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "5":
            try:
                delete_period(role, int(input("ID периода: ")))
                print("Период удалён")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "0":
            break


# -------------------------
# УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ (админ)
# -------------------------
def users_menu(role: str):
    while True:
        print("\n===== Пользователи =====")
        print("1. Добавить пациента")
        print("2. Добавить врача")
        print("3. Удалить пользователя")
        print("0. Назад")

        choice = input("Выберите: ")

        if choice == "1":
            try:
                user_id = register_patient(
                    role,
                    input("Логин: "),
                    input("Пароль: "),
                    input("Имя: "),
                    input("Фамилия: "),
                    input("Отчество: "),
                    input("Дата рождения (ГГГГ-ММ-ДД): "),
                    input("Пол (Enter — пропустить): ") or None,
                    input("Номер полиса (Enter — пропустить): ") or None,
                    input("Телефон (Enter — пропустить): ") or None
                )
                print(f"Пациент создан (user_id = {user_id})")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "2":
            try:
                user_id = register_doctor(
                    role,
                    input("Логин: "),
                    input("Пароль: "),
                    input("Имя: "),
                    input("Фамилия: "),
                    input("Отчество: "),
                    input("Специальность: "),
                    input("Тип графика (Enter — пропустить): ") or None,
                    input("Телефон (Enter — пропустить): ") or None
                )
                print(f"Врач создан (user_id = {user_id})")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "3":
            try:
                delete_user(role, int(input("ID пользователя: ")))
                print("Пользователь удалён")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "0":
            break


# -------------------------
# PATIENT MENU
# -------------------------
def patient_menu(user):
    while True:
        print(f"\n===== Пациент ({user.login}) =====")
        print("1. Расписание врачей (просмотр)")
        print("2. Список врачей")
        print("3. Меню бронирований")
        print("0. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            view_schedule_menu(user.role)

        elif choice == "2":
            try:
                doctors = get_doctors_list(user.role)
                if not doctors:
                    print("\nВрачей нет")
                    continue
                print("\nСписок врачей:")
                for d in doctors:
                    print(f"{d[0]}. {d[2]} {d[1]} {d[3]} | {d[5]}")
            except Exception as e:
                print(f"\nОшибка: {e}")

        elif choice == "3":
            bookings_menu(user)

        elif choice == "0":
            break


# -------------------------
# МЕНЮ БРОНИРОВАНИЙ (пациент)
# -------------------------
def bookings_menu(user):
    while True:
        print("\n===== Бронирования =====")
        print("1. Свободные смены")
        print("2. Записаться к специалисту")
        print("3. Мои записи")
        print("4. Удалить запись")
        print("0. Назад")

        choice = input("Выберите: ")

        if choice == "1":
            try:
                free = get_free_shifts(user.role)
                if not free:
                    print("\nСвободных смен нет")
                    continue
                for row in free:
                    shift_id, doctor_id, name, surname, patronymic, specialty, day, start, end = row
                    print(f"{shift_id}. {surname} {name} ({specialty}) | "
                          f"{day} {start}-{end}")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "2":
            try:
                shift_id = int(input("ID смены: "))
                create_appointment(user.role, user.user_id, shift_id)
                print("Вы записаны на приём")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "3":
            try:
                appointments = get_my_appointments(user.role, user.user_id)
                if not appointments:
                    print("\nУ вас нет записей")
                    continue
                print("\nМои записи:")
                for a in appointments:
                    appointment_id, status, created_at, name, surname, patronymic, \
                        specialty, day, start, end = a
                    print(f"{appointment_id}. {surname} {name} ({specialty}) | "
                          f"{day} {start}-{end} | статус: {status}")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "4":
            try:
                appointment_id = int(input("ID записи: "))
                delete_appointment(user.role, user.user_id, appointment_id)
                print("Запись удалена")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "0":
            break


# -------------------------
# DOCTOR MENU
# -------------------------
def doctor_menu(user):
    while True:
        print(f"\n===== Врач ({user.login}) =====")
        print("1. Расписание врачей (просмотр)")
        print("0. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            view_schedule_menu(user.role)

        elif choice == "0":
            break