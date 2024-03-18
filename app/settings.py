import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    TELEGRAM_TOKEN: str = ''
    TINKOFF_TOKEN: str = ''

    ROOT_DIR: Path = ROOT_DIR
    DB_DSN: str = ''
    DB_TEST_DSN: str = ''
    DATABASE_SCHEMA: str = 'main'

    CLASS_CODES: List[str] = ['TQBR', 'SPBFUT']  # поиск только по акциям РФ и фьючерсам

    SAVE_PATH: str = os.path.join(ROOT_DIR, 'files')

    MAX_ITEMS_PER_DAY: int = 5
    DATE_FORMAT: str = '%Y-%m-%d'
    LOG_FILE: str = os.path.join(ROOT_DIR, 'debug.log')

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / '.env',
        env_file_encoding='utf-8',
        extra='allow',
    )


settings = Settings()
