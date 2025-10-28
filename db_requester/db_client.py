from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from resources.db_creds import DataBaseCreds

USERNAME = DataBaseCreds.USERNAMEDB
PASSWORD = DataBaseCreds.PASSWORDDB
HOST = DataBaseCreds.HOSTDB
PORT = DataBaseCreds.PORTDB
DATABASE_NAME = DataBaseCreds.NAMEDB

#  движок для подключения к базе данных
engine = create_engine(
    f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}",
    echo=False  # Установить True для отладки SQL запросов
)

#  создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    """Создает новую сессию БД"""
    return SessionLocal()