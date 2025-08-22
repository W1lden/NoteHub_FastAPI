from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from notes.core.base import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    notes: Mapped[list["Note"]] = relationship(back_populates="user")  # noqa

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email!r}, is_admin={self.is_admin})>"  # noqa
