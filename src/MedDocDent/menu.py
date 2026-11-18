from services.users_serv import (
    register_patient,
    register_doctor,
    delete_user,
    get_doctors_list,
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
    delete_period,
    get_all_shifts,
)

from services.appointments_serv import (
    get_free_shifts,
    create_appointment,
    get_my_appointments,
    delete_appointment,
)

from services.info_serv import (
    get_doctor_full_info,
    get_patient_full_info,
    get_appointment_full_info,
    get_shift_full_info,
)

from utils import print_table


def print_info_blocks(blocks):
    """Печатает блоки полной информации о сущности (с учётом прав доступа)."""
    if not blocks:
        print("\nИнформация не найдена")
        return
    for title, headers, rows in blocks:
        print_table(title, headers, rows)


def _free_shifts_rows(free):
    """Кортежи get_free_shifts -> строки для таблицы."""
    return [(f[0], f[6], f[7], f[8], f"{f[3]} {f[2]} {f[4]}", f[5]) for f in free]


def _doctors_rows(doctors):
    return [(d[0], d[2], d[1], d[3], d[5]) for d in doctors]


# -------------------------
# ОБЩЕЕ: ПРОСМОТР РАСПИСАНИЯ
# -------------------------
def view_schedule_menu(user):
    """Просмотр расписания врачей — доступно всем ролям."""
    role = user.role

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
                rows = [
                    (r[0], f"{r[3]} {r[2]} {r[4]}", r[5], r[6], r[7], r[8])
                    for r in schedule
                ]
                print_table(
                    "Все смены",
                    ["Shift ID", "Врач", "Специальность", "Дата", "Начало", "Конец"],
                    rows,
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
            print_table(
                "Врачи (для выбора doctor_id)",
                ["ID", "Фамилия", "Имя", "Отчество", "Специальность"],
                _doctors_rows(doctors),
            )
            try:
                doctor_id = int(input("ID врача: "))
                # Полная информация о враче перед показом смен
                print_info_blocks(get_doctor_full_info(role, user.user_id, doctor_id))
                shifts = get_doctor_schedule(role, doctor_id)
                if shifts:
                    print_table(
                        "Смены врача",
                        ["Shift ID", "Дата", "Начало", "Конец"],
                        [(s.shift_id, s.day_date, s.start_time, s.end_time) for s in shifts],
                    )
                else:
                    print("\nУ этого врача нет смен")
            except Exception as e:
                print(f"\nОшибка: {e}")

        elif choice == "3":
            doctors = _safe_doctors_list(role)
            if doctors is None:
                continue
            if not doctors:
                print("\nВрачей нет")
                continue
            print_table(
                "Врачи (для выбора doctor_id)",
                ["ID", "Фамилия", "Имя", "Отчество", "Специальность"],
                _doctors_rows(doctors),
            )
            try:
                doctor_id = int(input("ID врача: "))
                print_info_blocks(get_doctor_full_info(role, user.user_id, doctor_id))
                periods = get_doctor_periods(role, doctor_id)
                if periods:
                    print_table(
                        "Периоды врача",
                        ["Period ID", "Тип", "Начало", "Конец"],
                        [(p.period_id, p.type, p.start_date, p.end_date) for p in periods],
                    )
                else:
                    print("\nПериодов нет")
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
        print("5. Все пользователи (таблица)")
        print("6. Все пациенты (таблица)")
        print("7. Все врачи (таблица)")
        print("8. Все смены (таблица)")
        print("9. Экспорт таблицы (JSON/CSV/XML/YAML)")
        print("0. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            view_schedule_menu(user)

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
                print_table(
                    "Список врачей",
                    ["ID", "Фамилия", "Имя", "Отчество", "Специальность", "Телефон"],
                    [(d[0], d[2], d[1], d[3], d[5], d[4] or "—") for d in doctors],
                )
            except Exception as e:
                print(f"\nОшибка: {e}")

        elif choice == "5":
            users = get_all_users()
            print_table(
                "Все пользователи",
                ["User ID", "Логин", "Роль", "ФИО", "Телефон"],
                [(u[0], u[1], u[2], f"{u[3]} {u[4]} {u[5]}", u[6] or "—") for u in users],
            )

        elif choice == "6":
            patients = get_all_patients()
            print_table(
                "Пациенты",
                ["User ID", "ФИО", "Дата рождения", "Пол", "Полис", "Телефон"],
                [(p[0], f"{p[1]} {p[2]} {p[3]}", p[4], p[5] or "—", p[6] or "—", p[7] or "—") for p in patients],
            )

        elif choice == "7":
            doctors = get_all_doctors()
            print_table(
                "Врачи",
                ["User ID", "ФИО", "Специальность", "Тип графика"],
                [(d[0], f"{d[1]} {d[2]} {d[3]}", d[4], d[5] or "—") for d in doctors],
            )

        elif choice == "8":
            shifts = get_all_shifts()
            print_table(
                "Все смены",
                ["Shift ID", "Дата", "Начало", "Конец", "Фамилия", "Имя", "Специальность"],
                shifts,
            )
        elif choice == "9":
            export_menu(user.role)

        elif choice == "0":
            break

def export_menu(role: str):
    """Экспорт выбранной таблицы в JSON/CSV/XML/YAML — только админ."""
    from services.export_serv import export_table, list_tables

    if role != "ADMIN":
        print("\nЭкспорт доступен только администратору")
        return

    while True:
        tables = list_tables()
        print("\n===== Экспорт таблицы =====")
        print("Доступные таблицы:")
        for i, t in enumerate(tables, 1):
            print(f"{i}. {t}")
        print("0. Назад")

        choice = input("Введите номер таблицы: ").strip()

        if choice == "0":
            break

        if choice.isdigit() and 1 <= int(choice) <= len(tables):
            try:
                out_dir = export_table(tables[int(choice) - 1])
                print("\nЭкспорт завершён. Файлы созданы в папке out:")
                print(f"  {out_dir / 'data.json'}")
                print(f"  {out_dir / 'data.csv'}")
                print(f"  {out_dir / 'data.xml'}")
                print(f"  {out_dir / 'data.yaml'}")
            except Exception as e:
                print(f"Ошибка: {e}")
        else:
            print("Неверный выбор")
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
            doctors = _safe_doctors_list(role)
            if not doctors:
                print("\nСначала добавьте врачей")
                continue
            print_table(
                "Врачи (для выбора doctor_id)",
                ["ID", "Фамилия", "Имя", "Отчество", "Специальность"],
                _doctors_rows(doctors),
            )
            try:
                add_shift(
                    role,
                    int(input("ID врача: ")),
                    input("Дата (ГГГГ-ММ-ДД): "),
                    input("Начало (ЧЧ:ММ): "),
                    input("Конец (ЧЧ:ММ): "),
                )
                print("Смена добавлена")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "2":
            shifts = get_all_shifts()
            print_table(
                "Все смены (для выбора shift_id)",
                ["Shift ID", "Дата", "Начало", "Конец", "Фамилия", "Имя", "Специальность"],
                shifts,
            )
            try:
                shift_id = int(input("ID смены: "))
                # Полная информация о смене и её записях перед изменением
                print_info_blocks(get_shift_full_info(role, None, shift_id))

                doctor_input = input("Новый ID врача (Enter — не менять): ")
                update_shift(
                    role,
                    shift_id,
                    int(doctor_input) if doctor_input.strip() else None,
                    input("Новая дата (Enter — не менять): ") or None,
                    input("Новое начало (Enter — не менять): ") or None,
                    input("Новый конец (Enter — не менять): ") or None,
                )
                print("Смена обновлена")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "3":
            shifts = get_all_shifts()
            print_table(
                "Все смены (для удаления)",
                ["Shift ID", "Дата", "Начало", "Конец", "Фамилия", "Имя", "Специальность"],
                shifts,
            )
            try:
                shift_id = int(input("ID смены для удаления: "))
                print_info_blocks(get_shift_full_info(role, None, shift_id))
                confirm = input("Удалить эту смену вместе с её записями? (y/n): ")
                if confirm.strip().lower() == "y":
                    delete_shift(role, shift_id)
                    print("Смена удалена (её записи удалены каскадно)")
                else:
                    print("Удаление отменено")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "4":
            doctors = _safe_doctors_list(role)
            if not doctors:
                print("\nСначала добавьте врачей")
                continue
            print_table(
                "Врачи (для выбора doctor_id)",
                ["ID", "Фамилия", "Имя", "Отчество", "Специальность"],
                _doctors_rows(doctors),
            )

            print("Типы периода: VACATION, TRAINING, SICK_LEAVE, DAY_OFF")
            try:
                add_period(
                    role,
                    int(input("ID врача: ")),
                    input("Начало (ГГГГ-ММ-ДД): "),
                    input("Конец (ГГГГ-ММ-ДД): "),
                    input("Тип: ").upper(),
                )
                print("Период добавлен")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "5":
            doctors = _safe_doctors_list(role)
            if not doctors:
                print("\nВрачей нет")
                continue
            print_table(
                "Врачи (чтобы выбрать doctor_id)",
                ["ID", "Фамилия", "Имя", "Отчество", "Специальность"],
                _doctors_rows(doctors),
            )
            try:
                doctor_id = int(input("ID врача для показа периодов: "))
                periods = get_doctor_periods(role, doctor_id)
                if not periods:
                    print("\nПериодов нет")
                    continue
                print_table(
                    f"Периоды врача {doctor_id}",
                    ["Period ID", "Тип", "Начало", "Конец"],
                    [(p.period_id, p.type, p.start_date, p.end_date) for p in periods],
                )
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
                    input("Телефон (Enter — пропустить): ") or None,
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
                    input("Телефон (Enter — пропустить): ") or None,
                )
                print(f"Врач создан (user_id = {user_id})")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "3":
            users = get_all_users()
            print_table(
                "Все пользователи (для выбора user_id)",
                ["User ID", "Логин", "Роль", "ФИО", "Телефон"],
                [(u[0], u[1], u[2], f"{u[3]} {u[4]} {u[5]}", u[6] or "—") for u in users],
            )
            try:
                user_id = int(input("ID пользователя для удаления: "))
                # Полная информация о пользователе перед удалением
                blocks = None
                try:
                    blocks = get_patient_full_info(role, None, user_id)
                except PermissionError:
                    pass
                if blocks is None:
                    try:
                        blocks = get_doctor_full_info(role, None, user_id)
                    except Exception:
                        pass
                print_info_blocks(blocks)
                delete_user(role, user_id)
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
            view_schedule_menu(user)

        elif choice == "2":
            try:
                doctors = get_doctors_list(user.role)
                if not doctors:
                    print("\nВрачей нет")
                    continue
                print_table(
                    "Список врачей",
                    ["ID", "Фамилия", "Имя", "Отчество", "Специальность"],
                    _doctors_rows(doctors),
                )
            except Exception as e:
                print(f"\nОшибка: {e}")

        elif choice == "3":
            bookings_menu(user)

        elif choice == "4":
            try:
                free = get_free_shifts(user.role)
                if not free:
                    print("\nСвободных смен нет")
                    continue
                print_table(
                    "Свободные смены",
                    ["Shift ID", "Дата", "Начало", "Конец", "Врач", "Специальность"],
                    _free_shifts_rows(free),
                )
            except Exception as e:
                print(f"\nОшибка: {e}")

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
            view_schedule_menu(user)

        elif choice == "2":
            shifts = get_all_shifts()
            print_table(
                "Все смены клиники",
                ["Shift ID", "Дата", "Начало", "Конец", "Фамилия", "Имя", "Специальность"],
                shifts,
            )

        elif choice == "0":
            break


# -------------------------
# МЕНЮ БРОНИРОВАНИЙ (пациент)
# -------------------------
def bookings_menu(user):
    role = user.role

    while True:
        print("\n===== Бронирования =====")
        print("1. Свободные смены (таблица)")
        print("2. Записаться к специалисту")
        print("3. Мои записи")
        print("4. Удалить запись")
        print("0. Назад")

        choice = input("Выберите: ")

        if choice == "1":
            free = get_free_shifts(role)
            if not free:
                print("\nСвободных смен нет")
                continue
            print_table(
                "Свободные смены",
                ["Shift ID", "Дата", "Начало", "Конец", "Врач", "Специальность"],
                _free_shifts_rows(free),
            )

        elif choice == "2":
            free = get_free_shifts(role)
            if not free:
                print("\nСвободных смен нет")
                continue
            print_table(
                "Свободные смены (выберите shift_id)",
                ["Shift ID", "Дата", "Начало", "Конец", "Врач", "Специальность"],
                _free_shifts_rows(free),
            )
            try:
                shift_id_input = input("ID смены для записи: ")
                if not shift_id_input.isdigit():
                    print("Некорректный ID")
                    continue
                shift_id = int(shift_id_input)
                # Информация о смене и враче перед записью
                print_info_blocks(get_shift_full_info(role, user.user_id, shift_id))
                create_appointment(role, user.user_id, shift_id)
                print("Вы записаны на приём")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "3":
            try:
                appointments = get_my_appointments(role, user.user_id)
                if not appointments:
                    print("\nУ вас нет записей")
                    continue
                rows = [
                    (a[0], a[1], a[2], f"{a[4]} {a[3]} {a[5]}", a[6], a[7], a[8], a[9])
                    for a in appointments
                ]
                print_table(
                    "Мои записи",
                    ["App. ID", "Статус", "Создано", "Врач", "Спец.", "Дата", "Начало", "Конец"],
                    rows,
                )
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "4":
            try:
                appointments = get_my_appointments(role, user.user_id)
                if not appointments:
                    print("\nУ вас нет записей")
                    continue
                rows = [
                    (a[0], a[1], a[2], f"{a[4]} {a[3]} {a[5]}", a[6], a[7], a[8], a[9])
                    for a in appointments
                ]
                print_table(
                    "Мои записи (выберите appointment_id)",
                    ["App. ID", "Статус", "Создано", "Врач", "Спец.", "Дата", "Начало", "Конец"],
                    rows,
                )
                appointment_id_input = input("ID записи для удаления: ")
                if not appointment_id_input.isdigit():
                    print("Некорректный ID")
                    continue
                appointment_id = int(appointment_id_input)
                # Полная информация о записи перед удалением
                print_info_blocks(get_appointment_full_info(role, user.user_id, appointment_id))
                confirm = input("Удалить эту запись? (y/n): ")
                if confirm.strip().lower() == "y":
                    delete_appointment(role, user.user_id, appointment_id)
                    print("Запись удалена")
                else:
                    print("Удаление отменено")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "0":
            break

'''from services.users_serv import (
    register_patient,
    register_doctor,
    delete_user,
    get_doctors_list,
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
    delete_period,
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
    
    # Проверка: все строки должны иметь столько же колонок, сколько заголовков
    expected_cols = len(headers)
    for i, row in enumerate(rows):
        if len(row) != expected_cols:
            raise ValueError(
                f"Несовпадение колонок: строка {i} имеет {len(row)} колонок, "
                f"а заголовков — {expected_cols}. Строка: {row}"
            )


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
            
            # Конвертируем кортежи в список словарей (ключи должны совпадать с логикой БД)
            free_dicts = [
                {
                    "shift_id": f[0],
                    "day_date": f[6],
                    "start_time": f[7],
                    "end_time": f[8],
                    "surname": f[2],
                    "name": f[3],
                    "specialty": f[5],
                }
                for f in free
            ]
            
            rows = [
                (d["shift_id"], d["day_date"], d["start_time"], d["end_time"], d["surname"], d["name"], d["specialty"])
                for d in free_dicts
            ]

            print_table("Свободные смены",
                        ["Shift ID", "Дата", "Начало", "Конец", "Врач", "Специальность"],
                        rows)
            
        elif choice == "2":
            free = get_free_shifts(user.role)
            if not free:
                print("\nСвободных смен нет")
                continue

            # То же самое преобразование
            free_dicts = [
                {
                    "shift_id": f[0],
                    "day_date": f[1],
                    "start_time": f[2],
                    "end_time": f[3],
                    "surname": f[4],
                    "specialty": f[5],
                }
                for f in free
            ]

            rows = [
                (d["shift_id"], d["day_date"], d["start_time"], d["end_time"], d["surname"], d["specialty"])
                for d in free_dicts
            ]

            print_table("Свободные смены (выберите shift_id для записи)",
                        ["Shift ID", "Дата", "Начало", "Конец", "Врач", "Специальность"],
                        rows)

            try:
                shift_id_input = input("ID смены для записи: ")
                if not shift_id_input.isdigit():
                    print("Некорректный ID")
                    continue
                
                shift_id = int(shift_id_input)
                create_appointment(user.role, user.user_id, shift_id)
                print("Вы записаны на приём")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "3":
            appointments = get_my_appointments(user.role, user.user_id)
            if not appointments:
                print("\nУ вас нет записей")
                continue

            # Здесь тоже используем индексы, так как get_my_appointments возвращает кортежи
            rows = []
            for a in appointments:
                # Подставь сюда реальные индексы из твоего SQL-запроса в сервисе
                appointment_id = a[0]
                status = a[1]
                created_at = a[2]
                surname = a[3]
                specialty = a[4]
                day = a[5]
                start_time = a[6]
                end_time = a[7]

                rows.append((
                    appointment_id,
                    status,
                    created_at,
                    f"{surname}",
                    specialty,
                    day,
                    start_time,
                    end_time
                ))

            print_table("Мои записи",
                        ["App. ID", "Статус", "Создано", "Врач", "Спец.", "Дата", "Время"],
                        rows)

        elif choice == "4":
            appointments = get_my_appointments(user.role, user.user_id)
            if not appointments:
                print("\nУ вас нет записей")
                continue

            rows = []
            for a in appointments:
                # Подставь сюда реальные индексы из твоего SQL-запроса в сервисе
                appointment_id = a[0]
                status = a[1]
                created_at = a[2]
                name = a[3]
                specialty = a[4]
                day = a[5]
                start_time = a[6]
                end_time = a[7]

                rows.append((
                    appointment_id,
                    status,
                    created_at,
                    f" {surname}",
                    specialty,
                    day,
                    start_time,
                    end_time
                ))

            print_table("Мои записи",
                        ["App. ID", "Статус", "Создано", "Врач", "Спец.", "Дата", "Время"],
                        rows)

            try:
                appointment_id_input = input("ID записи для удаления: ")
                if not appointment_id_input.isdigit():
                    print("Некорректный ID")
                    continue
                appointment_id = int(appointment_id_input)
                delete_appointment(user.role, user.user_id, appointment_id)
                print("Запись удалена")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "0":
            break'''


