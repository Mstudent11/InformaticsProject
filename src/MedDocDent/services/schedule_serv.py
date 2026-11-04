from src.MedDocDent.repositories import shifts_rep
from src.MedDocDent.repositories import schedule_periods_rep
from src.MedDocDent.models.shifts import Shift
from src.MedDocDent.models.schedule_periods import SchedulePeriod
from src.MedDocDent.services.access_control import AccessControl


# ---------- Просмотр (все роли) ----------

def get_full_schedule(actor_role: str):
    """Расписание всех врачей — доступно всем ролям."""
    if not AccessControl.can_view_schedule(actor_role):
        raise PermissionError("Нет прав на просмотр расписания")

    return shifts_rep.get_full_schedule()


def get_doctor_schedule(actor_role: str, doctor_id: int) -> list[Shift]:
    """Расписание конкретного врача — доступно всем ролям."""
    if not AccessControl.can_view_schedule(actor_role):
        raise PermissionError("Нет прав на просмотр расписания")

    return shifts_rep.get_doctor_schedule(doctor_id)


def get_doctor_periods(actor_role: str, doctor_id: int) -> list[SchedulePeriod]:
    """Периоды врача (отпуск, обучение) — просмотр доступен всем."""
    if not AccessControl.can_view_schedule(actor_role):
        raise PermissionError("Нет прав на просмотр расписания")

    return schedule_periods_rep.get_by_doctor(doctor_id)


# ---------- Редактирование (только админ) ----------

def add_shift(actor_role: str, doctor_id: int, day_date: str,
              start_time: str, end_time: str) -> int:
    """Добавление смены — только админ. Возвращает shift_id."""
    if not AccessControl.can_edit_schedule(actor_role):
        raise PermissionError("Только администратор может редактировать расписание")

    return shifts_rep.create(doctor_id, day_date, start_time, end_time)


def update_shift(actor_role: str, shift_id: int, doctor_id: int = None,
                 day_date: str = None, start_time: str = None, end_time: str = None):
    """Изменение смены — только админ."""
    if not AccessControl.can_edit_schedule(actor_role):
        raise PermissionError("Только администратор может редактировать расписание")

    shifts_rep.update(shift_id, doctor_id, day_date, start_time, end_time)


def delete_shift(actor_role: str, shift_id: int):
    """Удаление смены — только админ. Записи на смену удалятся каскадно."""
    if not AccessControl.can_edit_schedule(actor_role):
        raise PermissionError("Только администратор может редактировать расписание")

    shifts_rep.delete(shift_id)


def add_period(actor_role: str, doctor_id: int, start_date: str,
               end_date: str, period_type: str) -> int:
    """Добавление периода — только админ. Возвращает period_id."""
    if not AccessControl.can_edit_schedule(actor_role):
        raise PermissionError("Только администратор может редактировать расписание")

    return schedule_periods_rep.create(doctor_id, start_date, end_date, period_type)


def delete_period(actor_role: str, period_id: int):
    """Удаление периода — только админ."""
    if not AccessControl.can_edit_schedule(actor_role):
        raise PermissionError("Только администратор может редактировать расписание")

    schedule_periods_rep.delete(period_id)