from sqlalchemy.orm import Session

from src.app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_by_username(self, username: str) -> User | None:
        return self._db.query(User).filter(User.username == username).first()

    def create(self, user: User) -> User:
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user
