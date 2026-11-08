from services.users_serv import (
    register_patient,
    register_doctor,
    delete_user,
    get_doctors_list
    get_all_users,
    get_all_patients,
    get_all_doctors,
)

from services.schedule_serv import (
    get_full_schedule,
    get_doctor_schedule,
    add_shift,
    update_shift,
    delete_shift,
    add_period,
    get_doctor_periods,
    delete_period
    get_all_shifts,
)

from services.appointments_serv import (
    get_free_shifts,
    create_appointment,
    get_my_appointments,
    delete_appointment
)
from utils import print_table  # импорт нашей красивой таблицы

def show_appointments_for_user(appointments_service, current_role):
    """
    Показывает доступные записи на приём с учётом прав доступа.
    Возвращает список записей, чтобы можно было дополнительно проверить ID.
    """
    available = appointments_service.list_available_for_role(current_role)
    print("\n--- Доступные записи на приём ---")
    # Укажи только нужные колонки, чтобы таблица была компактной
    columns = ["appointment_id", "patient_id", "shift_id", "status", "created_at"]
    print_table(available, columns=columns)
    return available

def show_doctors_for_user(doctors_service, current_role):
    available = doctors_service.list_available_for_role(current_role)
    print("\n--- Список врачей ---")
    columns = ["user_id", "specialty", "shift_type"]
    print_table(available, columns=columns)
    return available

def show_patients_for_user(patients_service, current_role):
    available = patients_service.list_available_for_role(current_role)
    print("\n--- Список пациентов ---")
    columns = ["user_id", "name", "surname", "birth_date", "policy_number"]
    print_table(available, columns=columns)
    return available


def print_table(title, headers, rows):
    """Выводит таблицу в консоль с выравниванием колонок."""
    print(f"\n=== {title} ===")
    if not rows:
        print("(пусто)")
        return

    # Вычисляем ширину колонок по заголовкам и данным
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    # Строка разделителя
    separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

    def format_row(row_values):
        return "|" + "|".join(f" {str(v):<{w}} " for v, w in zip(row_values, col_widths)) + "|"

    print(separator)
    print(format_row(headers))
    print(separator)
    for r in rows:
        print(format_row(r))
    print(separator)


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
                # Превращаем кортежи в словари (ключи подбери под реальные названия колонок в БД)
                schedule_dicts = [
                    {
                        "shift_id": r[0],
                        "doctor_id": r[1],
                        "name": r[2],
                        "surname": r[3],
                        "patronymic": r[4],
                        "specialty": r[5],
                        "day": r[6],
                        "start": r[7],
                        "end": r[8],
                    }
                    for r in schedule
                ]

                print("\nСмены:")
                print_table(
                    schedule_dicts,
                    columns=["shift_id", "surname", "name", "specialty", "day", "start", "end"]
                )
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
                shifts_dicts = [
                    {"shift_id": s.shift_id, "day_date": s.day_date, "start_time": s.start_time, "end_time": s.end_time}
                    for s in shifts
                ]
                print("\nСмены врача:")
                print_table(shifts_dicts, columns=["shift_id", "day_date", "start_time", "end_time"])
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
                periods_dicts = [
                    {"period_id": p.period_id, "type": p.type, "start_date": p.start_date, "end_date": p.end_date}
                    for p in periods
                ]
                print("\nПериоды:")
                print_table(periods_dicts, columns=["period_id", "type", "start_date", "end_date"])
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
        # Новые пункты для просмотра таблиц
        print("5. Все пользователи (таблица)")
        print("6. Все пациенты (таблица)")
        print("7. Все врачи (таблица)")
        print("8. Все смены (таблица)")
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
                rows = [(d[0], d[2], d[1], d[3], d[5], d[4]) for d in doctors]
                print_table("Список врачей",
                            ["ID", "Фамилия", "Имя", "Отчество", "Специальность", "Телефон"],
                            rows)
            except Exception as e:
                print(f"\nОшибка: {e}")

        elif choice == "5":
            users = get_all_users()
            print_table("Все пользователи",
                        ["User ID", "Логин", "Роль", "ФИО", "Телефон"],
                        [(u[0], u[1], u[2], f"{u[3]} {u[4]} {u[5]}", u[6] or "—") for u in users])

        elif choice == "6":
            patients = get_all_patients()
            print_table("Пациенты",
                        ["User ID", "ФИО", "Дата рождения", "Пол", "Полис", "Телефон"],
                        [(p[0], f"{p[1]} {p[2]} {p[3]}", p[4], p[5] or "—", p[6] or "—", p[7] or "—") for p in patients])

        elif choice == "7":
            doctors = get_all_doctors()
            print_table("Врачи",
                        ["User ID", "ФИО", "Специальность", "Тип графика"],
                        [(d[0], f"{d[1]} {d[2]} {d[3]}", d[4], d[5] or "—") for d in doctors])

        elif choice == "8":
            shifts = get_all_shifts()
            print_table("Все смены",
                        ["Shift ID", "Дата", "Начало", "Конец", "Врач", "Специальность"],
                        shifts)

        elif choice == "0":
            break


