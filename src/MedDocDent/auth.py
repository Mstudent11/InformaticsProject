'''from services.auth_serv import authenticate, create_default_admin


def login():
    """Вход в систему — доступен всем ролям."""
    print("\n=== Авторизация ===")

    login_value = input("Логин: ")
    password_value = input("Пароль: ")

    user = authenticate(login_value, password_value)

    if not user:
        print("\nНеверный логин или пароль")
        return None

    print(f"\nДобро пожаловать, {user.name} {user.surname} (роль: {user.role})")
    return user


def show_default_admin_hint():
    """Создаёт админа по умолчанию и напоминает его данные."""
    create_default_admin()
    print("Админ по умолчанию: логин admin, пароль admin")'''


from services.auth_serv import authenticate


def login():
    """Вход в систему — доступен всем ролям."""
    print("\n=== Авторизация ===")

    login_value = input("Логин: ")
    password_value = input("Пароль: ")

    user = authenticate(login_value, password_value)

    if not user:
        print("\nНеверный логин или пароль")
        return None

    print(f"\nДобро пожаловать, {user.name} {user.surname} (роль: {user.role})")
    return user


def show_default_admin_hint():
    print("Админ по умолчанию: логин admin, пароль admin")