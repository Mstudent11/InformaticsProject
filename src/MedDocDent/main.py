from database.db import get_connection, init_db
from auth import login, show_default_admin_hint
from menu import admin_menu, doctor_menu, patient_menu
from services.auth_serv import create_default_admin


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
    main()