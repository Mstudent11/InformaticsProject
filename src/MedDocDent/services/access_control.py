class AccessControl:
    """Проверка прав по ролям пользователей системы.

    Роли:
        ADMIN   — администратор
        DOCTOR  — врач
        PATIENT — пациент
    """

    VALID_ROLES = ('ADMIN', 'DOCTOR', 'PATIENT')

    # ---------- Вход в систему ----------

    @staticmethod
    def can_login(role: str) -> bool:
        """Вход в систему доступен всем зарегистрированным ролям."""
        return role in AccessControl.VALID_ROLES

    # ---------- Просмотр расписания ----------

    @staticmethod
    def can_view_schedule(role: str) -> bool:
        """Просмотр расписания врачей — все роли."""
        return role in AccessControl.VALID_ROLES

    # ---------- Редактирование расписания ----------

    @staticmethod
    def can_edit_schedule(role: str) -> bool:
        """Редактирование расписания (создание/изменение/удаление смен и периодов) — только админ."""
        return role == 'ADMIN'

    # ---------- Управление пользователями ----------

    @staticmethod
    def can_manage_users(role: str) -> bool:
        """Добавление и удаление пользователей (пациентов/врачей) — только админ."""
        return role == 'ADMIN'

    # ---------- Просмотр списка врачей ----------

    @staticmethod
    def can_view_doctors(role: str) -> bool:
        """Просмотр списка врачей — админ и пациент.

        Врач видит только своё расписание, список коллег ему не нужен.
        """
        return role in ('ADMIN', 'PATIENT')

    # ---------- Бронирование записей ----------

    @staticmethod
    def can_book_appointment(role: str) -> bool:
        """Создание записи к специалисту через меню бронирований — только пациент."""
        return role == 'PATIENT'

    @staticmethod
    def can_delete_appointment(role: str, appointment_patient_id: int, user_id: int) -> bool:
        """Удаление записи из меню бронирований — только пациент и только свою запись.

        :param appointment_patient_id: patient_id из записи на приём
        :param user_id: user_id текущего пользователя
        """
        return role == 'PATIENT' and appointment_patient_id == user_id