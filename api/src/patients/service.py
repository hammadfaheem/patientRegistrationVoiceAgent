import logging
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.patients.models import Patient
from src.patients.schemas import PatientCreate, PatientUpdate

logger = logging.getLogger(__name__)


def _digits_only(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


async def list_patients(
    db: AsyncSession,
    last_name: str | None = None,
    date_of_birth: date | None = None,
    phone_number: str | None = None,
) -> list[Patient]:
    query = select(Patient).where(Patient.deleted_at.is_(None))
    if last_name:
        query = query.where(Patient.last_name == last_name)
    if date_of_birth:
        query = query.where(Patient.date_of_birth == date_of_birth)
    if phone_number:
        query = query.where(Patient.phone_number == _digits_only(phone_number))
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_patient(db: AsyncSession, patient_id: str) -> Patient | None:
    query = select(Patient).where(Patient.patient_id == patient_id, Patient.deleted_at.is_(None))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_patient(db: AsyncSession, data: PatientCreate) -> Patient:
    patient = Patient(**data.model_dump())
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    logger.info("patient created: %s payload=%s", patient.patient_id, data.model_dump(mode="json"))
    return patient


async def update_patient(db: AsyncSession, patient: Patient, data: PatientUpdate) -> Patient:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    await db.commit()
    await db.refresh(patient)
    logger.info("patient updated: %s", patient.patient_id)
    return patient


async def soft_delete_patient(db: AsyncSession, patient: Patient) -> None:
    patient.deleted_at = datetime.now(UTC)
    await db.commit()
    logger.info("patient soft-deleted: %s", patient.patient_id)
