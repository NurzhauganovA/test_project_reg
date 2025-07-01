from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import Integer, and_, cast, func, or_, select
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.sql.elements import ClauseElement
from sqlalchemy.sql.expression import column

from src.apps.registry.domain.models.schedule import ScheduleDomain
from src.apps.registry.infrastructure.db_models.models import Schedule, ScheduleDay
from src.apps.registry.interfaces.repository_interfaces import (
    ScheduleRepositoryInterface,
)
from src.apps.registry.mappers import (
    map_schedule_db_entity_to_domain,
    map_schedule_domain_to_db_entity,
)
from src.apps.users.infrastructure.db_models.models import User
from src.shared.infrastructure.base import BaseRepository


class ScheduleRepositoryImpl(BaseRepository, ScheduleRepositoryInterface):
    async def get_total_number_of_schedules(self) -> int:
        query = select(func.count(Schedule.id))
        result = await self._async_db_session.execute(query)

        return result.scalar_one()

    async def get_by_id(self, id: UUID) -> Optional[ScheduleDomain]:
        result = await self._async_db_session.execute(
            select(Schedule).where(Schedule.id == id)
        )
        schedule = result.scalar_one_or_none()
        if schedule:
            return map_schedule_db_entity_to_domain(schedule)

        return None

    async def get_schedule_by_day_id(self, day_id: UUID) -> Optional[ScheduleDomain]:
        query = select(Schedule).join(ScheduleDay).where(ScheduleDay.id == day_id)

        result = await self._async_db_session.execute(query)
        schedule_db_model = result.scalar_one_or_none()

        if schedule_db_model is None:
            return None

        schedule_domain = map_schedule_db_entity_to_domain(schedule_db_model)

        return schedule_domain

    async def get_schedules(
        self,
        filters: Dict[str, Any],
        page: int = 1,
        limit: int = 30,
    ) -> List[ScheduleDomain]:
        query = select(Schedule).join(Schedule.doctor)

        if filters.get("name_filter"):
            query = query.where(Schedule.schedule_name == filters["name_filter"])

        if filters.get("doctor_id_filter"):
            query = query.where(Schedule.doctor_id == filters["doctor_id_filter"])

        if filters.get("status_filter") is not None:
            query = query.where(Schedule.is_active == filters["status_filter"])

        if filters.get("serviced_area_number_filter") is not None:
            query = query.where(
                and_(
                    Schedule.doctor.has(
                        User.attachment_data["area_number"].isnot(None)
                    ),
                    Schedule.doctor.has(
                        cast(User.attachment_data["area_number"].astext, Integer)
                        == filters["serviced_area_number_filter"]
                    ),
                )
            )

        if filters.get("doctor_full_name_filter"):
            full_value = filters["doctor_full_name_filter"].strip().lower()
            parts = [p for p in full_value.split() if p]
            name_clauses = [
                or_(
                    func.lower(User.first_name).ilike(f"%{part}%"),
                    func.lower(User.last_name).ilike(f"%{part}%"),
                    func.lower(func.coalesce(User.middle_name, "")).ilike(f"%{part}%"),
                )
                for part in parts
            ]
            if name_clauses:
                query = query.where(and_(*name_clauses))

        # Filter by doctor's specialties
        specialization_names: List[str] = (
            filters.get("doctor_specializations_filter") or []
        )
        specialization_clauses: List[ClauseElement] = []
        if specialization_names:
            elements_source = func.jsonb_array_elements(
                User.specializations
            ).table_valued(column("value", JSONB), name="unnested_specs_alias")
            element_name_as_text = elements_source.c.value.op("->>")("name")

            for spec in specialization_names:
                if spec:
                    exists_clause = (
                        select(True)
                        .select_from(elements_source)
                        .where(
                            func.lower(element_name_as_text).ilike(f"%{spec.lower()}%")
                        )
                        .exists()
                    )
                    specialization_clauses.append(exists_clause)
            if specialization_clauses:
                query = query.where(or_(*specialization_clauses))

        # Pagination
        query = query.limit(limit).offset((page - 1) * limit)

        result = await self._async_db_session.execute(query)
        schedules = result.scalars().all()

        return [map_schedule_db_entity_to_domain(s) for s in schedules]

    async def add(self, schedule_domain: ScheduleDomain) -> ScheduleDomain:
        new_schedule = map_schedule_domain_to_db_entity(schedule_domain)

        self._async_db_session.add(new_schedule)
        await self._async_db_session.flush()
        await self._async_db_session.refresh(new_schedule)

        return map_schedule_db_entity_to_domain(new_schedule)

    async def update(self, schedule_domain: ScheduleDomain) -> ScheduleDomain:
        result = await self._async_db_session.execute(
            select(Schedule).where(Schedule.id == schedule_domain.id)
        )
        existing = result.scalar_one_or_none()

        # Updating fields...
        existing.doctor_id = schedule_domain.doctor_id
        existing.schedule_name = schedule_domain.schedule_name
        existing.period_start = schedule_domain.period_start
        existing.period_end = schedule_domain.period_end
        existing.is_active = schedule_domain.is_active
        existing.appointment_interval = schedule_domain.appointment_interval

        self._async_db_session.add(existing)
        await self._async_db_session.flush()
        await self._async_db_session.refresh(existing)

        return map_schedule_db_entity_to_domain(existing)

    async def delete(self, id: UUID) -> None:
        result = await self._async_db_session.execute(
            select(Schedule).where(Schedule.id == id)
        )
        schedule = result.scalar_one_or_none()

        await self._async_db_session.delete(schedule)
        await self._async_db_session.commit()
