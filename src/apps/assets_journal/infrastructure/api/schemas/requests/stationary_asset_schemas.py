# src/apps/assets_journal/infrastructure/api/schemas/requests/stationary_asset_schemas.py

from datetime import datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
)


class CreateStationaryAssetSchema(BaseModel):
    """Схема для создания актива стационара"""

    # Данные из BG
    bg_asset_id: str = Field(default="6800000006671309", description="ID из BG системы")
    card_number: str = Field(default="123456789012", description="Номер карты пациента")

    # Данные о пациенте
    patient_full_name: str = Field(default="Пак Виталий Валерьевич", description="ФИО или ИИН пациента")
    patient_iin: str = Field(default="030611550511", description="ИИН пациента")
    patient_birth_date: datetime = Field(default_factory=lambda: datetime(2003, 6, 11, 0, 0),description="Дата рождения пациента")
    patient_address: str = Field(default="Выбрать", description="Адрес пациента")

    # Данные о получении актива
    receive_date: datetime = Field(default_factory=lambda: datetime(2025, 3, 22, 10, 55), description="Дата получения")
    receive_time: time = Field(default_factory=lambda: time(10, 55), description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: str = Field(default="Выбрать", description="Получено от")
    is_repeat: bool = Field(default=False, description="Повторный")

    # Данные пребывания в стационаре
    stay_period_start: Optional[datetime] = Field(default=None, description="В стационаре находился с")
    stay_period_end: Optional[datetime] = Field(default=None, description="до")
    stay_outcome: str = Field(default="Выбрать", description="Исход пребывания")
    diagnosis: str = Field(default="Введите код или наименование", description="Диагноз")

    # Участок и специалист
    area: str = Field(default="Выбрать", description="Участок")
    specialist: str = Field(default="Введите код или наименование", description="Специалист")

    # Примечание
    note: Optional[str] = Field(default="", description="Примечание")

    class Config:
        json_schema_extra = {
            "example": {
                "bg_asset_id": "6800000006671309",
                "card_number": "123456789012",
                "patient_full_name": "Пак Виталий Валерьевич",
                "patient_iin": "030611550511",
                "patient_birth_date": "2003-06-11T00:00:00",
                "patient_address": "г. Алматы, ул. Абая 150",
                "receive_date": "2025-03-22T10:55:00",
                "receive_time": "10:55:00",
                "actual_datetime": "2025-03-22T10:55:00",
                "received_from": "Поликлиника №1",
                "is_repeat": False,
                "stay_period_start": "2025-03-20T08:00:00",
                "stay_period_end": "2025-03-25T14:00:00",
                "stay_outcome": "Выздоровление",
                "diagnosis": "J06.9 Острая инфекция верхних дыхательных путей неуточненная",
                "area": "Педиатрический",
                "specialist": "Малышева А.О.",
                "note": "Пациент направлен для дальнейшего наблюдения"
            }
        }


class UpdateStationaryAssetSchema(BaseModel):
    """Схема для обновления актива стационара (на основе UI)"""

    # Данные о пациенте (только если можно редактировать)
    patient_full_name: Optional[str] = Field(default=None, description="ФИО или ИИН пациента")
    patient_iin: Optional[str] = Field(default=None, description="ИИН пациента")
    patient_birth_date: Optional[datetime] = Field(default=None, description="Дата рождения пациента")
    patient_address: Optional[str] = Field(default=None, description="Адрес пациента")

    # Данные о получении актива
    receive_date: Optional[datetime] = Field(default=None, description="Дата получения")
    receive_time: Optional[time] = Field(default=None, description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: Optional[str] = Field(default=None, description="Получено от")
    is_repeat: Optional[bool] = Field(default=None, description="Повторный")

    # Данные пребывания в стационаре
    stay_period_start: Optional[datetime] = Field(default=None, description="В стационаре находился с")
    stay_period_end: Optional[datetime] = Field(default=None, description="до")
    stay_outcome: Optional[str] = Field(default=None, description="Исход пребывания")
    diagnosis: Optional[str] = Field(default=None, description="Диагноз")

    # Участок и специалист
    area: Optional[str] = Field(default=None, description="Участок")
    specialist: Optional[str] = Field(default=None, description="Специалист")

    # Примечание
    note: Optional[str] = Field(default=None, description="Примечание")

    # Статусы (для внутреннего использования)
    status: Optional[AssetStatusEnum] = Field(default=None, description="Статус актива")
    delivery_status: Optional[AssetDeliveryStatusEnum] = Field(default=None, description="Статус доставки")

    class Config:
        json_schema_extra = {
            "example": {
                "diagnosis": "J06.9 Острая инфекция верхних дыхательных путей неуточненная",
                "stay_outcome": "Выздоровление",
                "area": "Педиатрический",
                "specialist": "Малышева А.О.",
                "note": "Пациент направлен для дальнейшего наблюдения",
                "status": "confirmed"
            }
        }