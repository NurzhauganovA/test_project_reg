from datetime import datetime, time
from typing import Optional

from src.apps.assets_journal.domain.models.stationary_asset import StationaryAssetDomain
from src.apps.assets_journal.infrastructure.api.schemas.requests.stationary_asset_schemas import (
    CreateStationaryAssetSchema,
)
from src.apps.assets_journal.infrastructure.api.schemas.responses.stationary_asset_schemas import (
    StationaryAssetResponseSchema,
    StationaryAssetListItemSchema,
)
from src.apps.assets_journal.infrastructure.db_models.models import StationaryAsset


def map_stationary_asset_domain_to_db(domain: StationaryAssetDomain) -> StationaryAsset:
    """Маппинг доменной модели в DB модель"""
    return StationaryAsset(
        id=domain.id,
        bg_asset_id=domain.bg_asset_id,
        card_number=domain.card_number,
        patient_full_name=domain.patient_full_name,
        patient_iin=domain.patient_iin,
        patient_birth_date=domain.patient_birth_date,
        patient_address=domain.patient_address,
        receive_date=domain.receive_date,
        receive_time=domain.receive_time,
        actual_datetime=domain.actual_datetime,
        received_from=domain.received_from,
        is_repeat=domain.is_repeat,
        stay_period_start=domain.stay_period_start,
        stay_period_end=domain.stay_period_end,
        stay_outcome=domain.stay_outcome,
        diagnosis=domain.diagnosis,
        area=domain.area,
        specialization=domain.specialization,
        specialist=domain.specialist,
        note=domain.note,
        status=domain.status,
        delivery_status=domain.delivery_status,
        has_confirm=domain.has_confirm,
        has_files=domain.has_files,
        has_refusal=domain.has_refusal,
    )


def map_stationary_asset_db_to_domain(db_asset: StationaryAsset) -> StationaryAssetDomain:
    """Маппинг DB модели в доменную модель"""
    return StationaryAssetDomain(
        id=db_asset.id,
        bg_asset_id=db_asset.bg_asset_id,
        card_number=db_asset.card_number,
        patient_full_name=db_asset.patient_full_name,
        patient_iin=db_asset.patient_iin,
        patient_birth_date=db_asset.patient_birth_date,
        patient_address=db_asset.patient_address,
        receive_date=db_asset.receive_date,
        receive_time=db_asset.receive_time,
        actual_datetime=db_asset.actual_datetime,
        received_from=db_asset.received_from,
        is_repeat=db_asset.is_repeat,
        stay_period_start=db_asset.stay_period_start,
        stay_period_end=db_asset.stay_period_end,
        stay_outcome=db_asset.stay_outcome,
        diagnosis=db_asset.diagnosis,
        area=db_asset.area,
        specialization=db_asset.specialization,
        specialist=db_asset.specialist,
        note=db_asset.note,
        status=db_asset.status,
        delivery_status=db_asset.delivery_status,
        has_confirm=db_asset.has_confirm,
        has_files=db_asset.has_files,
        has_refusal=db_asset.has_refusal,
        created_at=db_asset.created_at,
        updated_at=db_asset.changed_at,
    )


def map_stationary_asset_domain_to_full_response(domain: StationaryAssetDomain) -> StationaryAssetResponseSchema:
    """Маппинг доменной модели в полную схему ответа (для детального просмотра)"""
    return StationaryAssetResponseSchema(
        id=domain.id,
        bg_asset_id=domain.bg_asset_id,
        card_number=domain.card_number,
        patient_full_name=domain.patient_full_name,
        patient_iin=domain.patient_iin,
        patient_birth_date=domain.patient_birth_date,
        patient_address=domain.patient_address,
        receive_date=domain.receive_date,
        receive_time=domain.receive_time,
        actual_datetime=domain.actual_datetime,
        received_from=domain.received_from,
        is_repeat=domain.is_repeat,
        stay_period_start=domain.stay_period_start,
        stay_period_end=domain.stay_period_end,
        stay_outcome=domain.stay_outcome,
        diagnosis=domain.diagnosis,
        area=domain.area,
        specialist=domain.specialist,
        note=domain.note,
        status=domain.status,
        delivery_status=domain.delivery_status,
        has_confirm=domain.has_confirm,
        has_files=domain.has_files,
        has_refusal=domain.has_refusal,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
    )


