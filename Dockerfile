FROM python:3.12
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN apt-get update && apt-get install -y libgl1-mesa-glx && \
    python -m pip install --upgrade pip && \
    apt-get install -y postgresql-client && \
    pip install poetry --no-cache-dir && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-root --no-cache --no-interaction

COPY alembic ./alembic
COPY app ./app
COPY fonts ./fonts
COPY alembic.ini entrypoint.sh db_restore.sh .env ./

CMD ["sh", "./entrypoint.sh"]
