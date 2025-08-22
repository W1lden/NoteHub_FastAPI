from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from notes.core.constants import TITLE_MAX_LEN
from notes.core.db import Base

note_category_association = Table(
    "note_category_association",
    Base.metadata,
    Column(
        "note_id",
        Integer,
        ForeignKey("note.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "category_id",
        Integer,
        ForeignKey("category.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Category(Base):
    name: Mapped[str] = mapped_column(String(TITLE_MAX_LEN), nullable=False)

    notes: Mapped[List["Note"]] = relationship(  # noqa
        "Note",
        secondary=note_category_association,
        back_populates="categories",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name!r})>"
