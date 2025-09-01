from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)
from asyncio import current_task
from core.config import settings


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
            pool_pre_ping=True,  # Check connections before reuse
            pool_recycle=3600    # Recycle connections hourly
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def get_scoped_session(self):
        return async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task
        )

    @staticmethod
    async def session_dependency() -> AsyncSession:
        """
        yields a brand‐new session from the factory and closes it on exit
        """
        # note: we refer to the *singleton* below, not `self`
        async with db_helper.session_factory() as session:
            yield session

    @staticmethod
    async def scoped_session_dependency() -> AsyncSession:
        """
        yields the scoped_session (one‐per‐task) and then closes/removes it
        """
        session = db_helper.get_scoped_session()
        try:
            yield session
        finally:
            await session.close()
            await session.remove()


db_helper = DatabaseHelper(
    url=settings.db.url,
    echo=settings.db.echo,
)