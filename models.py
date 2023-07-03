from sqlalchemy import create_engine, Column, Integer, String, Text, UniqueConstraint, Index, func, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

from config import DB_ENGINE, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_DBNAME

url_engine = f'{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DBNAME}'
print(f'{url_engine}')
engine = create_engine(url_engine)

Base = declarative_base()


class Anekdot(Base):
    __tablename__ = 'anekdot'

    id = Column(Integer, primary_key=True)
    date = Column(String(10))
    category = Column(String(1))
    consecutive = Column(Integer, default=0, nullable=False)
    an_id = Column(Integer, default=0, nullable=False)
    text = Column(Text)

    __table_args__ = (UniqueConstraint('category', 'date', 'consecutive', name='i_date'),)


class AnekdotUser(Base):
    __tablename__ = 'anekdot_user'

    id = Column(Integer, primary_key=True)
    user = Column(String(255))
    date = Column(String(10))
    category = Column(String(1))
    passed = Column(Integer, default=0)
    an_ids = Column(String(255))

    # Добавление уникального индекса
    __table_args__ = (
        UniqueConstraint('user', 'category', 'date', name='user_date'),
        Index('i_user', 'user'),
    )


class Photo(Base):
    __tablename__ = 'photos'

    id = Column(Integer, primary_key=True)
    user = Column(String(255))
    file = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now(), index=True)


if __name__ == '__main__':
    Base.metadata.create_all(engine)