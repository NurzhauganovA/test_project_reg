from datetime import date
from typing import List, Optional
from uuid import UUID

from src.apps.patients.domain.enums import (
    PatientAddressesEnum,
    PatientContactTypeEnum,
    PatientGenderEnum,
    PatientMaritalStatusEnum,
    PatientProfileStatusEnum,
    PatientRelativesKinshipEnum,
    PatientSocialStatusEnum,
)


class PatientRelativeDomain:
    type: PatientRelativesKinshipEnum
    full_name: str
    iin: Optional[str]
    birth_date: Optional[date]
    phone: Optional[str]
    relation_comment: Optional[str]

    def __init__(
        self,
        type: PatientRelativesKinshipEnum,
        full_name: str,
        iin: Optional[str] = None,
        birth_date: Optional[date] = None,
        phone: Optional[str] = None,
        relation_comment: Optional[str] = None,
    ) -> None:
        self.type = type
        self.full_name = full_name
        self.iin = iin
        self.birth_date = birth_date
        self.phone = phone
        self.relation_comment = relation_comment


class PatientAddressDomain:
    type: PatientAddressesEnum
    value: str
    is_primary: bool

    def __init__(
        self, type: PatientAddressesEnum, value: str, is_primary: bool
    ) -> None:
        self.type = type
        self.value = value
        self.is_primary = is_primary


class PatientContactInfoDomain:
    type: PatientContactTypeEnum
    value: str
    is_primary: bool

    def __init__(
        self, type: PatientContactTypeEnum, value: str, is_primary: bool
    ) -> None:
        self.type = type
        self.value = value
        self.is_primary = is_primary


class PatientDomain:
    def __init__(
        self,
        *,
        id: Optional[UUID],
        iin: str,
        first_name: str,
        last_name: str,
        middle_name: Optional[str],
        maiden_name: Optional[str],
        date_of_birth: date,
        gender: Optional[PatientGenderEnum] = None,
        citizenship_id: int,
        nationality_id: int,
        financing_sources_ids: Optional[List[int]] = None,
        context_attributes_ids: Optional[List[int]] = None,
        social_status: Optional[PatientSocialStatusEnum] = None,
        marital_status: Optional[PatientMaritalStatusEnum] = None,
        attached_clinic_id: int,
        relatives: Optional[List[PatientRelativeDomain]],
        addresses: Optional[List[PatientAddressDomain]],
        contact_info: Optional[List[PatientContactInfoDomain]],
        profile_status: Optional[PatientProfileStatusEnum] = None,
    ) -> None:
        self.id = id
        self.iin = iin
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.maiden_name = maiden_name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.citizenship_id = citizenship_id
        self.nationality_id = nationality_id
        self.financing_sources_ids = financing_sources_ids or []
        self.context_attributes_ids = context_attributes_ids or []
        self.social_status = social_status
        self.marital_status = marital_status
        self.attached_clinic_id = attached_clinic_id
        self.relatives = relatives or []
        self.addresses = addresses or []
        self.contact_info = contact_info or []
        self.profile_status = profile_status