def map_stationary_asset_domain_to_list_item(domain: StationaryAssetDomain) -> StationaryAssetListItemSchema:
    """Маппинг доменной модели в схему для списка"""
    return StationaryAssetListItemSchema(
        id=domain.id,
        card_number=domain.card_number,
        patient_full_name=domain.patient_full_name,
        patient_iin=domain.patient_iin,
        patient_birth_date=domain.patient_birth_date,
        specialization=domain.specialization,
        specialist=domain.specialist,
        area=domain.area,
        diagnosis=domain.diagnosis,
        status=domain.status,
        delivery_status=domain.delivery_status,
        receive_date=domain.receive_date,
        receive_time=domain.receive_time,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
    )


def map_create_schema_to_domain(create_schema: CreateStationaryAssetSchema) -> StationaryAssetDomain:
    """Маппинг схемы создания в доменную модель"""
    return StationaryAssetDomain(
        bg_asset_id=create_schema.bg_asset_id,
        card_number=create_schema.card_number,
        patient_full_name=create_schema.patient_full_name,
        patient_iin=create_schema.patient_iin,
        patient_birth_date=create_schema.patient_birth_date,
        patient_address=create_schema.patient_address,
        receive_date=create_schema.receive_date,
        receive_time=create_schema.receive_time,
        actual_datetime=create_schema.actual_datetime or create_schema.receive_date,
        received_from=create_schema.received_from,
        is_repeat=create_schema.is_repeat,
        stay_period_start=create_schema.stay_period_start,
        stay_period_end=create_schema.stay_period_end,
        stay_outcome=create_schema.stay_outcome,
        diagnosis=create_schema.diagnosis,
        area=create_schema.area,
        specialization=create_schema.specialization,
        specialist=create_schema.specialist,
        note=create_schema.note,
    )


def map_bg_response_to_domain(bg_data: dict) -> StationaryAssetDomain:
    """Маппинг ответа BG в доменную модель"""
    patient = bg_data.get("patient", {})

    # Парсинг дат из строк
    def parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('T', ' ').replace('Z', ''))
        except:
            return None

    # Парсинг времени
    def parse_time(date_str: Optional[str]) -> Optional[time]:
        if not date_str:
            return None
        try:
            dt = datetime.fromisoformat(date_str.replace('T', ' ').replace('Z', ''))
            return dt.time()
        except:
            return None

    # Получаем дату регистрации
    reg_datetime = parse_datetime(bg_data.get("regDate")) or datetime.utcnow()
    reg_time = parse_time(bg_data.get("regDate")) or time(9, 0)

    return StationaryAssetDomain(
        bg_asset_id=bg_data.get("id", ""),
        card_number=bg_data.get("cardNumber", ""),
        patient_full_name=patient.get("personFullName", ""),
        patient_iin=patient.get("personin", ""),
        patient_birth_date=parse_datetime(patient.get("birthDate")) or datetime.utcnow(),
        patient_address=bg_data.get("address", ""),
        receive_date=reg_datetime,
        receive_time=reg_time,
        actual_datetime=parse_datetime(bg_data.get("hospitalDate")) or reg_datetime,
        received_from=bg_data.get("orgHealthCareRequest", {}).get("name", ""),
        is_repeat=False,
        stay_period_start=parse_datetime(bg_data.get("hospitalDate")) or reg_datetime,
        stay_period_end=parse_datetime(bg_data.get("outDate")),
        stay_outcome=bg_data.get("treatmentOutcome", "Лечение"),
        diagnosis=bg_data.get("sick", {}).get("name", ""),
        area=bg_data.get("area", "Общий"),
        specialization=bg_data.get("specialization", ""),
        specialist=bg_data.get("directDoctor", ""),
        note=bg_data.get("addiditonalInformation"),
        has_confirm=bg_data.get("hasConfirm", "false").lower() == "true",
        has_files=bg_data.get("hasFiles", "false").lower() == "true",
        has_refusal=bg_data.get("hasRefusal", "false").lower() == "true",
    )