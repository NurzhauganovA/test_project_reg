from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from src.apps.registry.domain.enums import AppointmentStatusEnum
from src.apps.registry.domain.models.appointment import AppointmentDomain
from src.apps.registry.domain.models.schedule import ScheduleDomain
from src.apps.registry.exceptions import (
    AppointmentOverlappingError,
    InvalidAppointmentInsuranceTypeError,
    InvalidAppointmentTimeError,
    NoInstanceFoundError,
    ScheduleDayNotFoundError,
    ScheduleIsNotActiveError,
)
from src.apps.registry.infrastructure.api.schemas.requests.appointment_schemas import (
    CreateAppointmentSchema,
    UpdateAppointmentSchema,
)
from src.apps.registry.infrastructure.api.schemas.responses.schedule_day_schemas import (
    ResponseScheduleDaySchema,
)
from src.apps.registry.interfaces.repository_interfaces import (
    AppointmentRepositoryInterface,
    ScheduleDayRepositoryInterface,
    ScheduleRepositoryInterface,
)
from src.apps.registry.interfaces.uow_interface import UnitOfWorkInterface
from src.apps.users.domain.models.user import UserDomain
from src.apps.users.interfaces.user_repository_interface import UserRepositoryInterface
from src.apps.users.services.user_service import UserService
from src.core.i18n import _
from src.core.logger import LoggerService
from src.shared.exceptions import ApplicationError
from src.shared.schemas.pagination_schemas import PaginationParams


