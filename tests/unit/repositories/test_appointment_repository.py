import datetime
import uuid

import pytest

from unittest.mock import Mock, AsyncMock

from src.apps.registry.domain.enums import AppointmentStatusEnum
from src.apps.registry.infrastructure.repositories.appointment_repository import AppointmentRepositoryImpl
from tests.fixtures import mock_async_db_session


@pytest.mark.asyncio
async def test_get_by_id_success(
        mock_async_db_session,
        dummy_domain_appointment,
        dummy_db_appointment,
        dummy_logger,
        mocker
) -> None:
    fake_result = mocker.MagicMock()
    fake_result.scalar_one_or_none = Mock(return_value=dummy_db_appointment)
    mock_async_db_session.execute.return_value = fake_result

    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    result = await repository.get_by_id(dummy_db_appointment.id)

    assert result is not None
    assert result.id == dummy_domain_appointment.id


@pytest.mark.asyncio
async def test_get_by_id_not_found(
        mock_async_db_session,
        dummy_domain_appointment,
        dummy_db_appointment,
        dummy_logger,
        mocker
) -> None:
    fake_result = mocker.MagicMock()
    fake_result.scalar_one_or_none = Mock(return_value=None)
    mock_async_db_session.execute.return_value = fake_result
    fake_id = 404

    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    result = await repository.get_by_id(fake_id)

    assert result is None


@pytest.mark.asyncio
async def test_add_appointment(
        mock_async_db_session,
        dummy_domain_appointment,
        dummy_db_appointment,
        dummy_logger,
        mocker
) -> None:
    fake_result = mocker.MagicMock()
    fake_result.scalar_one_or_none = Mock(return_value=dummy_db_appointment)
    mock_async_db_session.execute.return_value = fake_result

    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    result = await repository.add(dummy_domain_appointment)
    result.id = dummy_domain_appointment.id

    assert result is not None
    assert result.id == dummy_domain_appointment.id


@pytest.mark.asyncio
async def test_add_appointment_without_patient(
        mock_async_db_session,
        dummy_domain_appointment,
        dummy_db_appointment,
        dummy_logger,
        mocker
) -> None:
    fake_result = mocker.MagicMock()
    fake_result.scalar_one_or_none = Mock(return_value=dummy_db_appointment)
    mock_async_db_session.execute.return_value = fake_result

    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    dummy_domain_appointment.patient_id = None
    result = await repository.add(dummy_domain_appointment)
    result.id = dummy_domain_appointment.id

    assert result is not None
    assert result.id == dummy_domain_appointment.id


@pytest.mark.asyncio
async def test_update_appointment(
        mock_async_db_session,
        dummy_domain_appointment,
        dummy_db_appointment,
        dummy_logger,
        mocker
) -> None:
    dummy_db_appointment.patient_id = "updated_patient_id"
    dummy_db_appointment.status = AppointmentStatusEnum.CANCELLED

    dummy_domain_appointment.patient_id = "updated_patient_id"
    dummy_domain_appointment.status = AppointmentStatusEnum.CANCELLED

    fake_result = mocker.MagicMock()
    fake_result.scalar_one_or_none = Mock(return_value=dummy_db_appointment)
    mock_async_db_session.execute.return_value = fake_result

    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    result = await repository.update(dummy_domain_appointment)

    assert result is not None
    assert result.id == dummy_domain_appointment.id


@pytest.mark.asyncio
async def test_delete_appointment(
        mock_async_db_session,
        dummy_db_appointment,
        dummy_domain_appointment,
        dummy_logger,
        mocker
) -> None:
    fake_result = mocker.MagicMock()
    fake_result.scalar_one_or_none = Mock(return_value=dummy_db_appointment)
    mock_async_db_session.execute.return_value = fake_result

    mock_async_db_session.delete = AsyncMock()

    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    await repository.delete_by_id(dummy_domain_appointment.id)

    mock_async_db_session.delete.assert_called_once_with(dummy_db_appointment)


@pytest.mark.asyncio
async def test_get_by_schedule_success(
        mock_async_db_session,
        dummy_db_appointment,
        dummy_domain_appointment,
        dummy_logger,
        mocker
) -> None:
    fake_result = mocker.MagicMock()
    fake_scalars = mocker.MagicMock()
    fake_scalars.all.return_value = [dummy_db_appointment, dummy_db_appointment]
    fake_result.scalars.return_value = fake_scalars
    mock_async_db_session.execute.return_value = fake_result

    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    result = await repository.get_by_schedule_id(
        dummy_db_appointment.schedule_id,
        page=1,
        limit=10
    )

    assert isinstance(result, list)
    assert result[0].id == dummy_domain_appointment.id
    assert result[1].id == dummy_db_appointment.id


@pytest.mark.asyncio
async def test_get_by_schedule_not_found(
        mock_async_db_session,
        dummy_logger,
        mocker
) -> None:
    fake_result = mocker.MagicMock(return_value=[])
    fake_result.scalars.return_value.all.return_value = fake_result
    mock_async_db_session.execute.return_value = fake_result
    fake_id = uuid.uuid4()

    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    result = await repository.get_by_schedule_id(
        fake_id,
        page=1,
        limit=10
    )

    assert isinstance(result, list)
    assert result == []


@pytest.mark.asyncio
async def test_get_appointments_by_schedule_and_period_success(
        mock_async_db_session,
        dummy_db_appointment,
        dummy_domain_appointment,
        dummy_logger,
        mocker
) -> None:
    fake_result = mocker.MagicMock()
    fake_scalars = mocker.MagicMock()
    fake_scalars.all.return_value = [dummy_db_appointment, dummy_db_appointment]
    fake_result.scalars.return_value = fake_scalars
    mock_async_db_session.execute.return_value = fake_result

    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    result = await repository.get_by_schedule_id_and_period(
        schedule_id=dummy_db_appointment.schedule_id,
        period_start=datetime.date(2025, 6, 3),
        period_end=datetime.date(2025, 8, 3),
    )

    assert isinstance(result, list)
    assert result[0].id == dummy_domain_appointment.id
    assert result[1].id == dummy_db_appointment.id


@pytest.mark.asyncio
async def test_get_appointments_by_schedule_and_period__not_found(
        mock_async_db_session,
        dummy_logger,
        mocker
) -> None:
    fake_result = mocker.MagicMock(return_value=[])
    fake_result.scalars.return_value.all.return_value = fake_result
    mock_async_db_session.execute.return_value = fake_result
    fake_id = uuid.uuid4()

    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    result = await repository.get_by_schedule_id_and_period(
        schedule_id=fake_id,
        period_start=datetime.date(2025, 6, 3),
        period_end=datetime.date(2025, 8, 3),
    )

    assert isinstance(result, list)
    assert result == []
