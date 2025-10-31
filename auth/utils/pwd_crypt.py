import hashlib


def hash_password(password: str) -> str:
    """
    Хешуємо пароль за допомогою SHA-256
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Перевіряємо, чи збігається хеш
    """
    return hash_password(plain_password) == hashed_password
