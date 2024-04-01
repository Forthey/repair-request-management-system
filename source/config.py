from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TOKEN: str

    DB_POSTGRES_HOST: str
    DB_POSTGRES_PORT: int
    DB_POSTGRES_USER: str
    DB_POSTGRES_NAME: str
    DB_POSTGRES_PASSWORD: str

    @property
    def get_token(self):
        return self.TOKEN

    @property
    def get_psycopg_URL(self):
        return f"postgresql+psycopg://{self.DB_POSTGRES_USER}:{self.DB_POSTGRES_PASSWORD}@{self.DB_POSTGRES_HOST}:{str(self.DB_POSTGRES_PORT)}/{str(self.DB_POSTGRES_NAME)}"

    model_config = SettingsConfigDict(env_file="../.env")


settings = Settings()
