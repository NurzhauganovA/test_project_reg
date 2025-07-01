from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm.session import sessionmaker

from src.apps.catalogs.infrastructure.repositories.citizenship_catalog_repository import (
    SQLAlchemyCitizenshipCatalogueRepositoryImpl,
)
from src.apps.catalogs.infrastructure.repositories.financing_sources_repository import (
    SQLAlchemyFinancingSourcesCatalogRepositoryImpl,
)
from src.apps.catalogs.infrastructure.repositories.medical_organizations_catalog_repository import (
    SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl,
)
from src.apps.catalogs.infrastructure.repositories.nationalities_catalog_repository import (
    SQLAlchemyNationalitiesCatalogRepositoryImpl,
)
from src.apps.catalogs.infrastructure.repositories.patient_context_attributes_repository import (
    SQLAlchemyPatientContextAttributesCatalogueRepositoryImpl,
)
from src.apps.catalogs.services.citizenship_catalog_service import (
    CitizenshipCatalogService,
)
from src.apps.catalogs.services.financing_sources_catalog_service import (
    FinancingSourceCatalogService,
)
from src.apps.catalogs.services.medical_organizations_catalog_service import (
    MedicalOrganizationsCatalogService,
)
from src.apps.catalogs.services.nationalities_catalog_service import (
    NationalitiesCatalogService,
)
from src.apps.catalogs.services.patient_context_attribute_service import (
    PatientContextAttributeService,
)
from src.core.logger import LoggerService


class CatalogsContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.apps.catalogs.infrastructure.api",
        ]
    )

    # Dependencies from core DI-container
    logger = providers.Dependency(instance_of=LoggerService)
    engine = providers.Dependency(instance_of=AsyncEngine)

    # Session factory
    session_factory = providers.Singleton(
        sessionmaker, bind=engine, expire_on_commit=False, class_=AsyncSession
    )

    # Async session
    async_db_session = providers.Singleton(
        lambda session_factory: session_factory(), session_factory
    )

    # Repositories
    citizenship_catalog_repository = providers.Factory(
        SQLAlchemyCitizenshipCatalogueRepositoryImpl,
        async_db_session=async_db_session,
        logger=logger,
    )

    nationalities_catalog_repository = providers.Factory(
        SQLAlchemyNationalitiesCatalogRepositoryImpl,
        async_db_session=async_db_session,
        logger=logger,
    )

    patient_context_attributes_repository = providers.Factory(
        SQLAlchemyPatientContextAttributesCatalogueRepositoryImpl,
        async_db_session=async_db_session,
        logger=logger,
    )

    financing_sources_catalog_repository = providers.Factory(
        SQLAlchemyFinancingSourcesCatalogRepositoryImpl,
        async_db_session=async_db_session,
        logger=logger,
    )

    medical_organizations_catalog_repository = providers.Factory(
        SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl,
        async_db_session=async_db_session,
        logger=logger,
    )

    # Services
    nationalities_catalog_service = providers.Factory(
        NationalitiesCatalogService,
        logger=logger,
        nationalities_catalog_repository=nationalities_catalog_repository,
    )

    patient_context_attributes_service = providers.Factory(
        PatientContextAttributeService,
        logger=logger,
        context_attributes_repository=patient_context_attributes_repository,
    )

    financing_sources_catalog_service = providers.Factory(
        FinancingSourceCatalogService,
        logger=logger,
        financing_sources_catalog_repository=financing_sources_catalog_repository,
    )

    medical_organizations_catalog_service = providers.Factory(
        MedicalOrganizationsCatalogService,
        logger=logger,
        medical_organizations_catalog_repository=medical_organizations_catalog_repository,
    )

    citizenship_catalog_service = providers.Factory(
        CitizenshipCatalogService,
        logger=logger,
        citizenship_catalog_repository=citizenship_catalog_repository,
    )
