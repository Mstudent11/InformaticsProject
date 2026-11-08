import hashlib

from repositories import users_rep
from models.users import User
from typing import List, Dict, Any


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


def list_available_for_role(self, role: str) -> List[Dict[str, Any]]:
    """
    Возвращает список записей, доступных для данной роли.
    ADMIN: видит всё.
    DOCTOR: видит только свои данные (по doctor_id / user_id).
    PATIENT: видит только свои записи.
    """
    all_rows = self.repository.get_all_rows()
    result = []

    for row in all_rows:
        row_dict = dict(row)  # sqlite3.Row -> dict
        if role == "ADMIN":
            # Админ видит всё
            result.append(row_dict)
            continue

        elif role == "DOCTOR":
            # Врач: показываем только то, где doctor_id совпадает с его user_id
            # Если в таблице doctors есть поле user_id — используй его.
            doctor_id_in_row = row_dict.get("doctor_id") or row_dict.get("user_id")
            if doctor_id_in_row is not None:
                # Сравниваем с текущим user_id врача (его нужно передать в сервис или хранить в сессии)
                # Для примера: self.current_user_id (добавь как атрибут в сервис при логине)
                if doctor_id_in_row == self.current_user_id:
                    result.append(row_dict)
            else:
                result.append(row_dict)  # fallback: если нет doctor_id, показываем всё
            continue

        elif role == "PATIENT":                # Пациент: показываем только свои записи
            patient_id_in_row = row_dict.get("patient_id") or row_dict.get("user_id")
            if patient_id_in_row is not None and patient_id_in_row == self.current_user_id:
                result.append(row_dict)
            elif patient_id_in_row is None:
                    # Если это таблица пациентов, и там нет patient_id, но есть user_id:
                user_id_in_row = row_dict.get("user_id")
                if user_id_in_row == self.current_user_id:
                    result.append(row_dict)
            continue

    return result