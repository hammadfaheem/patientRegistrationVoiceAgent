from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.exceptions import NotFoundError
from src.patients import service
from src.patients.models import Patient

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def valid_patient_id(patient_id: str, db: DbSession) -> Patient:
    patient = await service.get_patient(db, patient_id)
    if patient is None:
        raise NotFoundError(f"patient {patient_id} not found")
    return patient
