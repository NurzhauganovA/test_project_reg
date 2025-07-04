from datetime import datetime, time
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, computed_field

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
)
from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class StationaryAssetResponseSchema(BaseModel):
    """Схема ответа для актива стационара (под новые requests)"""

    # Основные поля
    id: UUID
    bg_asset_id: str
    card_number: str

    # Данные пациента
    patient_full_name: str
    patient_iin: str
    patient_birth_date: datetime
    patient_address: str

    # Данные о получении актива
    receive_date: datetime
    receive_time: time
    actual_datetime: Optional[datetime] = None
    received_from: str
    is_repeat: bool = False

    # Данные пребывания в стационаре
    stay_period_start: Optional[datetime] = None
    stay_period_end: Optional[datetime] = None
    stay_outcome: str
    diagnosis: str

    # Участок и специалист
    area: str
    specialist: str

    # Примечание
    note: Optional[str] = None

    # Статусы
    status: AssetStatusEnum
    delivery_status: AssetDeliveryStatusEnum

    # Флаги
    has_confirm: bool = False
    has_files: bool = False
    has_refusal: bool = False

    # Метаданные
    created_at: datetime
    updated_at: datetime

    # Computed fields для UI совместимости
    @computed_field
    @property
    def number(self) -> str:
        """Номер для UI (используем card_number)"""
        return self.card_number

    @computed_field
    @property
    def receive_datetime(self) -> datetime:
        """Объединенная дата и время получения"""
        if self.actual_datetime:
            return self.actual_datetime
        # Объединяем дату и время
        return datetime.combine(self.receive_date.date(), self.receive_time)

    @computed_field
    @property
    def birth_date(self) -> datetime:
        """Дата рождения для UI"""
        return self.patient_birth_date

    @computed_field
    @property
    def specialization(self) -> str:
        """Специализация (используем specialist)"""
        # Извлекаем специализацию из специалиста (например: "Педиатр - Малышева А.О.")
        if " - " in self.specialist:
            return self.specialist.split(" - ")[0]
        return "Не указано"

    @computed_field
    @property
    def specialist_name(self) -> str:
        """Имя специалиста"""
        # Извлекаем имя из специалиста
        if " - " in self.specialist:
            return self.specialist.split(" - ")[1]
        return self.specialist

    @computed_field
    @property
    def patient_age(self) -> int:
        """Возраст пациента"""
        today = datetime.now().date()
        birth_date = self.patient_birth_date.date()
        age = today.year - birth_date.year
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1
        return age

    @computed_field
    @property
    def additional_info(self) -> dict:
        """Дополнительная информация для UI"""
        return {
            "area": self.area,
            "specialist": self.specialist_name,
            "specialization": self.specialization,
            "diagnosis": self.diagnosis,
            "stay_outcome": self.stay_outcome,
            "status": self._get_status_display(),
            "delivery_status": self._get_delivery_status_display(),
            "is_repeat": self.is_repeat
        }

    def _get_status_display(self) -> str:
        """Получить отображаемое название статуса"""
        status_map = {
            AssetStatusEnum.REGISTERED: "Зарегистрирован",
            AssetStatusEnum.CONFIRMED: "Подтвержден",
            AssetStatusEnum.REFUSED: "Отказан",
            AssetStatusEnum.CANCELLED: "Отменен",
        }
        return status_map.get(self.status, "Неизвестно")

    def _get_delivery_status_display(self) -> str:
        """Получить отображаемое название статуса доставки"""
        status_map = {
            AssetDeliveryStatusEnum.RECEIVED_AUTOMATICALLY: "Получен автоматически",
            AssetDeliveryStatusEnum.PENDING_DELIVERY: "Ожидает доставки",
            AssetDeliveryStatusEnum.DELIVERED: "Доставлен",
        }
        return status_map.get(self.delivery_status, "Неизвестно")

    class Config:
        from_attributes = True


class MultipleStationaryAssetsResponseSchema(BaseModel):
    """Схема ответа для списка активов стационара"""

    items: List[StationaryAssetResponseSchema]
    pagination: PaginationMetaDataSchema


class StationaryAssetStatisticsSchema(BaseModel):
    """Схема статистики активов стационара"""

    total_assets: int
    confirmed_assets: int
    refused_assets: int
    pending_assets: int
    assets_with_files: int
    assets_with_rehabilitation_files: int