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
            # Поиск по пациенту (есть в UI)
            patient_search: Optional[str] = Query(
                None,
                description="Поиск по ФИО или ИИН пациента"
            ),

            # Период (есть в UI)
            date_from: Optional[datetime] = Query(
                None,
                description="Дата начала периода"
            ),
            date_to: Optional[datetime] = Query(
                None,
                description="Дата окончания периода"
            ),

            # Статус актива (есть в UI)
            status: Optional[AssetStatusEnum] = Query(
                None,
                description="Статус актива"
            ),

            # Статус доставки (есть в UI)
            delivery_status: Optional[AssetDeliveryStatusEnum] = Query(
                None,
                description="Статус доставки"
            ),

            # Участок (есть в UI)
            area: Optional[str] = Query(
                None,
                description="Участок (например: 17-Терапевтический)"
            ),

            # Специализация (есть в UI)
            specialization: Optional[str] = Query(
                None,
                description="Специализация (например: Педиатр)"
            ),

            # Специалист (есть в UI)
            specialist: Optional[str] = Query(
                None,
                description="Специалист (например: Малышева А.О.)"
            ),

            # Организация (длинное название в UI)
            organization: Optional[str] = Query(
                None,
                description="Организация (полное или частичное название)"
            ),

            # Дополнительные фильтры для внутреннего использования
            has_files: Optional[bool] = Query(
                None,
                description="Имеет файлы"
            ),

            is_repeat: Optional[bool] = Query(
                None,
                description="Повторный актив"
            ),

            # Диагноз
            diagnosis: Optional[str] = Query(
                None,
                description="Поиск по диагнозу"
            ),

            # Исход лечения
            stay_outcome: Optional[str] = Query(
                None,
                description="Исход пребывания в стационаре"
            ),
    ):
        self.patient_search = patient_search
        self.date_from = date_from
        self.date_to = date_to
        self.status = status
        self.delivery_status = delivery_status
        self.area = area
        self.specialization = specialization
        self.specialist = specialist
        self.organization = organization
        self.has_files = has_files
        self.is_repeat = is_repeat
        self.diagnosis = diagnosis
        self.stay_outcome = stay_outcome

    def to_dict(self, exclude_none: bool = True) -> dict:
        """Преобразовать в словарь для передачи в репозиторий"""
        data = vars(self)
        return {
            key: value
            for key, value in data.items()
            if not exclude_none or value is not None
        }