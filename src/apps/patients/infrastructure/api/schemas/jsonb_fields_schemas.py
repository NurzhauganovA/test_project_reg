from datetime import date
from typing import Optional

from pydantic import BaseModel, field_validator

from src.apps.patients.domain.enums import (
    PatientAddressesEnum,
    PatientContactTypeEnum,
    PatientRelativesKinshipEnum,
)
from src.shared.helpers.validation_helpers import (
    validate_date_of_birth,
    validate_field_not_blank,
    validate_iin,
    validate_phone_number,
)


class PatientRelativeItemSchema(BaseModel):
    type: PatientRelativesKinshipEnum
    full_name: str
    iin: Optional[str] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    relation_comment: Optional[str] = None

    @field_validator("full_name", mode="before")
    def validate_full_name(cls, v):
        return validate_field_not_blank(v, "full_name")

    @field_validator("iin", mode="before")
    def validate_iin_field(cls, v):
        return validate_iin(v) if v is not None else v

    @field_validator("birth_date", mode="after")
    def validate_birth_date(cls, v):
        return validate_date_of_birth(v) if v is not None else v

    @field_validator("phone", mode="before")
    def validate_phone(cls, v):
        return validate_phone_number(v) if v is not None else v


class PatientAddressItemSchema(BaseModel):
    type: PatientAddressesEnum
    value: str
    is_primary: bool

    @field_validator("value", mode="before")
    def validate_value_field(cls, v):
        return validate_field_not_blank(v, "value")


class PatientContactInfoItemSchema(BaseModel):
    type: PatientContactTypeEnum
    value: str
    is_primary: bool

    @field_validator("value", mode="before")
    def validate_value_field(cls, v):
        return validate_field_not_blank(v, "value")
