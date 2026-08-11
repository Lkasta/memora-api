import bcrypt


class PasswordHandler:
    """Stateless bcrypt helpers. Grouped in a class for a stable import path
    (``from security.password_handler import PasswordHandler``) even though no
    instance state is needed."""

    @staticmethod
    def encrypt_password(password: str) -> bytes:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt)

    @staticmethod
    def check_password(password: str, hashed_password: bytes) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password)
