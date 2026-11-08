from repositories import users_rep
from repositories import patients_rep
from repositories import doctors_rep
from services.access_control import AccessControl
from services.auth_serv import hash_password
from typing import List, Dict, Any


def register_patient(actor_role: str, login: str, password: str,
                     name: str, surname: str, patronymic: str,
                     birth_date: str, gender: str = None,
                     policy_number: str = None,
                     contact_phone: str = None) -> int:
    """Добавление пациента — только админ. Возвращает user_id."""
    if not AccessControl.can_manage_users(actor_role):
        raise PermissionError("Только администратор может добавлять пользователей")

    if users_rep.get_by_login(login):
        raise Exception("Пользователь уже существует")

    user_id = users_rep.create(
        login=login,
        password_hash=hash_password(password),
        role="PATIENT",
        name=name,
        surname=surname,
        patronymic=patronymic,
        contact_phone=contact_phone,
    )

    patients_rep.create(
        user_id=user_id,
        birth_date=birth_date,
        gender=gender,
        policy_number=policy_number,
        contact_phone=contact_phone,
    )

    return user_id


def register_doctor(actor_role: str, login: str, password: str,
                    name: str, surname: str, patronymic: str,
                    specialty: str, shift_type: str = None,
                    contact_phone: str = None) -> int:
    """Добавление врача — только админ. Возвращает user_id."""
    if not AccessControl.can_manage_users(actor_role):
        raise PermissionError("Только администратор может добавлять пользователей")

    if users_rep.get_by_login(login):
        raise Exception("Пользователь уже существует")

    user_id = users_rep.create(
        login=login,
        password_hash=hash_password(password),
        role="DOCTOR",
        name=name,
        surname=surname,
        patronymic=patronymic,
        contact_phone=contact_phone,
    )

    doctors_rep.create(
        user_id=user_id,
        specialty=specialty,
        shift_type=shift_type,
    )

    return user_id


def delete_user(actor_role: str, user_id: int):
    """Удаление пользователя (пациента/врача) — только админ.

    Благодаря ON DELETE CASCADE вместе с пользователем удалятся его профиль,
    смены, периоды и записи.
    """
    if not AccessControl.can_manage_users(actor_role):
        raise PermissionError("Только администратор может удалять пользователей")

    users_rep.delete(user_id)


def get_doctors_list(actor_role: str):
    """Просмотр списка врачей — админ и пациент."""
    if not AccessControl.can_view_doctors(actor_role):
        raise PermissionError("Нет прав на просмотр списка врачей")

    return users_rep.get_doctors_list()


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