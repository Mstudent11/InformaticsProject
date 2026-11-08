from repositories import shifts_rep
from repositories import schedule_periods_rep
from models.shifts import Shift
from models.schedule_periods import SchedulePeriod
from services.access_control import AccessControl
from typing import List, Dict, Any


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