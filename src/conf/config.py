from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str
    db_local_url: str
    db_user: str
    db_password: str
    db_port: int
    db_name: str
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    mail_use_ssl: bool
    mail_use_tls: bool

    redis_host: str
    redis_local_host: str = 'localhost'
    redis_port: int
    redis_password: str
    redis_name: str = ''

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()