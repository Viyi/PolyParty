from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_phrase: str = "super-secret-default"
    admin_pass: str = "hunter2"


settings = Settings()
