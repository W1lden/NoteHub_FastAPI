from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_TITLE: str = "NoteHub"
    DESCRIPTION: str

    SECRET_WORD: str = "SECRET"
    DATABASE_URL: str
    PRODUCTION: bool

    ADMIN: str

    SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