class AppointmentService:
    def __init__(
        self,
        uow: UnitOfWorkInterface,
        logger: LoggerService,
        appointment_repository: AppointmentRepositoryInterface,
        schedule_repository: ScheduleRepositoryInterface,
        schedule_day_repository: ScheduleDayRepositoryInterface,
        user_service: UserService,
        user_repository: UserRepositoryInterface,
    ):
        self._uow = uow
        self._logger = logger
        self._appointment_repository = appointment_repository
        self._schedule_repository = schedule_repository
        self._schedule_day_repository = schedule_day_repository
        self._user_service = user_service
        self._user_repository = user_repository

    @staticmethod
    def __subtract_interval(base_date: date, base_time: time, minutes: int) -> datetime:
        """
        Subtracts a minute interval from combined date and time and returns datetime.
        """
        base_datetime = datetime.combine(base_date, base_time)
        return base_datetime - timedelta(minutes=minutes)

    @staticmethod
    def __add_interval(base_date: date, base_time: time, minutes: int) -> datetime:
        """
        Adds a minute interval to combined date and time and returns datetime.
        """
        base_datetime = datetime.combine(base_date, base_time)
        return base_datetime + timedelta(minutes=minutes)

    @staticmethod
    def _validate_appointment_within_working_hours(
        appointment_start_datetime: datetime,
        appointment_end_datetime: datetime,
        schedule_day,
        appointment_interval_minutes: int,
        requested_start_time: time,
    ) -> None:
        """
        Checks that the appointment time falls within the schedule's working hours and does not exceed them.

        :param appointment_start_datetime: appointment start datetime (within a fictitious date)
        :param appointment_end_datetime: appointment end datetime
        :param schedule_day: ScheduleDay object with working hours
        :param appointment_interval_minutes: appointment duration in minutes
        :param requested_start_time: appointment start time (time), for error message

        :raises InvalidAppointmentTimeError: if time is outside working hours
        """
        working_day_start_datetime = datetime.combine(
            schedule_day.date, schedule_day.work_start_time
        )
        working_day_end_datetime = datetime.combine(
            schedule_day.date, schedule_day.work_end_time
        )

        if (appointment_start_datetime < working_day_start_datetime) or (
            appointment_end_datetime > working_day_end_datetime
        ):
            raise InvalidAppointmentTimeError(
                status_code=409,
                detail=_(
                    "Selected time from %(start_time)s for %(appointment_interval)d-minute appointment "
                    "is outside working hours (%(work_start_time)s–%(work_end_time)s)."
                )
                % {
                    "start_time": requested_start_time,
                    "appointment_interval": appointment_interval_minutes,
                    "work_start_time": schedule_day.work_start_time,
                    "work_end_time": schedule_day.work_end_time,
                },
            )

    @staticmethod
    def _validate_doctor_profile_dict(
        doctor_dict: Dict,
        key: str,
        exc_class: type[ApplicationError],
        detail: str,
        *,
        status_code: int = 409,
    ):
        """
        Generic validation of doctor profile by dictionary settings.

        :param doctor_dict: dict, such as doctor.served_payment_types, doctor.patient_type, etc.
        :param key: value to validate (string or Enum.value)
        :param exc_class: exception class (e.g., InvalidAppointmentInsuranceTypeError)
        :param detail: detail for exception
        :param status_code: HTTP status code (default 409)
        """
        if not doctor_dict or not doctor_dict.get(key, False):
            raise exc_class(status_code=status_code, detail=detail)

    @staticmethod
    def _extract_key(obj: Any) -> str:
        """
        Extracts the string value of a key from an object.
        If the object has a 'value' attribute (e.g., Enum), returns it,
        otherwise casts the object to a string.

        :param obj: The object to get the key from (Enum or str)
        :return: The string representation of the key
        """
        return getattr(obj, "value", str(obj))

    @staticmethod
    def _check_support(
        obj: Any, doctor: UserDomain, attribute_name: str, error_message: str
    ):
        """
        Checks that the doctor's attribute_name contains a key extracted from the obj object.
        If the key is missing, raises an exception
        InvalidAppointmentInsuranceTypeError with the specified message.

        :param obj: Object with the key (Enum or str)
        :param doctor: UserDomain object with the doctor's profile
        :param attribute_name: Name of the doctor's attribute containing the supported types
        (e.g. 'served_patient_types')
        :param error_message: Error text if support is missing

        :raises InvalidAppointmentInsuranceTypeError: if support is missing
        """
        key = AppointmentService._extract_key(obj)
        served = getattr(doctor, attribute_name, [])
        if key not in served:
            raise InvalidAppointmentInsuranceTypeError(
                status_code=409,
                detail=_(error_message),
            )

    @staticmethod
    def _check_appointment_overlapping(
        appointment_start_datetime: datetime,
        appointment_end_datetime: datetime,
        existing_appointments: List[AppointmentDomain],
        schedule_day_date: date,
        appointment_interval_minutes: int,
        current_appointment_id: Optional[int] = None,
    ) -> None:
        """
        Checks that the new appointment time does not overlap with existing ones.

        :param appointment_start_datetime: new appointment start time
        :param appointment_end_datetime: new appointment end time
        :param existing_appointments: list of already scheduled appointments
        :param schedule_day_date: schedule date
        :param appointment_interval_minutes: appointment duration in minutes
        :param current_appointment_id: current appointment id (if updating) to ignore

        :raises AppointmentOverlappingError: if overlap is detected
        """
        for existing_appointment in existing_appointments:
            if (
                current_appointment_id is not None
                and existing_appointment.id == current_appointment_id
            ):
                continue

            if existing_appointment.status == AppointmentStatusEnum.CANCELLED:
                continue

            existing_start = datetime.combine(
                schedule_day_date, existing_appointment.time
            )
            existing_end = existing_start + timedelta(
                minutes=appointment_interval_minutes
            )

            if (appointment_start_datetime < existing_end) and (
                appointment_end_datetime > existing_start
            ):
                raise AppointmentOverlappingError(
                    status_code=409,
                    detail=_("The selected appointment slot is already booked."),
                )

    @staticmethod
    def _check_appointment_exists(
        appointment: Optional[AppointmentDomain], appointment_id: int
    ) -> None:
        if not appointment:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Appointment with ID: %(ID)s not found.")
                % {"ID": appointment_id},
            )

    @staticmethod
    def _check_schedule_exists(
        schedule: Optional[ScheduleDomain], schedule_id: UUID
    ) -> None:
        if not schedule:
            raise ScheduleDayNotFoundError(
                status_code=404,
                detail=_("Schedule for day ID %(ID)s not found.") % {"ID": schedule_id},
            )

    @staticmethod
    def _check_schedule_day_exists(
        schedule_day: Optional[ResponseScheduleDaySchema], schedule_day_id: UUID
    ) -> None:
        if not schedule_day:
            raise ScheduleDayNotFoundError(
                status_code=404,
                detail=_("Schedule day with ID %(ID)s not found.")
                % {"ID": schedule_day_id},
            )

    async def get_by_id(
        self, appointment_id: int
    ) -> Tuple[AppointmentDomain, Optional[UserDomain], UserDomain, time, date]:
        """
        Retrieves an appointment by its ID.

        :return: List of AppointmentDomain, UserDomain objects and time of the appointment end.
        """
        appointment = await self._appointment_repository.get_by_id(appointment_id)
        self._check_appointment_exists(appointment, appointment_id)

        schedule = await self._schedule_repository.get_schedule_by_day_id(
            appointment.schedule_day_id
        )
        self._check_schedule_exists(schedule, appointment.schedule_day_id)

        schedule_day = await self._schedule_day_repository.get_by_id(
            appointment.schedule_day_id
        )
        self._check_schedule_day_exists(schedule_day, appointment.schedule_day_id)

        # Get a doctor and patient
        doctor: UserDomain = await self._user_service.get_by_id(schedule.doctor_id)
        patient = (
            await self._user_service.get_by_id(appointment.patient_id)
            if appointment.patient_id
            else None
        )

        appointment_date: date = schedule_day.date

        # Calculate the appointment end time
        appointment_end_datetime = self.__add_interval(
            appointment_date, appointment.time, schedule.appointment_interval
        )
        appointment_end_time = appointment_end_datetime.time()

        return appointment, patient, doctor, appointment_end_time, appointment_date

    async def get_appointments_by_schedule_and_period(
        self,
        schedule_id: UUID,
        period_start: date,
        period_end: date,
        pagination_params: PaginationParams,
    ) -> Tuple[
        List[Tuple[AppointmentDomain, Optional[UserDomain], UserDomain, time, date]],
        int,
    ]:
        """
        Gets a list of appointments for the given schedule (schedule_id),
        whose appointment date falls within the range [period_start, period_end].

        :param pagination_params: Pagination parameters (limit, page).
        :param schedule_id: Schedule UUID.
        :param period_start: Start date of the period.
        :param period_end: End date of the period.
        :return: Tuple with -> [list of tuples with AppointmentDomain,
        UserDomain objects and appointment end time for each appointment, int].
        """
        # Check if the schedule exists
        existing_schedule = await self._schedule_repository.get_by_id(
            id=schedule_id,
        )
        if not existing_schedule:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Schedule with ID: %(ID)s not found.") % {"ID": schedule_id},
            )

        # Get appointments
        appointments = await self._appointment_repository.get_by_schedule_id_and_period(
            schedule_id=schedule_id,
            period_start=period_start,
            period_end=period_end,
            page=pagination_params.page,
            limit=pagination_params.limit,
        )

        # Count the total number of records in the DB
        total_amount_of_records: int = (
            await self._appointment_repository.get_total_number_of_appointments()
        )

        if not appointments:
            return [], total_amount_of_records

        doctor = await self._user_service.get_by_id(existing_schedule.doctor_id)

        results: List[
            Tuple[AppointmentDomain, Optional[UserDomain], UserDomain, time, date]
        ] = []
        for appointment in appointments:
            # Get appointment's patient if it's presented
            patient: UserDomain | None = await self._user_repository.get_by_id(
                appointment.patient_id
            )
            schedule = await self._schedule_repository.get_schedule_by_day_id(
                appointment.schedule_day_id
            )
            self._check_schedule_exists(schedule, appointment.schedule_day_id)

            # Get appointment's day
            schedule_day = await self._schedule_day_repository.get_by_id(
                appointment.schedule_day_id
            )
            self._check_schedule_day_exists(schedule_day, appointment.schedule_day_id)

            # Calculate the appointment end time
            end_datetime = self.__add_interval(
                schedule_day.date, appointment.time, schedule.appointment_interval
            )
            end_time = end_datetime.time()

            appointment_date = schedule_day.date

            results.append((appointment, patient, doctor, end_time, appointment_date))

        return results, total_amount_of_records

    async def update_appointment(
        self, appointment_id: int, schema: UpdateAppointmentSchema
    ) -> Tuple[AppointmentDomain, Optional[UserDomain], UserDomain, time, date]:
        # Check if the appointment exists
        appointment = await self._appointment_repository.get_by_id(appointment_id)
        self._check_appointment_exists(appointment, appointment_id)

        # Check if the patient exists if it's provided
        if schema.patient_id:
            await self._user_service.get_by_id(schema.patient_id)

        # Get schedule day
        schedule_day_id = schema.schedule_day_id or appointment.schedule_day_id
        schedule_day = await self._schedule_day_repository.get_by_id(schedule_day_id)
        self._check_schedule_day_exists(schedule_day, schedule_day_id)

        # Get schedule
        schedule = await self._schedule_repository.get_schedule_by_day_id(
            schedule_day_id
        )
        self._check_schedule_exists(schedule, schedule_day_id)

        # Get schedule's doctor
        doctor = await self._user_service.get_by_id(schedule.doctor_id)
        if not doctor:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("The specialist with ID: %(ID) not found.")
                % {"ID": schedule.doctor_id},
            )

        # Check support of specialist
        if schema.patient_type:
            AppointmentService._check_support(
                schema.patient_type,
                doctor,
                "served_patient_types",
                "The specialist does not support the provided patient type.",
            )
        if schema.referral_type:
            AppointmentService._check_support(
                schema.referral_type,
                doctor,
                "served_referral_types",
                "The specialist does not support the referral type.",
            )
        if schema.referral_origin:
            AppointmentService._check_support(
                schema.referral_origin,
                doctor,
                "served_referral_origins",
                "The specialist does not support the referral origin type.",
            )
        if schema.insurance_type:
            AppointmentService._check_support(
                schema.insurance_type,
                doctor,
                "served_payment_types",
                "The specialist does not support the provided insurance type.",
            )

        # Check if day or/and time have changed
        day_changed = bool(
            schema.schedule_day_id
            and schema.schedule_day_id != appointment.schedule_day_id
        )
        time_changed = bool(schema.time and schema.time != appointment.time)

        # If the day or time has changed, we check all business rules
        if day_changed or time_changed:
            if not schedule.is_active:
                raise ScheduleIsNotActiveError(
                    status_code=409,
                    detail=_("Associated schedule is inactive or not found."),
                )

            new_appointment_time = schema.time or appointment.time
            appointment_interval_minutes = schedule.appointment_interval
            appointment_start_datetime = datetime.combine(
                schedule_day.date, new_appointment_time
            )
            appointment_end_datetime = appointment_start_datetime + timedelta(
                minutes=appointment_interval_minutes
            )

            # Validate working hours
            self._validate_appointment_within_working_hours(
                appointment_start_datetime,
                appointment_end_datetime,
                schedule_day,
                appointment_interval_minutes,
                schema.time,
            )

            # Check break overlap
            if schedule_day.break_start_time and schedule_day.break_end_time:
                break_start_datetime = datetime.combine(
                    schedule_day.date, schedule_day.break_start_time
                )
                break_end_datetime = datetime.combine(
                    schedule_day.date, schedule_day.break_end_time
                )
                if (appointment_start_datetime < break_end_datetime) and (
                    appointment_end_datetime > break_start_datetime
                ):
                    raise InvalidAppointmentTimeError(
                        status_code=409,
                        detail=_("The appointment cannot overlap with the break time."),
                    )

            # Check overlapping appointments
            existing_appointments = (
                await self._appointment_repository.get_appointments_by_day_id(
                    schedule_day_id
                )
            )
            self._check_appointment_overlapping(
                appointment_start_datetime,
                appointment_end_datetime,
                existing_appointments,
                schedule_day.date,
                appointment_interval_minutes,
                current_appointment_id=appointment.id,
            )

            # Save new fields to domain
            appointment.schedule_day_id = schedule_day_id
            appointment.time = new_appointment_time

        # Apply other changes
        update_data = schema.model_dump(exclude_unset=True)
        for attr, val in update_data.items():
            setattr(appointment, attr, val)

        # Update in DB
        async with self._uow:
            updated_appointment = await self._uow.appointment_repository.update(
                appointment
            )

        # Load related patient and doctor
        patient = (
            await self._user_service.get_by_id(updated_appointment.patient_id)
            if schema.patient_id
            else None
        )

        end_datetime = self.__add_interval(
            schedule_day.date, updated_appointment.time, schedule.appointment_interval
        )
        end_time = end_datetime.time()
        appointment_date = schedule_day.date

        return updated_appointment, patient, doctor, end_time, appointment_date

    async def create_appointment(
        self, schedule_day_id: UUID, schema: CreateAppointmentSchema
    ) -> Tuple[AppointmentDomain, Optional[UserDomain], UserDomain, time, date]:
        # Get schedule day
        schedule_day = await self._schedule_day_repository.get_by_id(schedule_day_id)
        self._check_schedule_day_exists(schedule_day, schedule_day_id)

        # Get schedule and check active
        schedule = await self._schedule_repository.get_schedule_by_day_id(
            schedule_day_id
        )
        self._check_schedule_exists(schedule, schedule_day_id)
        if not schedule.is_active:
            raise ScheduleIsNotActiveError(
                status_code=409,
                detail=_("Associated schedule is inactive or not found."),
            )

        # Get doctor
        doctor = await self._user_service.get_by_id(schedule.doctor_id)
        if not doctor:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Doctor with ID: %(ID)s not found.")
                % {"ID": schedule.doctor_id},
            )

        # Check support for patient, referral, insurance types
        if schema.patient_type:
            AppointmentService._check_support(
                schema.patient_type,
                doctor,
                "served_patient_types",
                "The specialist does not support the provided patient type.",
            )
        if schema.referral_type:
            AppointmentService._check_support(
                schema.referral_type,
                doctor,
                "served_referral_types",
                "The specialist does not support the referral type.",
            )
        if schema.referral_origin:
            AppointmentService._check_support(
                schema.referral_origin,
                doctor,
                "served_referral_origins",
                "The specialist does not support the referral origin type.",
            )
        if schema.insurance_type:
            AppointmentService._check_support(
                schema.insurance_type,
                doctor,
                "served_payment_types",
                "The specialist does not support the provided insurance type.",
            )

        # Check patient exists if provided
        if schema.patient_id:
            # TODO: Replace with check in patients table instead of users
            await self._user_service.get_by_id(schema.patient_id)

        if not schedule_day.is_active:
            raise ScheduleIsNotActiveError(
                status_code=409,
                detail=_("Schedule day %(id)s is inactive.") % {"id": schedule_day_id},
            )

        appointment_interval = timedelta(minutes=schedule.appointment_interval)
        appointment_start_datetime = datetime.combine(schedule_day.date, schema.time)
        appointment_end_datetime = appointment_start_datetime + appointment_interval

        # Validate working hours
        self._validate_appointment_within_working_hours(
            appointment_start_datetime,
            appointment_end_datetime,
            schedule_day,
            schedule.appointment_interval,
            schema.time,
        )

        # Check break overlap
        if schedule_day.break_start_time and schedule_day.break_end_time:
            break_start_datetime = datetime.combine(
                schedule_day.date, schedule_day.break_start_time
            )
            break_end_datetime = datetime.combine(
                schedule_day.date, schedule_day.break_end_time
            )
            if (appointment_start_datetime < break_end_datetime) and (
                appointment_end_datetime > break_start_datetime
            ):
                raise InvalidAppointmentTimeError(
                    status_code=409,
                    detail=_("The appointment cannot overlap with the break time."),
                )

        # Check overlapping appointments
        existing_appointments = (
            await self._appointment_repository.get_appointments_by_day_id(
                schedule_day_id
            )
        )
        self._check_appointment_overlapping(
            appointment_start_datetime,
            appointment_end_datetime,
            existing_appointments,
            schedule_day.date,
            schedule.appointment_interval,
        )

        appointment = AppointmentDomain(
            schedule_day_id=schedule_day_id,
            time=schema.time,
            patient_id=schema.patient_id,
            type=schema.type,
            insurance_type=schema.insurance_type,
            reason=schema.reason,
            additional_services=schema.additional_services or {},
        )
        async with self._uow:
            created_appointment = await self._uow.appointment_repository.add(
                appointment
            )

        patient = (
            await self._user_service.get_by_id(schema.patient_id)
            if schema.patient_id
            else None
        )

        created_appointment_end_datetime = (
            datetime.combine(schedule_day.date, created_appointment.time)
            + appointment_interval
        )

        return (
            created_appointment,
            patient,
            doctor,
            created_appointment_end_datetime.time(),
            schedule_day.date,
        )

    async def delete_by_id(self, appointment_id: int) -> None:
        async with self._uow:
            appointment = await self._uow.appointment_repository.get_by_id(
                appointment_id
            )
            if not appointment:
                raise NoInstanceFoundError(
                    status_code=404,
                    detail=_("Appointment with ID: %(ID)s not found.")
                    % {"ID": appointment_id},
                )

            await self._uow.appointment_repository.delete_by_id(appointment_id)
