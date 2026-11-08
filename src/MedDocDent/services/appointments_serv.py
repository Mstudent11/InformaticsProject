from repositories import appointments_rep
from repositories import shifts_rep
from models.appointment import Appointment
from services.access_control import AccessControl
from typing import List, Dict, Any


def get_free_shifts(actor_role: str):
    """Свободные смены для записи — только пациент."""
    if not AccessControl.can_book_appointment(actor_role):
        raise PermissionError("Записываться на приём может только пациент")

    return shifts_rep.get_free_shifts()


def create_appointment(actor_role: str, user_id: int, shift_id: int) -> int:
    """Создание записи к специалисту — только пациент.

    Возвращает appointment_id. Смена должна быть свободной
    (в БД есть ограничения по внешним ключам и наличию записи).
    """
    if not AccessControl.can_book_appointment(actor_role):
        raise PermissionError("Записываться на приём может только пациент")

    shift = shifts_rep.get_by_id(shift_id)
    if shift is None:
        raise Exception("Смена не найдена")

    return appointments_rep.create(patient_id=user_id, shift_id=shift_id)


def get_my_appointments(actor_role: str, user_id: int):
    """Записи текущего пациента с данными врача и смены — только пациент."""
    if not AccessControl.can_book_appointment(actor_role):
        raise PermissionError("Меню бронирований доступно только пациенту")

    return appointments_rep.get_by_patient(user_id)


def delete_appointment(actor_role: str, user_id: int, appointment_id: int):
    """Удаление своей записи — только пациент и только своя запись."""
    appointment: Appointment | None = appointments_rep.get_by_id(appointment_id)

    if not appointment:
        raise Exception("Запись не найдена")

    if not AccessControl.can_delete_appointment(actor_role, appointment.patient_id, user_id):
        raise PermissionError("Вы можете удалять только свои записи")

    appointments_rep.delete(appointment_id)


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