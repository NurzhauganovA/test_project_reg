from datetime import date
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from src.apps.patients.domain.enums import (
    PatientGenderEnum,
    PatientMaritalStatusEnum,
    PatientProfileStatusEnum,
    PatientSocialStatusEnum,
)
from src.apps.patients.infrastructure.api.schemas.jsonb_fields_schemas import (
    PatientAddressItemSchema,
    PatientContactInfoItemSchema,
    PatientRelativeItemSchema,
)
from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class ResponsePatientSchema(BaseModel):
    id: UUID
    iin: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    maiden_name: Optional[str] = None
    date_of_birth: date
    gender: PatientGenderEnum
    citizenship_id: int
    nationality_id: int
    financing_sources_ids: List[int]
    context_attributes_ids: List[int]
    social_status: PatientSocialStatusEnum
    marital_status: PatientMaritalStatusEnum
    attached_clinic_id: int
    relatives: Optional[List[PatientRelativeItemSchema]] = None
    addresses: Optional[List[PatientAddressItemSchema]] = None
    contact_info: Optional[List[PatientContactInfoItemSchema]] = None
    profile_status: PatientProfileStatusEnum


class MultiplePatientsResponseSchema(BaseModel):
    items: List[Union[ResponsePatientSchema,]]
    pagination: PaginationMetaDataSchema
