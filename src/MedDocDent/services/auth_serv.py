import hashlib

from repositories import users_rep
from models.users import User


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate(login: str, password: str) -> User | None:
    """Вход в систему для любого пользователя. Возвращает объект User или None."""
    user = users_rep.get_by_login(login)

    if not user:
        return None

    if user.password_hash != hash_password(password):
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