from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm.session import sessionmaker

from src.apps.assets_journal.infrastructure.repositories.stationary_asset_repository import (
    StationaryAssetRepositoryImpl,
)
from src.apps.assets_journal.services.stationary_asset_service import (
    StationaryAssetService,
)
from src.apps.assets_journal.uow import AssetsJournalUnitOfWorkImpl
from src.core.logger import LoggerService


class AssetsJournalContainer(containers.DeclarativeContainer):
    """DI контейнер для модуля журналов активов"""

    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.apps.assets_journal.infrastructure.api",
        ]
    )

    config = providers.Configuration()

    # Зависимости из основного контейнера
    logger = providers.Dependency(instance_of=LoggerService)
    engine = providers.Dependency(instance_of=AsyncEngine)

    # Фабрика сессий
    session_factory = providers.Singleton(
        sessionmaker,
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession
    )

    # Асинхронная сессия БД
    async_db_session = providers.Singleton(
        lambda session_factory: session_factory(),
        session_factory
    )

    # Unit of Work
    unit_of_work = providers.Factory(
        AssetsJournalUnitOfWorkImpl,
        session=async_db_session,
        logger=logger,
    )

    # Репозитории
    stationary_asset_repository = providers.Factory(
        StationaryAssetRepositoryImpl,
        async_db_session=async_db_session,
        logger=logger,
    )

    # Сервисы
    stationary_asset_service = providers.Factory(
        StationaryAssetService,
        uow=unit_of_work,
        stationary_asset_repository=stationary_asset_repository,
        logger=logger,
    )