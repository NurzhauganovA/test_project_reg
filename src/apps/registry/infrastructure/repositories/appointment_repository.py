from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from src.apps.registry.domain.models.appointment import AppointmentDomain
from src.apps.registry.infrastructure.db_models.models import Appointment, ScheduleDay
from src.apps.registry.interfaces.repository_interfaces import (
    AppointmentRepositoryInterface,
)
from src.apps.registry.mappers import map_appointment_db_entity_to_domain
from src.shared.infrastructure.base import BaseRepository


class AppointmentRepositoryImpl(BaseRepository, AppointmentRepositoryInterface):
    async def get_total_number_of_appointments(self) -> int:
        query = select(func.count(Appointment.id))
        result = await self._async_db_session.execute(query)

        return result.scalar_one()

    async def get_by_id(self, id: int) -> Optional[AppointmentDomain]:
        result = await self._async_db_session.execute(
            select(Appointment).where(Appointment.id == id)
        )
        appointment = result.scalar_one_or_none()
        if appointment:
            return map_appointment_db_entity_to_domain(appointment)

        return None

    async def get_appointments_by_day_id(
        self, schedule_day_id: UUID
    ) -> List[AppointmentDomain]:
        result = await self._async_db_session.execute(
            select(Appointment)
            .where(Appointment.schedule_day_id == schedule_day_id)
            .order_by(Appointment.time)
        )
        db_rows = result.scalars().all()

        return [map_appointment_db_entity_to_domain(row) for row in db_rows]

    async def get_by_schedule_id(
        self, schedule_id: UUID, page: int = 1, limit: int = 30
    ) -> List[AppointmentDomain]:
        offset = (page - 1) * limit

        stmt = (
            select(Appointment)
            .join(Appointment.schedule_day)
            .where(ScheduleDay.schedule_id == schedule_id)
            .options(joinedload(Appointment.schedule_day))
            .order_by(ScheduleDay.date, Appointment.time)
            .offset(offset)
            .limit(limit)
        )

        result = await self._async_db_session.execute(stmt)
        rows = result.scalars().all()

        return [map_appointment_db_entity_to_domain(row) for row in rows]

    async def get_by_schedule_id_and_period(
        self,
        schedule_id: UUID,
        period_start: date,
        period_end: date,
        limit: int = 30,
        page: int = 1,
    ) -> List[AppointmentDomain]:
        stmt = (
            select(Appointment)
            .join(Appointment.schedule_day)
            .where(
                ScheduleDay.schedule_id == schedule_id,
                ScheduleDay.date >= period_start,
                ScheduleDay.date <= period_end,
            )
            .options(joinedload(Appointment.schedule_day))
            .order_by(ScheduleDay.date, Appointment.time)
        )

        stmt = stmt.limit(limit).offset((page - 1) * limit)

        result = await self._async_db_session.execute(stmt)
        rows = result.scalars().all()

        return [map_appointment_db_entity_to_domain(row) for row in rows]

    async def add(self, appointment: AppointmentDomain) -> AppointmentDomain:
        new_appointment = Appointment(
            schedule_day_id=appointment.schedule_day_id,
            time=appointment.time,
            patient_id=appointment.patient_id,
            status=appointment.status,
            type=appointment.type,
            insurance_type=appointment.insurance_type,
            reason=appointment.reason,
            additional_services=appointment.additional_services,
        )
        self._async_db_session.add(new_appointment)
        await self._async_db_session.flush()
        await self._async_db_session.refresh(new_appointment)

        return map_appointment_db_entity_to_domain(new_appointment)

    async def update(self, appointment: AppointmentDomain) -> AppointmentDomain:
        result = await self._async_db_session.execute(
            select(Appointment).where(Appointment.id == appointment.id)
        )
        existing = result.scalar_one_or_none()

        # Updating fields...
        existing.schedule_day_id = appointment.schedule_day_id
        existing.time = appointment.time
        existing.patient_id = appointment.patient_id
        existing.status = appointment.status
        existing.type = appointment.type
        existing.insurance_type = appointment.insurance_type
        existing.reason = appointment.reason
        existing.additional_services = appointment.additional_services

        self._async_db_session.add(existing)
        await self._async_db_session.flush()
        await self._async_db_session.refresh(existing)

        return map_appointment_db_entity_to_domain(existing)

    async def delete_by_id(self, id: int) -> None:
        result = await self._async_db_session.execute(
            select(Appointment).where(Appointment.id == id)
        )
        existing = result.scalar_one_or_none()

        await self._async_db_session.delete(existing)
        await self._async_db_session.commit()
