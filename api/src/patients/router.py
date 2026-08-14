from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.patients import service
from src.patients.dependencies import DbSession, valid_patient_id
from src.patients.models import Patient
from src.patients.schemas import PatientCreate, PatientRead, PatientUpdate
from src.schemas import Envelope

router = APIRouter(prefix="/patients", tags=["patients"])

ExistingPatient = Annotated[Patient, Depends(valid_patient_id)]


@router.get("", response_model=Envelope[list[PatientRead]])
async def list_patients_endpoint(
    db: DbSession,
    last_name: str | None = None,
    date_of_birth: date | None = None,
    phone_number: str | None = None,
):
    patients = await service.list_patients(db, last_name, date_of_birth, phone_number)
    return Envelope(data=[PatientRead.model_validate(p) for p in patients])


@router.get("/{patient_id}", response_model=Envelope[PatientRead])
async def get_patient_endpoint(patient: ExistingPatient):
    return Envelope(data=PatientRead.model_validate(patient))


@router.post("", response_model=Envelope[PatientRead], status_code=status.HTTP_201_CREATED)
async def create_patient_endpoint(payload: PatientCreate, db: DbSession):
    patient = await service.create_patient(db, payload)
    return Envelope(data=PatientRead.model_validate(patient))


@router.put("/{patient_id}", response_model=Envelope[PatientRead])
async def update_patient_endpoint(payload: PatientUpdate, patient: ExistingPatient, db: DbSession):
    updated = await service.update_patient(db, patient, payload)
    return Envelope(data=PatientRead.model_validate(updated))


@router.delete("/{patient_id}", response_model=Envelope[None])
async def delete_patient_endpoint(patient: ExistingPatient, db: DbSession):
    await service.soft_delete_patient(db, patient)
    return Envelope(data=None)
