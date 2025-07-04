from datetime import datetime, time

from sqlalchemy import Boolean, DateTime, Enum, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
)
from src.shared.infrastructure.base import (
    Base,
    ChangedAtMixin,
    CreatedAtMixin,
    PrimaryKey,
)


class StationaryAsset(Base, PrimaryKey, CreatedAtMixin, ChangedAtMixin):
    """
    Новая модель актива стационара под requests
    """
    __tablename__ = "stationary_assets"

    # Данные из BG
    bg_asset_id: Mapped[str] = mapped_column(String(50), nullable=True, unique=True)
    card_number: Mapped[str] = mapped_column(String(50), nullable=True)

    # Данные пациента
    patient_full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    patient_iin: Mapped[str] = mapped_column(String(12), nullable=True)
    patient_birth_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    patient_address: Mapped[str] = mapped_column(Text, nullable=True)

    # Данные о получении актива
    receive_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    receive_time: Mapped[time] = mapped_column(Time, nullable=True)
    actual_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    received_from: Mapped[str] = mapped_column(String(255), nullable=True)
    is_repeat: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)

    # Данные пребывания в стационаре
    stay_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    stay_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    stay_outcome: Mapped[str] = mapped_column(String(255), nullable=True)
    diagnosis: Mapped[str] = mapped_column(Text, nullable=True)

    # Участок и специалист
    area: Mapped[str] = mapped_column(String(255), nullable=True)
    specialist: Mapped[str] = mapped_column(String(255), nullable=True)

    # Примечание
    note: Mapped[str] = mapped_column(Text, nullable=True)

    # Статусы
    status: Mapped[AssetStatusEnum] = mapped_column(
        Enum(AssetStatusEnum), nullable=True, default=AssetStatusEnum.REGISTERED
    )
    delivery_status: Mapped[AssetDeliveryStatusEnum] = mapped_column(
        Enum(AssetDeliveryStatusEnum),
        nullable=True,
        default=AssetDeliveryStatusEnum.RECEIVED_AUTOMATICALLY
    )
    reg_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, default=datetime.utcnow
    )

    # Флаги для совместимости с BG
    has_confirm: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    has_files: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    has_refusal: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)