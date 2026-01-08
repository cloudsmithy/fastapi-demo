from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ISSUER: str = "http://localhost:8000"  # 签发者域名

    class Config:
        env_file = ".env"


settings = Settings()
