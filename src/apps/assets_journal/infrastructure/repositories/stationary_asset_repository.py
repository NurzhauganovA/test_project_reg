from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.assets_journal.domain.models.stationary_asset import StationaryAssetDomain
from src.apps.assets_journal.infrastructure.api.schemas.responses.stationary_asset_schemas import (
    StationaryAssetStatisticsSchema,
)
from src.apps.assets_journal.infrastructure.db_models.models import StationaryAsset
from src.apps.assets_journal.interfaces.repository_interfaces import (
    StationaryAssetRepositoryInterface,
)
from src.apps.assets_journal.mappers import (
    map_stationary_asset_db_to_domain,
    map_stationary_asset_domain_to_db,
)
from src.core.logger import LoggerService
from src.shared.infrastructure.base import BaseRepository


class StationaryAssetRepositoryImpl(BaseRepository, StationaryAssetRepositoryInterface):
    """Реализация репозитория активов стационара"""

    def __init__(self, async_db_session: AsyncSession, logger: LoggerService):
        super().__init__(async_db_session, logger)

    async def get_by_id(self, asset_id: UUID) -> Optional[StationaryAssetDomain]:
        query = select(StationaryAsset).where(StationaryAsset.id == asset_id)
        result = await self._async_db_session.execute(query)
        asset = result.scalar_one_or_none()

        if asset:
            return map_stationary_asset_db_to_domain(asset)
        return None

    async def get_by_bg_asset_id(self, bg_asset_id: str) -> Optional[StationaryAssetDomain]:
        query = select(StationaryAsset).where(StationaryAsset.bg_asset_id == bg_asset_id)
        result = await self._async_db_session.execute(query)
        asset = result.scalar_one_or_none()

        if asset:
            return map_stationary_asset_db_to_domain(asset)
        return None

    async def get_assets(
            self,
            filters: Dict[str, any],
            page: int = 1,
            limit: int = 30,
    ) -> List[StationaryAssetDomain]:
        query = select(StationaryAsset)

        # Применяем фильтры
        query = self._apply_filters(query, filters)

        # Сортировка по дате регистрации (сначала новые)
        query = query.order_by(StationaryAsset.reg_date.desc())

        # Пагинация
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        assets = result.scalars().all()

        return [map_stationary_asset_db_to_domain(asset) for asset in assets]

    async def get_total_count(self, filters: Dict[str, any]) -> int:
        query = select(func.count(StationaryAsset.id))

        # Применяем фильтры
        query = self._apply_filters(query, filters)

        result = await self._async_db_session.execute(query)
        return result.scalar_one()

    async def create(self, asset: StationaryAssetDomain) -> StationaryAssetDomain:
        db_asset = map_stationary_asset_domain_to_db(asset)

        self._async_db_session.add(db_asset)
        await self._async_db_session.flush()
        await self._async_db_session.refresh(db_asset)

        return map_stationary_asset_db_to_domain(db_asset)

    async def update(self, asset: StationaryAssetDomain) -> StationaryAssetDomain:
        query = select(StationaryAsset).where(StationaryAsset.id == asset.id)
        result = await self._async_db_session.execute(query)
        db_asset = result.scalar_one()

        # Обновляем поля
        for field, value in asset.__dict__.items():
            if hasattr(db_asset, field) and field != 'id':
                setattr(db_asset, field, value)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(db_asset)

        return map_stationary_asset_db_to_domain(db_asset)

    async def delete(self, asset_id: UUID) -> None:
        query = select(StationaryAsset).where(StationaryAsset.id == asset_id)
        result = await self._async_db_session.execute(query)
        asset = result.scalar_one()

        await self._async_db_session.delete(asset)
        await self._async_db_session.flush()

    async def get_statistics(self, filters: Dict[str, any]) -> StationaryAssetStatisticsSchema:
        base_query = select(StationaryAsset)
        base_query = self._apply_filters(base_query, filters)

        # Общее количество
        total_query = select(func.count(StationaryAsset.id))
        total_query = self._apply_filters(total_query, filters)
        total_result = await self._async_db_session.execute(total_query)
        total_assets = total_result.scalar_one()

        # Подтвержденные
        confirmed_query = select(func.count(StationaryAsset.id)).where(
            StationaryAsset.has_confirm == True
        )
        confirmed_query = self._apply_filters(confirmed_query, filters)
        confirmed_result = await self._async_db_session.execute(confirmed_query)
        confirmed_assets = confirmed_result.scalar_one()

        # Отказанные
        refused_query = select(func.count(StationaryAsset.id)).where(
            StationaryAsset.has_refusal == True
        )
        refused_query = self._apply_filters(refused_query, filters)
        refused_result = await self._async_db_session.execute(refused_query)
        refused_assets = refused_result.scalar_one()

        # Ожидающие
        pending_assets = total_assets - confirmed_assets - refused_assets

        # С файлами
        files_query = select(func.count(StationaryAsset.id)).where(
            StationaryAsset.has_files == True
        )
        files_query = self._apply_filters(files_query, filters)
        files_result = await self._async_db_session.execute(files_query)
        assets_with_files = files_result.scalar_one()

        # С файлами реабилитации
        rehab_files_query = select(func.count(StationaryAsset.id)).where(
            StationaryAsset.has_rehabilitation_files == True
        )
        rehab_files_query = self._apply_filters(rehab_files_query, filters)
        rehab_files_result = await self._async_db_session.execute(rehab_files_query)
        assets_with_rehabilitation_files = rehab_files_result.scalar_one()

        return StationaryAssetStatisticsSchema(
            total_assets=total_assets,
            confirmed_assets=confirmed_assets,
            refused_assets=refused_assets,
            pending_assets=pending_assets,
            assets_with_files=assets_with_files,
            assets_with_rehabilitation_files=assets_with_rehabilitation_files,
        )

    async def bulk_create(self, assets: List[StationaryAssetDomain]) -> List[StationaryAssetDomain]:
        db_assets = [map_stationary_asset_domain_to_db(asset) for asset in assets]

        self._async_db_session.add_all(db_assets)
        await self._async_db_session.flush()

        for db_asset in db_assets:
            await self._async_db_session.refresh(db_asset)

        return [map_stationary_asset_db_to_domain(db_asset) for db_asset in db_assets]

    async def exists_by_bg_asset_id(self, bg_asset_id: str) -> bool:
        query = select(func.count(StationaryAsset.id)).where(
            StationaryAsset.bg_asset_id == bg_asset_id
        )
        result = await self._async_db_session.execute(query)
        count = result.scalar_one()
        return count > 0

    def _apply_filters(self, query, filters: Dict[str, any]):
        """Применить фильтры к запросу"""

        # Поиск по пациенту (ФИО или ИИН)
        if filters.get("patient_search"):
            search_term = f"%{filters['patient_search'].lower()}%"
            query = query.where(
                or_(
                    func.lower(StationaryAsset.patient_full_name).like(search_term),
                    StationaryAsset.patient_iin.like(search_term)
                )
            )

        # ИИН пациента
        if filters.get("patient_iin"):
            query = query.where(StationaryAsset.patient_iin == filters["patient_iin"])

        # Период по дате регистрации
        if filters.get("date_from"):
            query = query.where(StationaryAsset.reg_date >= filters["date_from"])

        if filters.get("date_to"):
            query = query.where(StationaryAsset.reg_date <= filters["date_to"])

        # Статусы
        if filters.get("status") is not None:
            query = query.where(StationaryAsset.status == filters["status"])

        if filters.get("delivery_status") is not None:
            query = query.where(StationaryAsset.delivery_status == filters["delivery_status"])

        # Участок и специализация
        if filters.get("area_number") is not None:
            query = query.where(StationaryAsset.area_number == filters["area_number"])

        if filters.get("specialization"):
            query = query.where(
                func.lower(StationaryAsset.specialization).like(
                    f"%{filters['specialization'].lower()}%"
                )
            )

        if filters.get("specialist_name"):
            query = query.where(
                func.lower(StationaryAsset.specialist_name).like(
                    f"%{filters['specialist_name'].lower()}%"
                )
            )

        # Медицинские данные
        if filters.get("referral_target") is not None:
            query = query.where(StationaryAsset.referral_target == filters["referral_target"])

        if filters.get("referral_type") is not None:
            query = query.where(StationaryAsset.referral_type == filters["referral_type"])

        if filters.get("rehabilitation_type") is not None:
            query = query.where(StationaryAsset.rehabilitation_type == filters["rehabilitation_type"])

        # Организации
        if filters.get("org_health_care_request_code"):
            query = query.where(
                StationaryAsset.org_health_care_request_code == filters["org_health_care_request_code"]
            )

        if filters.get("org_health_care_direct_code"):
            query = query.where(
                StationaryAsset.org_health_care_direct_code == filters["org_health_care_direct_code"]
            )

        if filters.get("org_health_care_ref_code"):
            query = query.where(
                StationaryAsset.org_health_care_ref_code == filters["org_health_care_ref_code"]
            )

        # Врач
        if filters.get("direct_doctor"):
            query = query.where(
                func.lower(StationaryAsset.direct_doctor).like(
                    f"%{filters['direct_doctor'].lower()}%"
                )
            )

        # Диагноз
        if filters.get("sick_code"):
            query = query.where(StationaryAsset.sick_code == filters["sick_code"])

        # Профиль койки
        if filters.get("bed_profile_code"):
            query = query.where(StationaryAsset.bed_profile_code == filters["bed_profile_code"])

        # Флаги
        if filters.get("has_confirm") is not None:
            query = query.where(StationaryAsset.has_confirm == filters["has_confirm"])

        if filters.get("has_files") is not None:
            query = query.where(StationaryAsset.has_files == filters["has_files"])

        if filters.get("has_refusal") is not None:
            query = query.where(StationaryAsset.has_refusal == filters["has_refusal"])

        if filters.get("has_rehabilitation_files") is not None:
            query = query.where(
                StationaryAsset.has_rehabilitation_files == filters["has_rehabilitation_files"]
            )

        # Номер карты
        if filters.get("card_number"):
            query = query.where(StationaryAsset.card_number == filters["card_number"])

        # Исход лечения
        if filters.get("treatment_outcome"):
            query = query.where(
                func.lower(StationaryAsset.treatment_outcome).like(
                    f"%{filters['treatment_outcome'].lower()}%"
                )
            )

        return query