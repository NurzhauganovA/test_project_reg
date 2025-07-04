from datetime import date
from typing import List, Optional
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
    PatientAttachmentDataItemSchema,
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
    context_attributes_ids: Optional[List[int]]
    social_status: PatientSocialStatusEnum
    marital_status: PatientMaritalStatusEnum
    attachment_data: Optional[PatientAttachmentDataItemSchema] = None
    relatives: Optional[List[PatientRelativeItemSchema]] = None
    addresses: Optional[List[PatientAddressItemSchema]] = None
    contact_info: Optional[List[PatientContactInfoItemSchema]] = None
    profile_status: PatientProfileStatusEnum


class MultiplePatientsResponseSchema(BaseModel):
    items: List[ResponsePatientSchema]
    pagination: PaginationMetaDataSchema
