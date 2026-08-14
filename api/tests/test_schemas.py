from src.exceptions import AppError, NotFoundError
from src.schemas import Envelope


def test_envelope_defaults_to_no_error():
    env = Envelope[str](data="hi")
    assert env.data == "hi"
    assert env.error is None


def test_envelope_serializes_error_shape():
    env = Envelope[None](data=None, error="boom")
    assert env.model_dump() == {"data": None, "error": "boom"}


def test_not_found_error_has_404_status():
    exc = NotFoundError("patient abc not found")
    assert isinstance(exc, AppError)
    assert exc.status_code == 404
    assert exc.message == "patient abc not found"
