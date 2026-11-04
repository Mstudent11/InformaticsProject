from src.MedDocDent.repositories import users_rep
from src.MedDocDent.repositories import patients_rep
from src.MedDocDent.repositories import doctors_rep
from src.MedDocDent.services.access_control import AccessControl
from src.MedDocDent.services.auth_serv import hash_password


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