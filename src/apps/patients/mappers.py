from datetime import date, datetime
from typing import Any, Dict, List, Optional

from src.apps.patients.domain.patient import (
    PatientAddressDomain,
    PatientContactInfoDomain,
    PatientDomain,
    PatientRelativeDomain,
)
from src.apps.patients.infrastructure.api.schemas.jsonb_fields_schemas import (
    PatientAddressItemSchema,
    PatientContactInfoItemSchema,
    PatientRelativeItemSchema,
)
from src.apps.patients.infrastructure.api.schemas.requests.patient_request_schemas import (
    CreatePatientSchema,
    UpdatePatientSchema,
)
from src.apps.patients.infrastructure.api.schemas.responses.patient_response_schemas import (
    ResponsePatientSchema,
)
from src.apps.patients.infrastructure.db_models.patients import SQLAlchemyPatient


def get_enum_value(val):
    if hasattr(val, "value"):
        return val.value

    return val


def ensure_date(val):
    """Converts a string to a date if needed."""
    if val is None:
        return None
    if isinstance(val, date):
        return val
    if isinstance(val, str):
        try:
            return datetime.strptime(val, "%Y-%m-%d").date()
        except Exception:
            raise ValueError(f"Invalid date string: {val!r}")

    raise ValueError(f"Unknown date type: {type(val)}")


def map_patient_db_entity_to_domain(db_patient: SQLAlchemyPatient) -> PatientDomain:
    """
    Maps SQLAlchemy patient entity to a domain model.
    """
    relatives = (
        [
            PatientRelativeDomain(
                type=relative.get("type"),
                full_name=relative.get("full_name"),
                iin=relative.get("iin"),
                birth_date=relative.get("birth_date"),
                phone=relative.get("phone"),
                relation_comment=relative.get("relation_comment"),
            )
            for relative in (db_patient.relatives or [])
        ]
        if db_patient.relatives is not None
        else None
    )

    addresses = (
        [
            PatientAddressDomain(
                type=address.get("type"),
                value=address.get("value"),
                is_primary=address.get("is_primary"),
            )
            for address in (db_patient.addresses or [])
        ]
        if db_patient.addresses is not None
        else None
    )

    contact_info = (
        [
            PatientContactInfoDomain(
                type=contact_info_record.get("type"),
                value=contact_info_record.get("value"),
                is_primary=contact_info_record.get("is_primary"),
            )
            for contact_info_record in (db_patient.contact_info or [])
        ]
        if db_patient.contact_info is not None
        else None
    )

    financing_sources_ids = [source.id for source in db_patient.financing_sources or []]
    context_attributes_ids = [
        attribute.id for attribute in db_patient.additional_attributes or []
    ]

    return PatientDomain(
        id=db_patient.id,
        iin=db_patient.iin,
        first_name=db_patient.first_name,
        last_name=db_patient.last_name,
        middle_name=db_patient.middle_name,
        maiden_name=db_patient.maiden_name,
        date_of_birth=db_patient.date_of_birth,
        gender=db_patient.gender,
        citizenship_id=db_patient.citizenship_id,
        nationality_id=db_patient.nationality_id,
        financing_sources_ids=financing_sources_ids,
        context_attributes_ids=context_attributes_ids,
        social_status=db_patient.social_status,
        marital_status=db_patient.marital_status,
        attached_clinic_id=db_patient.attached_clinic_id,
        relatives=relatives,
        addresses=addresses,
        contact_info=contact_info,
        profile_status=db_patient.profile_status,
    )


