from typing import List

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from notes.core.constants import TITLE_MAX_LEN
from notes.core.db import Base

from .category import note_category_association


class Note(Base):
    title: Mapped[str] = mapped_column(String(TITLE_MAX_LEN), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    user: Mapped["User"] = relationship(back_populates="notes")  # noqa
    categories: Mapped[List["Category"]] = relationship(  # noqa
        "Category", secondary=note_category_association, back_populates="notes"
    )

    def __repr__(self) -> str:
        return f"<Note(id={self.id}, title={self.title!r}, user_id={self.user_id})>"  # noqa
