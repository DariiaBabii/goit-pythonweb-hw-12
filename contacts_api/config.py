from pydantic import BaseSettings
import redis

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

class Settings(BaseSettings):
    SECRET_KEY: str
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    FRONTEND_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
