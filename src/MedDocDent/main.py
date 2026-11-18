from database.db import init_db
from auth import login, show_default_admin_hint
from menu import admin_menu, doctor_menu, patient_menu
from services.auth_serv import create_default_admin


def main():
    init_db()
    # Админ по умолчанию (admin / admin) — если его ещё нет
    create_default_admin()
    show_default_admin_hint()

    while True:
        print("\n===== Поликлиника =====")
        print("1. Вход")
        print("0. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            user = login()
            if not user:
                continue

            if user.role == "ADMIN":
                admin_menu(user)
            elif user.role == "DOCTOR":
                doctor_menu(user)
            elif user.role == "PATIENT":
                patient_menu(user)

        elif choice == "0":
            print("До свидания!")
            break

        else:
            print("Неверный выбор")


if __name__ == "__main__":
    main()

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

''' from database.db import get_connection, init_db
from auth import login, show_default_admin_hint
from menu import admin_menu, doctor_menu, patient_menu
from services.auth_serv import create_default_admin
from utils import print_table


def main():
    # Проверяем, что база доступна (таблицы созданы через schema.sql)
    conn = get_connection()
    conn.close()
    init_db()
    # Создаём админа по умолчанию (admin / admin), если его нет
    create_default_admin()

    while True:
        print("=== ЗАПУЩЕН ЭТОТ ФАЙЛ:", __file__, "===")
        print("\n===== Поликлиника =====")
        print("1. Вход")
        print("0. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            user = login()

            if not user:
                continue

            if user.role == "ADMIN":
                admin_menu(user)
            elif user.role == "DOCTOR":
                doctor_menu(user)
            elif user.role == "PATIENT":
                patient_menu(user)

        elif choice == "0":
            print("До свидания!")
            break

        else:
            print("Неверный выбор")


if __name__ == "__main__":
    main()'''