import sys
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.settings import settings

SEARCH_PATH_PARAM_NAME = '-csearch_path%3D'


def get_dsn():
    if 'pytest' in sys.modules:
        if '_test_' not in settings.DATABASE_SCHEMA:
            settings.DATABASE_SCHEMA += '_test_' + str(uuid.uuid4()).replace('-', '_')

        schema_in_uri = settings.DB_DSN.split(SEARCH_PATH_PARAM_NAME, 1)
        if len(schema_in_uri) == 2:
            settings.DB_DSN = schema_in_uri[0] + SEARCH_PATH_PARAM_NAME + settings.DATABASE_SCHEMA

            other_params = schema_in_uri[1].split('&', 1)
            if len(other_params) == 2:
                settings.DB_DSN += f'&{other_params[1]}'
    return settings.DB_DSN


db_url = get_dsn()

engine = create_engine(
    get_dsn(),
    echo=False,
    pool_size=6,
    max_overflow=10,
)
engine.connect()
session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
