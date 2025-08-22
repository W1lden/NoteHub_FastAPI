from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from notes.core.constants import TITLE_MAX_LEN

from .category import CategoryDB


class NoteBase(BaseModel):
    title: str = Field(..., max_length=TITLE_MAX_LEN)
    text: Optional[str] = None


class NoteCreate(NoteBase):
    category_ids: Optional[List[int]] = None


class NoteDB(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    categories: List[CategoryDB]

    class Config:
        from_attributes = True


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=TITLE_MAX_LEN)
    text: Optional[str] = None
    category_ids: Optional[list[int]] = None
