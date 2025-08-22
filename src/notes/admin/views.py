from sqladmin import ModelView

from notes.db.models import Category, Note, User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.is_admin]
    column_searchable_list = [User.email]
    column_sortable_list = [User.id, User.email]


class NoteAdmin(ModelView, model=Note):
    column_list = [Note.id, Note.title, Note.user_id, Note.created_at]


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.name]
