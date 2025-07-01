from datetime import time
from typing import Dict, Optional
from uuid import UUID

from src.apps.registry.domain.enums import (
    AppointmentInsuranceType,
    AppointmentStatusEnum,
    AppointmentTypeEnum,
)
from src.apps.registry.domain.exceptions import (
    AppointmentIsNotAvailableError,
    AppointmentIsNotBookedError,
)
from src.core.i18n import _


class AppointmentDomain:
    """Appointment domain class"""

    def __init__(
        self,
        *,
        id: Optional[int] = None,
        schedule_day_id: UUID,
        time: time,
        patient_id: Optional[UUID],
        status: AppointmentStatusEnum = AppointmentStatusEnum.BOOKED,
        type: AppointmentTypeEnum,
        insurance_type: AppointmentInsuranceType,
        reason: Optional[str] = None,
        additional_services: Optional[Dict[str, bool]] = None,
    ):
        self.id = id
        self.schedule_day_id = schedule_day_id
        self.time = time
        self.patient_id = patient_id
        self.status = status
        self.type = type
        self.insurance_type = insurance_type
        self.reason = reason
        self.additional_services = (
            additional_services if additional_services is not None else {}
        )

    def book(self):
        """Method for booking an appointment."""
        if self.status != AppointmentStatusEnum.FREE:
            raise AppointmentIsNotAvailableError(
                _("The entry is not available for booking.")
            )
        self.status = AppointmentStatusEnum.BOOKED

    def cancel(self):
        """Method for canceling a reservation."""
        if self.status != AppointmentStatusEnum.BOOKED:
            raise AppointmentIsNotBookedError(
                _("Only reserved appointments can be cancelled.")
            )
        self.status = AppointmentStatusEnum.CANCELLED
