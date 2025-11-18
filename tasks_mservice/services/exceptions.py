class NotFoundError(Exception):
    """Використовується, коли об'єкт не знайдено в БД."""

    pass


class BusinessLogicError(Exception):
    """Для помилок бізнес-логіки (напр., переміщення таска)."""

    pass


class PermissionDeniedError(Exception):
    """Для помилок коли check_if_accessible повертає False"""

    pass
