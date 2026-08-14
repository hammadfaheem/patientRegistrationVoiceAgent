"""Function tools that connect the voice agent to the patients REST API."""

from datetime import date
from typing import Annotated

from livekit.agents import RunContext, function_tool
from livekit.agents.llm import ToolError
from pydantic import EmailStr, Field

from utils.api import make_api_request
from utils.config import config
from utils.helpers import digits_only
from utils.logging import logger
from utils.types import Sex

PATIENTS_URL = f"{config.api_base_url}/patients"


@function_tool()
async def lookup_patient_by_phone(
    context: RunContext,
    phone_number: Annotated[str, Field(description="The caller's phone number, in any format.")],
) -> dict:
    """Look up an existing patient record by phone number.

    Call this as soon as the caller provides their phone number, before
    collecting any other information, to check whether they already have a
    record. Returns found=False if no matching patient exists.
    """
    response = await make_api_request(
        "GET", PATIENTS_URL, headers={}, params={"phone_number": digits_only(phone_number)}
    )
    if response["error"] is not None:
        logger.error("lookup_patient_by_phone failed: %s", response["error"])
        raise ToolError(
            "I couldn't check our records right now. Let's continue and I'll try again shortly."
        )

    patients = (response["data"] or {}).get("data") or []
    return {"found": bool(patients), "patient": patients[0] if patients else None}


@function_tool()
async def create_patient(
    context: RunContext,
    first_name: str,
    last_name: str,
    date_of_birth: date,
    sex: Sex,
    phone_number: str,
    address_line_1: str,
    city: str,
    state: str,
    zip_code: str,
    email: EmailStr | None = None,
    address_line_2: str | None = None,
    insurance_provider: str | None = None,
    insurance_member_id: str | None = None,
    preferred_language: str | None = None,
    emergency_contact_name: str | None = None,
    emergency_contact_phone: str | None = None,
) -> dict:
    """Create a new patient record.

    Only call this after the caller has explicitly confirmed every field is
    correct, and only for a caller who does NOT already have an existing
    record — use update_patient for a returning caller instead.
    """
    context.disallow_interruptions()

    fields = {
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": date_of_birth.isoformat(),
        "sex": sex,
        "phone_number": digits_only(phone_number),
        "address_line_1": address_line_1,
        "address_line_2": address_line_2,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "email": email,
        "insurance_provider": insurance_provider,
        "insurance_member_id": insurance_member_id,
        "preferred_language": preferred_language,
        "emergency_contact_name": emergency_contact_name,
        "emergency_contact_phone": (
            digits_only(emergency_contact_phone) if emergency_contact_phone else None
        ),
    }
    # Omit unset optional fields entirely rather than sending explicit nulls —
    # the API's preferred_language is a plain `str` with a default, so a JSON
    # null (as opposed to an absent key) fails its validation.
    payload = {k: v for k, v in fields.items() if v is not None}

    response = await make_api_request("POST", PATIENTS_URL, headers={}, json=payload)
    if response["error"] is not None:
        logger.error("create_patient failed: %s", response["error"])
        raise ToolError(
            "I wasn't able to save that registration. Some information may not have "
            "passed validation — please review the details with the caller and try again."
        )

    return (response["data"] or {}).get("data")


@function_tool()
async def update_patient(
    context: RunContext,
    patient_id: Annotated[
        str,
        Field(description="The existing patient's ID, from a prior lookup_patient_by_phone call."),
    ],
    first_name: str | None = None,
    last_name: str | None = None,
    date_of_birth: date | None = None,
    sex: Sex | None = None,
    phone_number: str | None = None,
    email: EmailStr | None = None,
    address_line_1: str | None = None,
    address_line_2: str | None = None,
    city: str | None = None,
    state: str | None = None,
    zip_code: str | None = None,
    insurance_provider: str | None = None,
    insurance_member_id: str | None = None,
    preferred_language: str | None = None,
    emergency_contact_name: str | None = None,
    emergency_contact_phone: str | None = None,
) -> dict:
    """Update an existing patient's record.

    Only pass the fields the caller confirmed have changed. Only call this
    after the caller has confirmed the changes.
    """
    context.disallow_interruptions()

    fields = {
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": date_of_birth.isoformat() if date_of_birth else None,
        "sex": sex,
        "phone_number": digits_only(phone_number) if phone_number else None,
        "email": email,
        "address_line_1": address_line_1,
        "address_line_2": address_line_2,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "insurance_provider": insurance_provider,
        "insurance_member_id": insurance_member_id,
        "preferred_language": preferred_language,
        "emergency_contact_name": emergency_contact_name,
        "emergency_contact_phone": (
            digits_only(emergency_contact_phone) if emergency_contact_phone else None
        ),
    }
    payload = {k: v for k, v in fields.items() if v is not None}

    response = await make_api_request(
        "PUT", f"{PATIENTS_URL}/{patient_id}", headers={}, json=payload
    )
    if response["error"] is not None:
        logger.error("update_patient failed: %s", response["error"])
        raise ToolError(
            "I wasn't able to update that record. Some information may not have passed "
            "validation — please review the details with the caller and try again."
        )

    return (response["data"] or {}).get("data")
