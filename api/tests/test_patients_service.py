from datetime import date

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.database import Base
from src.patients import service
from src.patients.schemas import PatientCreate, PatientUpdate

VALID = dict(
    first_name="Jane",
    last_name="Doe",
    date_of_birth=date(1990, 3, 3),
    sex="Female",
    phone_number="5551234567",
    address_line_1="123 Main St",
    city="Springfield",
    state="IL",
    zip_code="62704",
)


@pytest.fixture
async def db_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    SessionFactory = async_sessionmaker(engine, expire_on_commit=False)
    async with SessionFactory() as session:
        yield session
    await engine.dispose()


async def test_create_then_get_patient(db_session):
    created = await service.create_patient(db_session, PatientCreate(**VALID))
    fetched = await service.get_patient(db_session, created.patient_id)
    assert fetched is not None
    assert fetched.last_name == "Doe"


async def test_get_missing_patient_returns_none(db_session):
    assert await service.get_patient(db_session, "does-not-exist") is None


async def test_list_patients_filters_by_last_name(db_session):
    await service.create_patient(db_session, PatientCreate(**VALID))
    await service.create_patient(db_session, PatientCreate(**{**VALID, "last_name": "Smith"}))

    matches = await service.list_patients(db_session, last_name="Doe")
    assert len(matches) == 1
    assert matches[0].last_name == "Doe"


async def test_list_patients_filters_by_phone_number_ignoring_formatting(db_session):
    await service.create_patient(db_session, PatientCreate(**VALID))
    matches = await service.list_patients(db_session, phone_number="(555) 123-4567")
    assert len(matches) == 1


async def test_update_patient_partially_changes_fields(db_session):
    created = await service.create_patient(db_session, PatientCreate(**VALID))
    updated = await service.update_patient(db_session, created, PatientUpdate(city="Chicago"))
    assert updated.city == "Chicago"
    assert updated.last_name == "Doe"


async def test_soft_delete_hides_patient_from_list_and_get(db_session):
    created = await service.create_patient(db_session, PatientCreate(**VALID))
    await service.soft_delete_patient(db_session, created)

    assert await service.get_patient(db_session, created.patient_id) is None
    assert await service.list_patients(db_session) == []
