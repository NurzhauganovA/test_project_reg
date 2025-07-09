import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
from uuid import UUID

from src.apps.assets_journal.domain.enums import AssetDeliveryStatusEnum, AssetStatusEnum
from src.apps.assets_journal.domain.models.stationary_asset import StationaryAssetDomain, StationaryAssetListItemDomain
from src.apps.assets_journal.infrastructure.api.schemas.requests.stationary_asset_filter_params import (
    StationaryAssetFilterParams, OrganizationAssetsFilterParams,
)
from src.apps.assets_journal.infrastructure.api.schemas.requests.stationary_asset_schemas import (
    CreateStationaryAssetSchema,
    UpdateStationaryAssetSchema, CreateStationaryAssetByPatientIdSchema,
)
from src.apps.assets_journal.infrastructure.api.schemas.responses.stationary_asset_schemas import (
    StationaryAssetStatisticsSchema,
)
from src.apps.assets_journal.interfaces.repository_interfaces import (
    StationaryAssetRepositoryInterface,
)
from src.apps.assets_journal.interfaces.uow_interface import (
    AssetsJournalUnitOfWorkInterface,
)
from src.apps.assets_journal.mappers import map_bg_response_to_domain, map_create_schema_to_domain
from src.apps.patients.services.patients_service import PatientService
from src.core.i18n import _
from src.core.logger import LoggerService
from src.shared.exceptions import NoInstanceFoundError
from src.shared.schemas.pagination_schemas import PaginationParams


