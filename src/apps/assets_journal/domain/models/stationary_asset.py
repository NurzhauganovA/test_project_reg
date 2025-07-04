from datetime import datetime, time
from typing import Optional
from uuid import UUID

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
)


class StationaryAssetDomain:
    """
    Доменная модель актива стационара (под новые requests)
    """

    def __init__(
            self,
            *,
            id: Optional[UUID] = None,

            # Данные из BG
            bg_asset_id: str,
            card_number: str,

            # Данные о пациенте
            patient_full_name: str,
            patient_iin: str,
            patient_birth_date: datetime,
            patient_address: str,

            # Данные о получении актива
            receive_date: datetime,
            receive_time: time,
            actual_datetime: Optional[datetime] = None,
            received_from: str,
            is_repeat: bool = False,

            # Данные пребывания в стационаре
            stay_period_start: Optional[datetime] = None,
            stay_period_end: Optional[datetime] = None,
            stay_outcome: str,
            diagnosis: str,

            # Участок и специалист
            area: str,
            specialist: str,

            # Примечание
            note: Optional[str] = None,

            # Статусы
            status: AssetStatusEnum = AssetStatusEnum.REGISTERED,
            delivery_status: AssetDeliveryStatusEnum = AssetDeliveryStatusEnum.RECEIVED_AUTOMATICALLY,

            # Флаги для совместимости с BG
            has_confirm: bool = False,
            has_files: bool = False,
            has_refusal: bool = False,

            # Метаданные
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.bg_asset_id = bg_asset_id
        self.card_number = card_number
        self.patient_full_name = patient_full_name
        self.patient_iin = patient_iin
        self.patient_birth_date = patient_birth_date
        self.patient_address = patient_address
        self.receive_date = receive_date
        self.receive_time = receive_time
        self.actual_datetime = actual_datetime
        self.received_from = received_from
        self.is_repeat = is_repeat
        self.stay_period_start = stay_period_start
        self.stay_period_end = stay_period_end
        self.stay_outcome = stay_outcome
        self.diagnosis = diagnosis
        self.area = area
        self.specialist = specialist
        self.note = note
        self.status = status
        self.delivery_status = delivery_status
        self.has_confirm = has_confirm
        self.has_files = has_files
        self.has_refusal = has_refusal
        self.created_at = created_at
        self.updated_at = updated_at

    def update_status(self, new_status: AssetStatusEnum) -> None:
        """Обновить статус актива"""
        self.status = new_status
        self.updated_at = datetime.utcnow()

    def update_delivery_status(self, new_delivery_status: AssetDeliveryStatusEnum) -> None:
        """Обновить статус доставки"""
        self.delivery_status = new_delivery_status
        self.updated_at = datetime.utcnow()

    def add_note(self, note: str) -> None:
        """Добавить примечание"""
        self.note = note
        self.updated_at = datetime.utcnow()

    def update_diagnosis(self, diagnosis: str) -> None:
        """Обновить диагноз"""
        self.diagnosis = diagnosis
        self.updated_at = datetime.utcnow()

    def update_stay_outcome(self, outcome: str) -> None:
        """Обновить исход лечения"""
        self.stay_outcome = outcome
        self.updated_at = datetime.utcnow()

    def confirm_asset(self) -> None:
        """Подтвердить актив"""
        self.has_confirm = True
        self.status = AssetStatusEnum.CONFIRMED
        self.updated_at = datetime.utcnow()

    def refuse_asset(self, reason: str) -> None:
        """Отказать в активе"""
        self.has_refusal = True
        self.status = AssetStatusEnum.REFUSED
        self.note = f"Отказ: {reason}" + (f"\n{self.note}" if self.note else "")
        self.updated_at = datetime.utcnow()

    @property
    def is_confirmed(self) -> bool:
        """Проверить, подтвержден ли актив"""
        return self.has_confirm

    @property
    def is_refused(self) -> bool:
        """Проверить, отказан ли актив"""
        return self.has_refusal

    @property
    def patient_age(self) -> int:
        """Вычислить возраст пациента"""
        today = datetime.now().date()
        birth_date = self.patient_birth_date.date()
        age = today.year - birth_date.year
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1
        return age

    @property
    def receive_datetime(self) -> datetime:
        """Объединенная дата и время получения"""
        if self.actual_datetime:
            return self.actual_datetime
        # Объединяем дату и время
        return datetime.combine(self.receive_date.date(), self.receive_time)

    @property
    def additional_info(self) -> dict:
        """Дополнительная информация для UI"""
        return {
            "area": self.area,
            "specialist": self.specialist,
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