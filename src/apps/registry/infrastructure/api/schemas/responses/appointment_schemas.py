from datetime import date, time
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel

from src.apps.registry.domain.enums import (
    AppointmentInsuranceType,
    AppointmentStatusEnum,
    AppointmentTypeEnum,
)
from src.apps.users.infrastructure.schemas.user_schemas import UserSchema
from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class ResponseAppointmentSchema(BaseModel):
    id: int
    schedule_day_id: UUID
    start_time: time
    end_time: time  # Not in the 'appointments' DB table
    date: date  # Not in the 'appointments' DB table
    doctor: (
        UserSchema  # Not in the 'appointments' DB table, only 'doctor_id' is in the DB
    )
    patient: Optional[UserSchema] = (
        None  # Not in the 'appointments' DB table, only 'patient_id' is in the DB
    )
    status: AppointmentStatusEnum
    type: AppointmentTypeEnum
    insurance_type: AppointmentInsuranceType
    reason: str
    additional_services: Dict[str, bool]


class MultipleAppointmentsResponseSchema(BaseModel):
    items: List[ResponseAppointmentSchema]
    pagination: PaginationMetaDataSchema
