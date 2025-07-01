from src.apps.registry.domain.models.appointment import AppointmentDomain
from src.apps.registry.domain.models.schedule import ScheduleDomain
from src.apps.registry.infrastructure.api.schemas.responses.schedule_day_schemas import (
    ResponseScheduleDaySchema,
)
from src.apps.registry.infrastructure.db_models.models import (
    Appointment,
    Schedule,
    ScheduleDay,
)


def map_appointment_db_entity_to_domain(
    appointment_from_db: Appointment,
) -> AppointmentDomain:
    return AppointmentDomain(
        id=appointment_from_db.id,
        schedule_day_id=appointment_from_db.schedule_day_id,
        time=appointment_from_db.time,
        patient_id=appointment_from_db.patient_id,
        status=appointment_from_db.status,
        type=appointment_from_db.type,
        insurance_type=appointment_from_db.insurance_type,
        reason=appointment_from_db.reason,
        additional_services=appointment_from_db.additional_services,
    )


def map_schedule_domain_to_db_entity(schedule_domain: ScheduleDomain) -> Schedule:
    return Schedule(
        doctor_id=schedule_domain.doctor_id,
        schedule_name=schedule_domain.schedule_name,
        period_start=schedule_domain.period_start,
        period_end=schedule_domain.period_end,
        appointment_interval=schedule_domain.appointment_interval,
        description=schedule_domain.description,
    )


def map_schedule_db_entity_to_domain(schedule_from_db: Schedule) -> ScheduleDomain:
    return ScheduleDomain(
        id=schedule_from_db.id,
        doctor_id=schedule_from_db.doctor_id,
        schedule_name=schedule_from_db.schedule_name,
        period_start=schedule_from_db.period_start,
        period_end=schedule_from_db.period_end,
        is_active=schedule_from_db.is_active,
        appointment_interval=schedule_from_db.appointment_interval,
        description=schedule_from_db.description,
    )


def map_schedule_day_db_entity_to_schema(
    schedule_day: ScheduleDay,
) -> ResponseScheduleDaySchema:
    return ResponseScheduleDaySchema(
        id=schedule_day.id,
        schedule_id=schedule_day.schedule_id,
        day_of_week=schedule_day.day_of_week,
        is_active=schedule_day.is_active,
        work_start_time=schedule_day.work_start_time,
        work_end_time=schedule_day.work_end_time,
        break_start_time=schedule_day.break_start_time,
        break_end_time=schedule_day.break_end_time,
        date=schedule_day.date,
    )