# -------------------------
# РЕДАКТИРОВАНИЕ РАСПИСАНИЯ (админ)
# -------------------------
def schedule_edit_menu(role: str):
    while True:
        print("\n===== Редактирование расписания =====")
        print("1. Добавить смену")
        print("2. Изменить смену (с показом всех смен)")
        print("3. Удалить смену (с показом всех смен)")
        print("4. Добавить период (отпуск/обучение)")
        print("5. Удалить период (с показом периодов)")
        print("0. Назад")

        choice = input("Выберите: ")

        if choice == "1":
            # Перед добавлением покажем врачей, чтобы выбрать ID
            doctors = _safe_doctors_list(role)
            if not doctors:
                print("\nСначала добавьте врачей")
                continue
            print_table("Врачи (для выбора doctor_id)",
                        ["ID", "Фамилия", "Имя", "Отчество", "Специальность"],
                        [(d[0], d[2], d[1], d[3], d[5]) for d in doctors])

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
            shifts = get_all_shifts()
            print_table("Все смены (для выбора shift_id)",
                        ["Shift ID", "Дата", "Начало", "Конец", "Врач", "Специальность"],
                        shifts)
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
            shifts = get_all_shifts()
            print_table("Все смены (для удаления)",
                        ["Shift ID", "Дата", "Начало", "Конец", "Врач", "Специальность"],
                        shifts)
            try:
                delete_shift(role, int(input("ID смены для удаления: ")))
                print("Смена удалена (её записи удалены каскадно)")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "4":
            doctors = _safe_doctors_list(role)
            if not doctors:
                print("\nСначала добавьте врачей")
                continue
            print_table("Врачи (для выбора doctor_id)",
                        ["ID", "Фамилия", "Имя", "Отчество", "Специальность"],
                        [(d[0], d[2], d[1], d[3], d[5]) for d in doctors])

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
            # Для удаления периода сначала нужно показать периоды (по врачу)
            doctors = _safe_doctors_list(role)
            if not doctors:
                print("\nВрачей нет")
                continue
            print_table("Врачи (чтобы выбрать doctor_id)",
                        ["ID", "Фамилия", "Имя", "Отчество", "Специальность"],
                        [(d[0], d[2], d[1], d[3], d[5]) for d in doctors])
            try:
                doctor_id = int(input("ID врача для показа периодов: "))
                periods = get_doctor_periods(role, doctor_id)
                if not periods:
                    print("\nПериодов нет")
                    continue
                # Переводим объекты в кортежи для print_table
                rows = [(p.period_id, p.type, p.start_date, p.end_date) for p in periods]
                print_table(f"Периоды врача {doctor_id}",
                            ["Period ID", "Тип", "Начало", "Конец"],
                            rows)
                delete_period(role, int(input("ID периода для удаления: ")))
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
        print("3. Удалить пользователя (с показом таблицы)")
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
            users = get_all_users()
            print_table("Все пользователи (для выбора user_id)",
                        ["User ID", "Логин", "Роль", "ФИО", "Телефон"],
                        [(u[0], u[1], u[2], f"{u[3]} {u[4]} {u[5]}", u[6] or "—") for u in users])
            try:
                delete_user(role, int(input("ID пользователя для удаления: ")))
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
        print("4. Свободные смены (таблица)")
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
                rows = [(d[0], d[2], d[1], d[3], d[5]) for d in doctors]
                print_table("Список врачей",
                            ["ID", "Фамилия", "Имя", "Отчество", "Специальность"],
                            rows)
            except Exception as e:
                print(f"\nОшибка: {e}")

        elif choice == "3":
            bookings_menu(user)

        elif choice == "4":
            free = get_free_shifts(user.role)
            if not free:
                print("\nСвободных смен нет")
                continue
            rows = [(f.shift_id, f.day_date, f.start_time, f.end_time, f.surname, f.name, f.specialty) for f in free]
            print_table("Свободные смены",
                        ["Shift ID", "Дата", "Начало", "Конец", "Врач", "Специальность"],
                        rows)

        elif choice == "0":
            break


