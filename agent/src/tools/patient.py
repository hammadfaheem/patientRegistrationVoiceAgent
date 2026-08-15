"""Function tools that connect the voice agent to the patients REST API."""

from datetime import date
from typing import Annotated

from livekit.agents import RunContext, function_tool
from livekit.agents.llm import ToolError
from pydantic import EmailStr, Field

from plugins.patient import patient_api_client
from utils.helpers import digits_only
from utils.logging import logger
from utils.types import Sex


def _validation_error_message(error: object) -> str:
    """Turn a FastAPI validation error list into a per-field message the agent can act on."""
    if not isinstance(error, list):
        return str(error)
    parts = []
    for err in error:
        loc = err.get("loc") or []
        field = str(loc[-1]).replace("_", " ") if loc and loc[-1] != "body" else "a field"
        msg = str(err.get("msg", "is invalid")).removeprefix("Value error, ")
        parts.append(f"{field}: {msg}")
    return "; ".join(parts) or str(error)


@function_tool()
async def lookup_patient_by_phone(
    context: RunContext,
    phone_number: Annotated[str, Field(description="The caller's phone number, in E.164 format.")],
) -> dict:
    """Look up an existing patient record by phone number.

    Call this as soon as the caller provides their phone number, before
    collecting any other information, to check whether they already have a
    record. Returns found=False if no matching patient exists.
    """
    response = await patient_api_client.lookup_by_phone(digits_only(phone_number))
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
    first_name: Annotated[str, Field(description="The patient's first name.")],
    last_name: Annotated[str, Field(description="The patient's last name.")],
    date_of_birth: Annotated[
        date, Field(description="The patient's date of birth. Must not be in the future.")
    ],
    sex: Annotated[
        Sex, Field(description="The patient's sex: Male, Female, Other, or Decline to Answer.")
    ],
    phone_number: Annotated[str, Field(description="The patient's phone number, in any format.")],
    address_line_1: Annotated[str, Field(description="The patient's street address.")],
    city: Annotated[str, Field(description="The city of the patient's address.")],
    state: Annotated[
        str, Field(description="The patient's US state, as a 2-letter abbreviation (e.g. IL).")
    ],
    zip_code: Annotated[
        str, Field(description="The patient's 5-digit ZIP code, or ZIP+4 (e.g. 62704-1234).")
    ],
    email: Annotated[
        EmailStr | None, Field(description="The patient's email address, if provided.")
    ] = None,
    address_line_2: Annotated[
        str | None, Field(description="Apartment, suite, or unit number, if applicable.")
    ] = None,
    insurance_provider: Annotated[
        str | None,
        Field(description="The patient's insurance provider name, if they opted to give it."),
    ] = None,
    insurance_member_id: Annotated[
        str | None,
        Field(
            description="The patient's insurance member/subscriber ID, if they opted to give it."
        ),
    ] = None,
    preferred_language: Annotated[
        str | None,
        Field(
            description="The patient's preferred language, if they opted to give it. "
            "Defaults to English."
        ),
    ] = None,
    emergency_contact_name: Annotated[
        str | None,
        Field(description="Full name of the patient's emergency contact, if provided."),
    ] = None,
    emergency_contact_phone: Annotated[
        str | None,
        Field(description="Phone number of the patient's emergency contact, if provided."),
    ] = None,
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

    response = await patient_api_client.create(payload)
    if response["error"] is not None:
        logger.error("create_patient failed: %s", response["error"])
        raise ToolError(
            "I wasn't able to save that registration because of a problem with: "
            f"{_validation_error_message(response['error'])}. Ask the caller to correct "
            "only that, then try saving again."
        )

    return (response["data"] or {}).get("data")


@function_tool()
async def update_patient(
    context: RunContext,
    patient_id: Annotated[
        str,
        Field(description="The existing patient's ID, from a prior lookup_patient_by_phone call."),
    ],
    first_name: Annotated[
        str | None, Field(description="The patient's first name, if it changed.")
    ] = None,
    last_name: Annotated[
        str | None, Field(description="The patient's last name, if it changed.")
    ] = None,
    date_of_birth: Annotated[
        date | None,
        Field(description="The patient's date of birth, if it changed. Must not be in the future."),
    ] = None,
    sex: Annotated[
        Sex | None,
        Field(
            description="The patient's sex, if it changed: Male, Female, Other, or Decline to Answer."
        ),
    ] = None,
    phone_number: Annotated[
        str | None, Field(description="The patient's phone number, if it changed, in any format.")
    ] = None,
    email: Annotated[
        EmailStr | None, Field(description="The patient's email address, if it changed.")
    ] = None,
    address_line_1: Annotated[
        str | None, Field(description="The patient's street address, if it changed.")
    ] = None,
    address_line_2: Annotated[
        str | None, Field(description="Apartment, suite, or unit number, if it changed.")
    ] = None,
    city: Annotated[
        str | None, Field(description="The city of the patient's address, if it changed.")
    ] = None,
    state: Annotated[
        str | None,
        Field(
            description="The patient's US state, if it changed, as a 2-letter abbreviation (e.g. IL)."
        ),
    ] = None,
    zip_code: Annotated[
        str | None,
        Field(description="The patient's ZIP code, if it changed (5-digit or ZIP+4)."),
    ] = None,
    insurance_provider: Annotated[
        str | None, Field(description="The patient's insurance provider name, if it changed.")
    ] = None,
    insurance_member_id: Annotated[
        str | None,
        Field(description="The patient's insurance member/subscriber ID, if it changed."),
    ] = None,
    preferred_language: Annotated[
        str | None, Field(description="The patient's preferred language, if it changed.")
    ] = None,
    emergency_contact_name: Annotated[
        str | None,
        Field(description="Full name of the patient's emergency contact, if it changed."),
    ] = None,
    emergency_contact_phone: Annotated[
        str | None,
        Field(description="Phone number of the patient's emergency contact, if it changed."),
    ] = None,
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

    response = await patient_api_client.update(patient_id, payload)
    if response["error"] is not None:
        logger.error("update_patient failed: %s", response["error"])
        raise ToolError(
            "I wasn't able to update that record because of a problem with: "
            f"{_validation_error_message(response['error'])}. Ask the caller to correct "
            "only that, then try saving again."
        )

    return (response["data"] or {}).get("data")
