from datetime import datetime, time
from typing import Optional
from uuid import UUID

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
)


class StationaryAssetDomain:
    """
    Доменная модель актива стационара
    """

    def __init__(
            self,
            *,
            id: Optional[UUID] = None,

            # Данные из BG
            bg_asset_id: Optional[str] = None,
            card_number: Optional[str] = None,

            # Данные о пациенте
            patient_full_name: str,
            patient_iin: str,
            patient_birth_date: datetime,
            patient_address: Optional[str] = None,

            # Данные о получении актива
            receive_date: datetime,
            receive_time: time,
            actual_datetime: datetime,
            received_from: str,
            is_repeat: bool,

            # Данные пребывания в стационаре
            stay_period_start: datetime,
            stay_period_end: Optional[datetime] = None,
            stay_outcome: Optional[str] = None,
            diagnosis: str,

            # Участок и специалист
            area: str,
            specialization: str,
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
        self.specialization = specialization
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
        current_note = self.note or ""
        self.note = f"Отказ: {reason}" + (f"\n{current_note}" if current_note else "")
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
    def patient_age(self) -> Optional[int]:
        """Вычислить возраст пациента"""
        if not self.patient_birth_date:
            return None
        today = datetime.now().date()
        birth_date = self.patient_birth_date.date()
        age = today.year - birth_date.year
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1
        return age

    @property
    def receive_datetime(self) -> Optional[datetime]:
        """Объединенная дата и время получения"""
        if self.actual_datetime:
            return self.actual_datetime
        if self.receive_date and self.receive_time:
            # Объединяем дату и время
            return datetime.combine(self.receive_date.date(), self.receive_time)
        return None

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


class StationaryAssetListItemDomain:
    """
    Доменная модель для списка активов стационара
    """

    def __init__(
            self,
            id: UUID,
            card_number: str,
            patient_full_name: str,
            patient_iin: str,
            patient_birth_date: datetime,
            specialization: str,
            specialist: str,
            area: str,
            diagnosis: str,
            status: AssetStatusEnum,
            delivery_status: AssetDeliveryStatusEnum,
            receive_date: datetime,
            receive_time: time,
            created_at: datetime,
            updated_at: datetime,
    ):
        self.id = id
        self.card_number = card_number
        self.patient_full_name = patient_full_name
        self.patient_iin = patient_iin
        self.patient_birth_date = patient_birth_date
        self.specialization = specialization
        self.specialist = specialist
        self.area = area
        self.diagnosis = diagnosis
        self.status = status
        self.delivery_status = delivery_status
        self.receive_date = receive_date
        self.receive_time = receive_time
        self.created_at = created_at
        self.updated_at = updated_at