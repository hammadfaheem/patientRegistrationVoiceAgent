from datetime import date

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.database import Base
from src.patients.models import Patient


async def test_patient_row_round_trips_with_generated_id_and_timestamps():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionFactory = async_sessionmaker(engine, expire_on_commit=False)
    async with SessionFactory() as session:
        patient = Patient(
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
        session.add(patient)
        await session.commit()
        await session.refresh(patient)

        assert patient.patient_id is not None
        assert patient.created_at is not None
        assert patient.updated_at is not None
        assert patient.deleted_at is None
        assert patient.preferred_language == "English"

    await engine.dispose()
