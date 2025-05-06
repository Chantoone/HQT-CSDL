from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: int
    database_name: str
    database_username: str
    database_password: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    default_password: str
    port: int
    host: str

    email_host: str
    email_port: int
    email_username: str
    email_password: str
    email_receiver: str

    class Config:
        env_file = ".env"

settings = Settings()
