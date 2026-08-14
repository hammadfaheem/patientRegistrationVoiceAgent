from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from src.patients.constants import NAME_PATTERN, US_STATE_CODES, ZIP_PATTERN

Sex = Literal["Male", "Female", "Other", "Decline to Answer"]


def _normalize_phone(value: str | None) -> str | None:
    if value is None:
        return None
    digits = "".join(ch for ch in value if ch.isdigit())
    if len(digits) != 10:
        raise ValueError("phone number must contain exactly 10 digits")
    return digits


def _reject_future_dob(value: date | None) -> date | None:
    if value is not None and value > date.today():
        raise ValueError("date_of_birth cannot be in the future")
    return value


def _normalize_state(value: str | None) -> str | None:
    if value is None:
        return None
    upper = value.upper()
    if upper not in US_STATE_CODES:
        raise ValueError(f"'{value}' is not a valid US state abbreviation")
    return upper


class PatientBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=50, pattern=NAME_PATTERN)
    last_name: str = Field(min_length=1, max_length=50, pattern=NAME_PATTERN)
    date_of_birth: date
    sex: Sex
    phone_number: str
    email: EmailStr | None = None
    address_line_1: str = Field(min_length=1, max_length=200)
    address_line_2: str | None = Field(default=None, max_length=200)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=2, max_length=2)
    zip_code: str = Field(pattern=ZIP_PATTERN)
    insurance_provider: str | None = Field(default=None, max_length=100)
    insurance_member_id: str | None = Field(default=None, max_length=50)
    preferred_language: str = Field(default="English", max_length=50)
    emergency_contact_name: str | None = Field(default=None, max_length=100)
    emergency_contact_phone: str | None = None

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: date) -> date:
        return _reject_future_dob(value)

    @field_validator("state")
    @classmethod
    def validate_state(cls, value: str) -> str:
        return _normalize_state(value)

    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        return _normalize_phone(value)


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=50, pattern=NAME_PATTERN)
    last_name: str | None = Field(default=None, min_length=1, max_length=50, pattern=NAME_PATTERN)
    date_of_birth: date | None = None
    sex: Sex | None = None
    phone_number: str | None = None
    email: EmailStr | None = None
    address_line_1: str | None = Field(default=None, min_length=1, max_length=200)
    address_line_2: str | None = Field(default=None, max_length=200)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    state: str | None = Field(default=None, min_length=2, max_length=2)
    zip_code: str | None = Field(default=None, pattern=ZIP_PATTERN)
    insurance_provider: str | None = Field(default=None, max_length=100)
    insurance_member_id: str | None = Field(default=None, max_length=50)
    preferred_language: str | None = Field(default=None, max_length=50)
    emergency_contact_name: str | None = Field(default=None, max_length=100)
    emergency_contact_phone: str | None = None

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: date | None) -> date | None:
        return _reject_future_dob(value)

    @field_validator("state")
    @classmethod
    def validate_state(cls, value: str | None) -> str | None:
        return _normalize_state(value)

    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        return _normalize_phone(value)


class PatientRead(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    patient_id: str
    created_at: datetime
    updated_at: datetime
