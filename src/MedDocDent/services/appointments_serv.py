from src.MedDocDent.repositories import appointments_rep
from src.MedDocDent.repositories import shifts_rep
from src.MedDocDent.models.appointment import Appointment
from src.MedDocDent.services.access_control import AccessControl


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