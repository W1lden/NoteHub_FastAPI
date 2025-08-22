from fastapi import APIRouter

from notes.api.endpoints import category_router, note_router, user_router

main_router = APIRouter()

main_router.include_router(
    category_router, prefix="/category", tags=["Category"]
)

main_router.include_router(note_router, prefix="/note", tags=["Note"])

main_router.include_router(user_router)
