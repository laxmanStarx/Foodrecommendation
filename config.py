from pydantic import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_SSLMODE: str = "require"

    class Config:
        env_file = ".env"

settings = Settings()