class StationaryAssetService:
    """Сервис для работы с активами стационара"""

    def __init__(
            self,
            uow: AssetsJournalUnitOfWorkInterface,
            stationary_asset_repository: StationaryAssetRepositoryInterface,
            patients_service: PatientService,
            logger: LoggerService,
    ):
        self._uow = uow
        self._stationary_asset_repository = stationary_asset_repository
        self._patients_service = patients_service
        self._logger = logger

    async def get_by_id(self, asset_id: UUID) -> StationaryAssetDomain:
        """
        Получить актив по ID

        :param asset_id: ID актива
        :return: Доменная модель актива
        :raises NoInstanceFoundError: Если актив не найден
        """
        asset = await self._stationary_asset_repository.get_by_id(asset_id)
        if not asset:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Актив стационара с ID: %(ID)s не найден.") % {"ID": asset_id}
            )
        return asset

    async def get_assets(
            self,
            pagination_params: PaginationParams,
            filter_params: StationaryAssetFilterParams,
    ) -> Tuple[List[StationaryAssetListItemDomain], int]:
        """
        Получить список активов с фильтрацией и пагинацией

        :param pagination_params: Параметры пагинации
        :param filter_params: Параметры фильтрации
        :return: Кортеж из списка активов и общего количества
        """
        filters = filter_params.to_dict(exclude_none=True)

        assets = await self._stationary_asset_repository.get_assets(
            filters=filters,
            page=pagination_params.page,
            limit=pagination_params.limit,
        )

        total_count = await self._stationary_asset_repository.get_total_count(filters)

        return assets, total_count

    async def get_assets_by_organization(
            self,
            pagination_params: PaginationParams,
            filter_params: OrganizationAssetsFilterParams,
    ) -> Tuple[List[StationaryAssetDomain], int]:
        """
        Получить список активов по организации

        :param pagination_params: Параметры пагинации
        :param filter_params: Параметры фильтрации по организации
        :return: Кортеж из списка активов и общего количества
        """
        filters = filter_params.to_dict(exclude_none=True)

        assets = await self._stationary_asset_repository.get_assets(
            filters=filters,
            page=pagination_params.page,
            limit=pagination_params.limit,
        )

        total_count = await self._stationary_asset_repository.get_total_count(filters)

        return assets, total_count

    async def get_assets_by_patient(
            self,
            patient_id: UUID,
            pagination_params: PaginationParams,
    ) -> Tuple[List[StationaryAssetDomain], int]:
        """
        Получить список активов пациента

        :param patient_id: ID пациента
        :param pagination_params: Параметры пагинации
        :return: Кортеж из списка активов и общего количества
        """
        filters = {'patient_id': patient_id}

        assets = await self._stationary_asset_repository.get_assets(
            filters=filters,
            page=pagination_params.page,
            limit=pagination_params.limit,
        )

        total_count = await self._stationary_asset_repository.get_total_count(filters)

        return assets, total_count

    async def create_asset(self, create_schema: CreateStationaryAssetSchema) -> StationaryAssetDomain:
        """
        Создать новый актив

        :param create_schema: Схема создания актива
        :return: Созданная доменная модель актива
        """
        # Находим пациента по ИИН
        patient = await self._patients_service.get_by_iin(create_schema.patient_iin)
        if not patient:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Пациент с ИИН %(IIN)s не найден.") % {"IIN": create_schema.patient_iin}
            )

        # Проверяем, что актив с таким BG ID еще не существует
        if create_schema.bg_asset_id:
            existing_asset = await self._stationary_asset_repository.get_by_bg_asset_id(
                create_schema.bg_asset_id
            )
            if existing_asset:
                raise ValueError(
                    _("Актив с BG ID %(ID)s уже существует.") % {"ID": create_schema.bg_asset_id}
                )

        # Mapping
        asset_domain = map_create_schema_to_domain(create_schema, patient.id)

        async with self._uow:
            created_asset = await self._uow.stationary_asset_repository.create(asset_domain)

        return created_asset

    async def create_asset_by_patient_id(self, create_schema: CreateStationaryAssetByPatientIdSchema, patient_id: UUID) -> StationaryAssetDomain:
        """
        Создать новый актив по ID пациента

        :param create_schema: Схема создания актива с ID пациента
        :return: Созданная доменная модель актива
        """
        # Проверяем, что актив с таким BG ID еще не существует
        if create_schema.bg_asset_id:
            existing_asset = await self._stationary_asset_repository.get_by_bg_asset_id(
                create_schema.bg_asset_id
            )
            if existing_asset:
                raise ValueError(
                    _("Актив с BG ID %(ID)s уже существует.") % {"ID": create_schema.bg_asset_id}
                )

        # Преобразуем схему в доменную модель
        asset_domain = StationaryAssetDomain(
            bg_asset_id=create_schema.bg_asset_id,
            card_number=create_schema.card_number,
            organization_id=create_schema.organization_id,
            patient_id=patient_id,
            receive_date=create_schema.receive_date,
            receive_time=create_schema.receive_time,
            actual_datetime=create_schema.actual_datetime or create_schema.receive_date,
            received_from=create_schema.received_from,
            is_repeat=create_schema.is_repeat,
            stay_period_start=create_schema.stay_period_start,
            stay_period_end=create_schema.stay_period_end,
            stay_outcome=create_schema.stay_outcome,
            diagnosis=create_schema.diagnosis,
            area=create_schema.area,
            specialization=create_schema.specialization,
            specialist=create_schema.specialist,
            note=create_schema.note,
        )

        async with self._uow:
            created_asset = await self._uow.stationary_asset_repository.create(asset_domain)

        return created_asset

    async def update_asset(
            self,
            asset_id: UUID,
            update_schema: UpdateStationaryAssetSchema
    ) -> StationaryAssetDomain:
        """
        Обновить актив

        :param asset_id: ID актива
        :param update_schema: Схема обновления актива
        :return: Обновленная доменная модель актива
        """
        # Получаем существующий актив
        asset = await self.get_by_id(asset_id)

        # Обновляем поля
        update_data = update_schema.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(asset, field) and value is not None:
                setattr(asset, field, value)

        # Специальная логика для статуса
        if update_schema.status:
            asset.update_status(update_schema.status)

        if update_schema.delivery_status:
            asset.update_delivery_status(update_schema.delivery_status)

        # Обновление диагноза
        if update_schema.diagnosis:
            asset.update_diagnosis(update_schema.diagnosis)

        # Обновление исхода лечения
        if update_schema.stay_outcome:
            asset.update_stay_outcome(update_schema.stay_outcome)

        # Добавление примечания
        if update_schema.note:
            asset.add_note(update_schema.note)

        async with self._uow:
            updated_asset = await self._uow.stationary_asset_repository.update(asset)

        return updated_asset

    async def transfer_to_organization(
            self,
            asset_id: UUID,
            new_organization_id: UUID,
            transfer_reason: Optional[str] = None
    ) -> StationaryAssetDomain:
        """
        Передать актив стационара другой организации

        :param asset_id: ID актива
        :param new_organization_id: ID новой организации
        :param transfer_reason: Причина передачи
        :return: Обновленная доменная модель актива
        """
        # Получаем существующий актив
        asset = await self.get_by_id(asset_id)

        # Проверяем, что это не та же организация
        if asset.organization_id == new_organization_id:
            raise ValueError(_("Актив уже принадлежит указанной организации."))

        # Логируем передачу
        old_org_name = asset.organization_data.get('name', 'Неизвестно') if asset.organization_data else 'Неизвестно'
        self._logger.info(
            f"Передача актива стационара {asset_id} из организации '{old_org_name}' "
            f"в организацию с ID '{new_organization_id}'. Причина: {transfer_reason or 'Не указана'}"
        )

        # Выполняем передачу
        asset.organization_id = new_organization_id
        asset.delivery_status = AssetDeliveryStatusEnum.PENDING_DELIVERY
        asset.status = AssetStatusEnum.REGISTERED  # Сбрасываем статус на зарегистрированный
        asset.actual_datetime = datetime.utcnow()  # Обновляем фактическую дату и время

        # Добавляем примечание о передаче
        transfer_note = f"Актив передан другой организации"
        if transfer_reason:
            transfer_note += f". Причина: {transfer_reason}"

        current_note = asset.note or ""
        asset.note = f"{transfer_note}\n{current_note}" if current_note else transfer_note

        async with self._uow:
            updated_asset = await self._uow.stationary_asset_repository.update(asset)

        return updated_asset

    async def delete_asset(self, asset_id: UUID) -> None:
        """
        Удалить актив

        :param asset_id: ID актива
        """
        # Проверяем существование актива
        await self.get_by_id(asset_id)

        async with self._uow:
            await self._uow.stationary_asset_repository.delete(asset_id)

    async def get_statistics(
            self,
            filter_params: StationaryAssetFilterParams
    ) -> StationaryAssetStatisticsSchema:
        """
        Получить статистику активов

        :param filter_params: Параметры фильтрации
        :return: Статистика активов
        """
        filters = filter_params.to_dict(exclude_none=True)
        return await self._stationary_asset_repository.get_statistics(filters)

    async def confirm_asset(self, asset_id: UUID) -> StationaryAssetDomain:
        """
        Подтвердить актив

        :param asset_id: ID актива
        :return: Обновленная доменная модель актива
        """
        asset = await self.get_by_id(asset_id)
        asset.confirm_asset()

        async with self._uow:
            updated_asset = await self._uow.stationary_asset_repository.update(asset)

        return updated_asset

    async def load_assets_from_bg_file(self, file_path: str = None) -> List[StationaryAssetDomain]:
        """
        Загрузить активы из файла BG (временно, пока нет интеграции)

        :param file_path: Путь к JSON файлу с данными BG
        :return: Список созданных активов
        """
        if not file_path:
            # Используем файл по умолчанию
            project_root = Path(__file__).parent.parent.parent.parent
            file_path = project_root / "data" / "bg_responses" / "stationary_assets_response.json"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                bg_data = json.load(f)

            # Преобразуем данные BG в доменные модели
            assets_to_create = []
            for item in bg_data:
                # Проверяем, что актив еще не существует
                if not await self._stationary_asset_repository.exists_by_bg_asset_id(item.get("id", "")):
                    # Находим или создаем пациента по данным из BG
                    patient_data = item.get("patient", {})
                    patient_iin = patient_data.get("personin", "")

                    if patient_iin:
                        # Пытаемся найти существующего пациента
                        patient = await self._patients_service.get_by_id(patient_iin)

                        if patient:
                            asset_domain = map_bg_response_to_domain(item, patient.id)
                            assets_to_create.append(asset_domain)
                        else:
                            self._logger.warning(
                                f"Пациент с ИИН {patient_iin} не найден, пропускаем актив {item.get('id', '')}")
                    else:
                        self._logger.warning(f"Отсутствует ИИН пациента в данных BG для актива {item.get('id', '')}")

            if not assets_to_create:
                self._logger.info("Все активы из файла уже существуют в базе данных")
                return []

            # Массовое создание активов
            async with self._uow:
                created_assets = await self._uow.stationary_asset_repository.bulk_create(
                    assets_to_create
                )

            self._logger.info(f"Успешно загружено {len(created_assets)} активов из файла BG")
            return created_assets

        except FileNotFoundError:
            self._logger.error(f"Файл BG данных не найден: {file_path}")
            raise ValueError(_("Файл с данными BG не найден"))
        except json.JSONDecodeError:
            self._logger.error(f"Ошибка парсинга JSON файла: {file_path}")
            raise ValueError(_("Ошибка в формате файла данных BG"))
        except Exception as e:
            self._logger.error(f"Ошибка при загрузке данных из файла BG: {str(e)}")
            raise ValueError(_("Ошибка при загрузке данных из файла BG"))