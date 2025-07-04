from src.apps.catalogs.infrastructure.api.schemas.requests.insurance_info_catalog_request_schemas import (
    AddInsuranceInfoRecordSchema,
    UpdateInsuranceInfoRecordSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.insurance_info_catalog_response_schemas import (
    ResponseInsuranceInfoRecordSchema,
)
from src.apps.catalogs.infrastructure.db_models.models import (
    SQLAlchemyInsuranceInfoCatalogue,
)


def map_insurance_info_create_schema_to_db_entity(
    create_schema: AddInsuranceInfoRecordSchema,
) -> SQLAlchemyInsuranceInfoCatalogue:
    return SQLAlchemyInsuranceInfoCatalogue(
        financing_source_id=create_schema.financing_source_id,
        policy_number=create_schema.policy_number,
        company=create_schema.company,
        valid_from=create_schema.valid_from,
        valid_till=create_schema.valid_till,
        comment=create_schema.comment,
        patient_id=create_schema.patient_id,
    )


def map_insurance_info_update_schema_to_db_entity(
    db_entity: SQLAlchemyInsuranceInfoCatalogue,
    update_schema: UpdateInsuranceInfoRecordSchema,
) -> SQLAlchemyInsuranceInfoCatalogue:
    """
    Update the database entity fields with values from the update schema.

    Only fields explicitly provided in the update schema (`model_fields_set`) are updated.
    This allows distinguishing between fields that should remain unchanged and those
    that should be explicitly set to None (i.e., cleared).

    Args:
        db_entity (SQLAlchemyInsuranceInfoCatalogue): The existing database entity to update.
        update_schema (UpdateInsuranceInfoRecordSchema): The Pydantic update schema containing new values.

    Returns:
        SQLAlchemyInsuranceInfoCatalogue: The updated database entity with applied changes.
    """
    for field in update_schema.model_fields_set:
        value = getattr(update_schema, field)
        setattr(db_entity, field, value)

    return db_entity


def map_insurance_info_db_entity_to_response_schema(
    db_entity: SQLAlchemyInsuranceInfoCatalogue,
) -> ResponseInsuranceInfoRecordSchema:
    return ResponseInsuranceInfoRecordSchema(
        id=db_entity.id,
        financing_source_id=db_entity.financing_source_id,
        policy_number=db_entity.policy_number,
        company=db_entity.company,
        valid_from=db_entity.valid_from,
        valid_till=db_entity.valid_till,
        comment=db_entity.comment,
        patient_id=db_entity.patient_id,
    )