def map_patient_domain_to_db_entity(patient: PatientDomain) -> SQLAlchemyPatient:
    """
    Converts PatientDomain to SQLAlchemyPatient for saving to the DB.

    - Enum fields (.gender, .social_status, .marital_status, .profile_status)
    are converted to string values .value.
    - date_of_birth goes directly to the Date column.
    - JSONB list fields (relatives, addresses, contact_info):
    * each element is converted to a dictionary with basic types,
    * dates to an ISO string,
    * enum values to strings.
    """
    relatives_json: Optional[List[Dict[str, Any]]] = None
    if patient.relatives is not None:
        relatives_json = []
        for relative in patient.relatives:
            birth_date_val = ensure_date(relative.birth_date)
            relatives_json.append(
                {
                    "type": get_enum_value(relative.type),
                    "full_name": relative.full_name,
                    "iin": relative.iin,
                    "birth_date": (
                        birth_date_val.isoformat() if birth_date_val else None
                    ),
                    "phone": relative.phone,
                    "relation_comment": relative.relation_comment,
                }
            )

    addresses_json: Optional[List[Dict[str, Any]]] = None
    if patient.addresses is not None:
        addresses_json = []
        for addr in patient.addresses:
            addresses_json.append(
                {
                    "type": get_enum_value(addr.type),
                    "value": addr.value,
                    "is_primary": addr.is_primary,
                }
            )

    contact_info_json: Optional[List[Dict[str, Any]]] = None
    if patient.contact_info is not None:
        contact_info_json = []
        for contact_info in patient.contact_info:
            contact_info_json.append(
                {
                    "type": get_enum_value(contact_info.type),
                    "value": contact_info.value,
                    "is_primary": contact_info.is_primary,
                }
            )

    db_patient = SQLAlchemyPatient(
        iin=patient.iin,
        first_name=patient.first_name,
        last_name=patient.last_name,
        middle_name=patient.middle_name,
        maiden_name=patient.maiden_name,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender.value if patient.gender else None,
        social_status=patient.social_status.value if patient.social_status else None,
        marital_status=patient.marital_status.value if patient.marital_status else None,
        profile_status=patient.profile_status.value if patient.profile_status else None,
        citizenship_id=patient.citizenship_id,
        nationality_id=patient.nationality_id,
        attached_clinic_id=patient.attached_clinic_id,
        relatives=relatives_json,
        addresses=addresses_json,
        contact_info=contact_info_json,
    )

    return db_patient


def map_patient_domain_to_response_schema(
    domain: PatientDomain,
) -> ResponsePatientSchema:
    relatives = (
        [
            PatientRelativeItemSchema(
                type=relative.type,
                full_name=relative.full_name,
                iin=relative.iin,
                birth_date=relative.birth_date,
                phone=relative.phone,
                relation_comment=relative.relation_comment,
            )
            for relative in domain.relatives
        ]
        if domain.relatives is not None
        else None
    )
    addresses = (
        [
            PatientAddressItemSchema(
                type=address.type,
                value=address.value,
                is_primary=address.is_primary,
            )
            for address in domain.addresses
        ]
        if domain.addresses is not None
        else None
    )
    contact_info = (
        [
            PatientContactInfoItemSchema(
                type=contact.type,
                value=contact.value,
                is_primary=contact.is_primary,
            )
            for contact in domain.contact_info
        ]
        if domain.contact_info is not None
        else None
    )

    return ResponsePatientSchema(
        id=domain.id,
        iin=domain.iin,
        first_name=domain.first_name,
        last_name=domain.last_name,
        middle_name=domain.middle_name,
        maiden_name=domain.maiden_name,
        date_of_birth=domain.date_of_birth,
        gender=domain.gender,
        citizenship_id=domain.citizenship_id,
        nationality_id=domain.nationality_id,
        financing_sources_ids=domain.financing_sources_ids,
        context_attributes_ids=domain.context_attributes_ids,
        social_status=domain.social_status,
        marital_status=domain.marital_status,
        attached_clinic_id=domain.attached_clinic_id,
        relatives=relatives,
        addresses=addresses,
        contact_info=contact_info,
        profile_status=domain.profile_status,
    )


