"""API response utilities."""

from typing import Any, TypedDict, TypeVar

import httpx

from .logging import logger

T = TypeVar("T")


class ApiResponse[T](TypedDict):
    """Standardized API response."""

    success: bool
    data: T | None
    error: str | None


def create_api_response[T](data: T | None = None, error: str | None = None) -> ApiResponse[T]:
    """Create a standardized API response."""
    return {"success": error is None, "data": data, "error": error}


async def make_api_request(
    method: str,
    url: str,
    headers: dict[str, str],
    json: dict[str, Any] | None = None,
    params: dict[str, str] | None = None,
) -> ApiResponse[dict[str, Any]]:
    """Make an API request.

    Args:
        method: HTTP method (GET, POST, or PUT)
        url: API endpoint URL
        headers: Request headers
        json: Optional JSON payload for POST/PUT requests
        params: Optional query parameters

    Returns:
        ApiResponse containing parsed JSON response data or error

    """
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            logger.debug(f"Making {method} request to {url}")
            logger.debug(f"Payload: {json}")

            if method == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=json, params=params)
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=json, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            logger.debug(f"Request Response: {response}")

            if response.is_success:
                return create_api_response(data=response.json())
            else:
                try:
                    error_detail = response.json()
                    logger.debug(f"Error response JSON: {error_detail}")

                    error_msg = (
                        error_detail.get("message")
                        or error_detail.get("Message")
                        or error_detail.get("error")
                        or error_detail.get("Error")
                        or str(error_detail)
                    )
                except Exception:
                    error_msg = response.text or f"HTTP {response.status_code}"

                logger.error(f"API returned error: {error_msg} (status {response.status_code})")
                return create_api_response(error=error_msg)

    except Exception as e:
        logger.exception("Unexpected exception during API request")
        error_msg = str(e).strip() or "Unknown error occurred during API request"
        return create_api_response(error=error_msg)
