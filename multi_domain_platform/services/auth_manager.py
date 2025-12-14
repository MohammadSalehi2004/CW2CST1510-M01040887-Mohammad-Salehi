from typing import Optional
from models.user import User
from services.database_manager import DatabaseManager
import bcrypt #replaced with hashlib example from lab

class SimpleHasher:
    """Password hashing and verification using bcrypt (Week 8 logic)."""

    def hash_password(self, plain_text_password: str) -> str:
        password_bytes = plain_text_password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    def verify_password(self, plain_text_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_text_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )


class AuthManager:
    """Handles user registration and login."""

    def __init__(self, db: DatabaseManager):
        self._db = db
        self._hasher = SimpleHasher()

    def register_user(self, username: str, password: str, role: str = "user") -> None:
        password_hash = self._hasher.hash_password(password)
        self._db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )

    def login_user(self, username: str, password: str) -> Optional[User]:
        row = self._db.fetch_one(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (username,),
        )

        if row is None:
            return None

        username_db, password_hash_db, role_db = row

        if self._hasher.verify_password(password, password_hash_db):
            return User(username_db, password_hash_db, role_db)

        return None