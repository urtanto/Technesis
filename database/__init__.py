import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SqlAlchemyBase = declarative_base()

from database.models import *


class Database:
    """
    Singleton-класс для работы с асинхронной базой данных.
    Позволяет выполнять init() один раз и затем получать сессии с помощью get_session().
    """
    _instance = None  # Единственный экземпляр класса
    _initialized = False  # Флаг инициализации для избежания повторного запуска init()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise Exception("Необходимо указать переменную окружения DATABASE_URL для подключения к базе данных.")

        db_file = self.db_url.split("///")[-1]
        if not os.path.exists(db_file):
            open(db_file, "a").close()

        self._engine = None
        self._session_factory = None

    async def init(self):
        """
        Инициализация асинхронного движка и фабрики сессий

        Использование:
        async with await Database().get_session() as session:
            async with session.begin():
                ...
        """
        if self._initialized:
            return self

        self._engine = create_async_engine(self.db_url, echo=False)

        self._session_factory = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False
        )

        async with self._engine.begin() as conn:
            await conn.run_sync(SqlAlchemyBase.metadata.create_all)

        self._initialized = True

        return self

    async def get_session(self) -> AsyncSession:
        """
        Создает и возвращает асинхронную сессию

        :return: Асинхронная сессия
        :rtype: AsyncSession
        """
        if not self._session_factory:
            raise Exception("База данных не инициализирована. Сначала вызовите await Database().init().")
        return self._session_factory()
