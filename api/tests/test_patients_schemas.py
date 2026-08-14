from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from src.patients.schemas import PatientCreate, PatientRead, PatientUpdate

VALID = dict(
    first_name="Jane",
    last_name="Doe",
    date_of_birth=date(1990, 3, 3),
    sex="Female",
    phone_number="(555) 123-4567",
    address_line_1="123 Main St",
    city="Springfield",
    state="il",
    zip_code="62704",
)


def test_valid_patient_normalizes_phone_and_state():
    patient = PatientCreate(**VALID)
    assert patient.phone_number == "5551234567"
    assert patient.state == "IL"


def test_rejects_future_date_of_birth():
    bad = {**VALID, "date_of_birth": date.today() + timedelta(days=1)}
    with pytest.raises(ValidationError):
        PatientCreate(**bad)


def test_rejects_invalid_state():
    bad = {**VALID, "state": "ZZ"}
    with pytest.raises(ValidationError):
        PatientCreate(**bad)


def test_rejects_short_phone_number():
    bad = {**VALID, "phone_number": "123"}
    with pytest.raises(ValidationError):
        PatientCreate(**bad)


def test_rejects_invalid_zip():
    bad = {**VALID, "zip_code": "abc"}
    with pytest.raises(ValidationError):
        PatientCreate(**bad)


def test_rejects_name_with_digits():
    bad = {**VALID, "first_name": "Jane2"}
    with pytest.raises(ValidationError):
        PatientCreate(**bad)


def test_preferred_language_defaults_to_english():
    patient = PatientCreate(**VALID)
    assert patient.preferred_language == "English"


def test_patient_update_allows_partial_fields():
    update = PatientUpdate(last_name="Smith")
    assert update.last_name == "Smith"
    assert update.first_name is None


def test_patient_read_builds_from_object_attributes():
    class FakeOrmPatient:
        patient_id = "11111111-1111-1111-1111-111111111111"
        first_name = "Jane"
        last_name = "Doe"
        date_of_birth = date(1990, 3, 3)
        sex = "Female"
        phone_number = "5551234567"
        email = None
        address_line_1 = "123 Main St"
        address_line_2 = None
        city = "Springfield"
        state = "IL"
        zip_code = "62704"
        insurance_provider = None
        insurance_member_id = None
        preferred_language = "English"
        emergency_contact_name = None
        emergency_contact_phone = None
        created_at = date(2026, 1, 1)
        updated_at = date(2026, 1, 1)

    read = PatientRead.model_validate(FakeOrmPatient())
    assert read.patient_id == "11111111-1111-1111-1111-111111111111"
