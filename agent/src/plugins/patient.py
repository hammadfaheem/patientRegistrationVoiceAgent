"""Client for the patients REST API — the transport layer the tools call into."""

from typing import Any

from utils.api import ApiResponse, make_api_request
from utils.config import config

PATIENTS_URL = f"{config.api_base_url}/patients"


class PatientApiClient:
    """Thin HTTP client wrapping the patients REST API endpoints this agent needs."""

    async def lookup_by_phone(self, phone_number: str) -> ApiResponse[dict[str, Any]]:
        return await make_api_request(
            "GET", PATIENTS_URL, headers={}, params={"phone_number": phone_number}
        )

    async def create(self, payload: dict[str, Any]) -> ApiResponse[dict[str, Any]]:
        return await make_api_request("POST", PATIENTS_URL, headers={}, json=payload)

    async def update(self, patient_id: str, payload: dict[str, Any]) -> ApiResponse[dict[str, Any]]:
        return await make_api_request(
            "PUT", f"{PATIENTS_URL}/{patient_id}", headers={}, json=payload
        )


patient_api_client = PatientApiClient()
