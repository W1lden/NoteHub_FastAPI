from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from notes.core.constants import TITLE_MAX_LEN


class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=TITLE_MAX_LEN)


class CategoryDB(CategoryCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
