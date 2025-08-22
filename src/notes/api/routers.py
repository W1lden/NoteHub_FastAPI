from fastapi import APIRouter

from notes.api.endpoints import category_router, note_router, user_router

api_router = APIRouter()

api_router.include_router(
    category_router, prefix="/category", tags=["Category"]
)

api_router.include_router(note_router, prefix="/note", tags=["Note"])

api_router.include_router(user_router)
