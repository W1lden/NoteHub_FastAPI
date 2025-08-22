import logging
from typing import Generic, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ModelType = TypeVar("ModelType")


class CRUDBase(Generic[ModelType]):

    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    async def get(
        self, obj_id: int, session: AsyncSession
    ) -> ModelType | None:
        logger.info("Getting %s with id=%s", self.model.__name__, obj_id)
        db_obj = await session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        result = db_obj.scalars().first()
        logger.info("Got %s: %s", self.model.__name__, result)
        return result

    async def get_multi(self, session: AsyncSession) -> list[ModelType]:
        logger.info("Getting all %s objects", self.model.__name__)
        db_objs = await session.execute(select(self.model))
        result = db_objs.scalars().all()
        logger.info("Got %d %s objects", len(result), self.model.__name__)
        return result

    async def create(
        self, obj_in: BaseModel, session: AsyncSession
    ) -> ModelType:
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        logger.info("Created %s with id=%s", self.model.__name__, db_obj.id)
        return db_obj

    async def update(
        self, db_obj: ModelType, obj_in: BaseModel, session: AsyncSession
    ) -> ModelType:
        logger.info(
            "Updating %s with id=%s",
            self.model.__name__,
            getattr(db_obj, "id", None),
        )
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        await session.commit()
        await session.refresh(db_obj)
        logger.info(
            "Updated %s with id=%s",
            self.model.__name__,
            getattr(db_obj, "id", None),
        )
        return db_obj

    async def delete(
        self, db_obj: ModelType, session: AsyncSession
    ) -> ModelType:
        logger.info(
            "Deleting %s with id=%s",
            self.model.__name__,
            getattr(db_obj, "id", None),
        )
        await session.delete(db_obj)
        await session.commit()
        logger.info(
            "Deleted %s with id=%s",
            self.model.__name__,
            getattr(db_obj, "id", None),
        )
        return db_obj