def map_create_schema_to_domain(schema: CreatePatientSchema) -> PatientDomain:
    relatives = (
        [
            PatientRelativeDomain(
                type=item.type,
                full_name=item.full_name,
                iin=item.iin,
                birth_date=item.birth_date,
                phone=item.phone,
                relation_comment=item.relation_comment,
            )
            for item in schema.relatives or []
        ]
        if schema.relatives is not None
        else None
    )

    addresses = (
        [
            PatientAddressDomain(
                type=item.type,
                value=item.value,
                is_primary=item.is_primary,
            )
            for item in schema.addresses or []
        ]
        if schema.addresses is not None
        else None
    )

    contact_info = (
        [
            PatientContactInfoDomain(
                type=item.type,
                value=item.value,
                is_primary=item.is_primary,
            )
            for item in schema.contact_info or []
        ]
        if schema.contact_info is not None
        else None
    )

    return PatientDomain(
        id=None,
        iin=schema.iin,
        first_name=schema.first_name,
        last_name=schema.last_name,
        middle_name=schema.middle_name,
        maiden_name=schema.maiden_name,
        date_of_birth=schema.date_of_birth,
        gender=schema.gender,
        citizenship_id=schema.citizenship_id,
        nationality_id=schema.nationality_id,
        financing_sources_ids=schema.financing_sources_ids,
        context_attributes_ids=schema.context_attributes_ids,
        social_status=schema.social_status,
        marital_status=schema.marital_status,
        attached_clinic_id=schema.attached_clinic_id,
        relatives=relatives,
        addresses=addresses,
        contact_info=contact_info,
        profile_status=schema.profile_status,
    )


def map_update_schema_to_domain(
    schema: UpdatePatientSchema, existing_patient: PatientDomain
) -> PatientDomain:
    """
    Maps a schema to an existing patient domain model.
    Updates only those fields that are explicitly defined in the schema.
    """

    def use(new, old):
        return new if new is not None else old

    # relatives
    if "relatives" in schema.model_fields_set:
        if schema.relatives is None or schema.relatives == []:
            relatives = None
        else:
            relatives = [
                PatientRelativeDomain(
                    type=item.type,
                    full_name=item.full_name,
                    iin=item.iin,
                    birth_date=item.birth_date,
                    phone=item.phone,
                    relation_comment=item.relation_comment,
                )
                for item in schema.relatives
            ]
    else:
        relatives = existing_patient.relatives

    # addresses
    if "addresses" in schema.model_fields_set:
        if schema.addresses is None or schema.addresses == []:
            addresses = None
        else:
            addresses = [
                PatientAddressDomain(
                    type=item.type,
                    value=item.value,
                    is_primary=item.is_primary,
                )
                for item in schema.addresses
            ]
    else:
        addresses = existing_patient.addresses

    # contact_info
    if "contact_info" in schema.model_fields_set:
        if schema.contact_info is None or schema.contact_info == []:
            contact_info = None
        else:
            contact_info = [
                PatientContactInfoDomain(
                    type=item.type,
                    value=item.value,
                    is_primary=item.is_primary,
                )
                for item in schema.contact_info
            ]
    else:
        contact_info = existing_patient.contact_info

    return PatientDomain(
        id=existing_patient.id,
        iin=use(schema.iin, existing_patient.iin),
        first_name=use(schema.first_name, existing_patient.first_name),
        last_name=use(schema.last_name, existing_patient.last_name),
        middle_name=use(schema.middle_name, existing_patient.middle_name),
        maiden_name=use(schema.maiden_name, existing_patient.maiden_name),
        date_of_birth=use(schema.date_of_birth, existing_patient.date_of_birth),
        gender=use(schema.gender, existing_patient.gender),
        citizenship_id=use(schema.citizenship_id, existing_patient.citizenship_id),
        nationality_id=use(schema.nationality_id, existing_patient.nationality_id),
        financing_sources_ids=use(
            schema.financing_sources_ids, existing_patient.financing_sources_ids
        ),
        context_attributes_ids=use(
            schema.context_attributes_ids, existing_patient.context_attributes_ids
        ),
        social_status=use(schema.social_status, existing_patient.social_status),
        marital_status=use(schema.marital_status, existing_patient.marital_status),
        attached_clinic_id=use(
            schema.attached_clinic_id, existing_patient.attached_clinic_id
        ),
        relatives=relatives,
        addresses=addresses,
        contact_info=contact_info,
        profile_status=use(schema.profile_status, existing_patient.profile_status),
    )
