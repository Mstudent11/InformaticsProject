import hashlib

from repositories import users_rep
from models.users import User


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate(login: str, password: str) -> User | None:
    print("=== ЗАГРУЖЕН auth_serv:", __file__, "===")
    user = users_rep.get_by_login(login)

    print(f"[DEBUG] Ищем логин: {login!r}, найдено: {user is not None}")

    if not user:
        return None

    print(f"[DEBUG] В базе: {user.password_hash!r}")
    print(f"[DEBUG] Ввели:  {password!r}")

    if user.password_hash != password:
        print("[DEBUG] Не совпали")
        return None

    return user


def create_default_admin():
    """Создаёт администратора по умолчанию (admin / admin), если его ещё нет."""
    if users_rep.get_by_login("admin"):
        return

    users_rep.create(
        login="admin",
        password_hash=hash_password("admin"),
        role="ADMIN",
        name="System",
        surname="Admin",
        patronymic="Admin",
    )