# -------------------------
# DOCTOR MENU
# -------------------------
def doctor_menu(user):
    while True:
        print(f"\n===== Врач ({user.login}) =====")
        print("1. Расписание врачей (просмотр)")
        print("2. Все смены клиники (таблица)")
        print("0. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            view_schedule_menu(user.role)

        elif choice == "2":
            shifts = get_all_shifts()
            print_table("Все смены клиники",
                        ["Shift ID", "Дата", "Начало", "Конец", "Врач", "Специальность"],
                        shifts)

        elif choice == "0":
            break


# -------------------------
# МЕНЮ БРОНИРОВАНИЙ (пациент)
# -------------------------
def bookings_menu(user):
    while True:
        print("\n===== Бронирования =====")
        print("1. Свободные смены (таблица)")
        print("2. Записаться к специалисту (после показа смен)")
        print("3. Мои записи")
        print("4. Удалить запись (после показа моих записей)")
        print("0. Назад")

        choice = input("Выберите: ")

        if choice == "1":
            free = get_free_shifts(user.role)
            if not free:
                print("\nСвободных смен нет")
                continue
            rows = [(f.shift_id, f.day_date, f.start_time, f.end_time, f.surname, f.name, f.specialty) for f in free]
            print_table("Свободные смены",
                        ["Shift ID", "Дата", "Начало", "Конец", "Врач", "Специальность"],
                        rows)

        elif choice == "2":
            free = get_free_shifts(user.role)
            if not free:
                print("\nСвободных смен нет")
                continue
            rows = [(f.shift_id, f.day_date, f.start_time, f.end_time, f.surname, f.name, f.specialty) for f in free]
            print_table("Свободные смены (выберите shift_id для записи)",
                        ["Shift ID", "Дата", "Начало", "Конец", "Врач", "Специальность"],
                        rows)
            try:
        elif choice == "2":
            free = get_free_shifts(user.role)
            if not free:
                print("\nСвободных смен нет")
                continue
            rows = [(f.shift_id, f.day_date, f.start_time, f.end_time, f.surname, f.name, f.specialty) for f in free]
            print_table("Свободные смены (выберите shift_id для записи)",
                        ["Shift ID", "Дата", "Начало", "Конец", "Врач", "Специальность"],
                        rows)
            try:
                shift_id = int(input("ID смены для записи: "))
                create_appointment(user.role, user.user_id, shift_id)
                print("Вы записаны на приём")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "3":
            appointments = get_my_appointments(user.role, user.user_id)
            if not appointments:
                print("\nУ вас нет записей")
                continue
            # Преобразуем объекты в кортежи для print_table
            rows = [
                (a.appointment_id, a.status, a.created_at,
                 f"{a.surname} {a.name}", a.specialty, a.day, a.start_time, a.end_time)
                for a in appointments
            ]
            print_table("Мои записи",
                        ["App. ID", "Статус", "Создано", "Врач", "Спец.", "Дата", "Время"],
                        rows)

        elif choice == "4":
            appointments = get_my_appointments(user.role, user.user_id)
            if not appointments:
                print("\nУ вас нет записей")
                continue
            rows = [
                (a.appointment_id, a.status,
                 f"{a.surname} {a.name}", a.day, a.start_time, a.end_time)
                for a in appointments
            ]
            print_table("Мои записи (выберите App. ID для удаления)",
                        ["App. ID", "Статус", "Врач", "Дата", "Время"],
                        rows)
            try:
                appointment_id = int(input("ID записи для удаления: "))
                delete_appointment(user.role, user.user_id, appointment_id)
                print("Запись удалена")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "0":
            break



