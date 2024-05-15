from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TOKEN: str

    BOT_USERNAME: str

    TG_API_ID: int
    TG_API_HASH: str

    YANDEX_CLIENT_ID: str
    YANDEX_CLIENT_SECRET: str
    YANDEX_TOKEN: str
    YANDEX_DIR_PUBLIC_KEY: str

    DB_POSTGRES_HOST: str
    DB_POSTGRES_PORT: int
    DB_POSTGRES_USER: str
    DB_POSTGRES_NAME: str
    DB_POSTGRES_PASSWORD: str

    @property
    def get_token(self):
        return self.TOKEN

    @property
    def get_bot_username(self):
        return self.BOT_USERNAME

    @property
    def get_tg_api_id(self):
        return self.TG_API_ID

    @property
    def get_tg_api_hash(self):
        return self.TG_API_HASH

    @property
    def get_psycopg_URL(self):
        return f"postgresql+psycopg://{self.DB_POSTGRES_USER}:{self.DB_POSTGRES_PASSWORD}@{self.DB_POSTGRES_HOST}:{str(self.DB_POSTGRES_PORT)}/{str(self.DB_POSTGRES_NAME)}"

    model_config = SettingsConfigDict(env_file="../.env")


settings = Settings()
