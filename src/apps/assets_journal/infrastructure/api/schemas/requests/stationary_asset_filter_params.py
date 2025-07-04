from datetime import datetime
from typing import Optional

from fastapi import Query

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
)


class StationaryAssetFilterParams:
    """Параметры фильтрации активов стационара (на основе UI)"""

    def __init__(
            self,
            # Поиск по пациенту
            patient_search: Optional[str] = Query(
                None,
                description="Поиск по ФИО или ИИН пациента"
            ),

            # Период
            date_from: Optional[datetime] = Query(
                None,
                description="Дата начала периода"
            ),
            date_to: Optional[datetime] = Query(
                None,
                description="Дата окончания периода"
            ),

            # Статус актива
            status: Optional[AssetStatusEnum] = Query(
                None,
                description="Статус актива"
            ),

            # Статус доставки
            delivery_status: Optional[AssetDeliveryStatusEnum] = Query(
                None,
                description="Статус доставки"
            ),

            # Участок
            area: Optional[str] = Query(
                None,
                description="Участок (например: 17-Терапевтический)"
            ),

            # Специализация
            specialization: Optional[str] = Query(
                None,
                description="Специализация (например: Педиатр)"
            ),

            # Специалист
            specialist: Optional[str] = Query(
                None,
                description="Специалист (например: Малышева А.О.)"
            )
    ):
        self.patient_search = patient_search
        self.date_from = date_from
        self.date_to = date_to
        self.status = status
        self.delivery_status = delivery_status
        self.area = area
        self.specialization = specialization
        self.specialist = specialist

    def to_dict(self, exclude_none: bool = True) -> dict:
        """Преобразовать в словарь для передачи в репозиторий"""
        data = vars(self)
        return {
            key: value
            for key, value in data.items()
            if not exclude_none or value is not None
        }