# Patient Registration API

FastAPI REST service that stores patient demographic records collected by the
voice AI agent (see `../agent/`) and exposes them for querying.

## Setup

```bash
cd api
uv sync
cp .env.example .env
uv run uvicorn src.main:app --reload --port 8000
```

## Environment variables

| Variable       | Default                                | Description                          |
|----------------|-----------------------------------------|---------------------------------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./patients.db`     | Async SQLAlchemy connection string    |
| `LOG_LEVEL`    | `INFO`                                  | Python `logging` level                |

## Architecture

- `src/main.py` — FastAPI app, lifespan-managed table creation, global exception handlers.
- `src/patients/` — the one bounded context in this service: `schemas.py` (Pydantic validation),
  `models.py` (SQLAlchemy ORM), `service.py` (CRUD + soft delete), `router.py` (HTTP layer),
  `dependencies.py` (shared `valid_patient_id` lookup).
- `src/database.py`, `src/config.py`, `src/schemas.py`, `src/exceptions.py` — cross-cutting
  concerns shared by every future domain, kept outside `patients/`.
- Every response is wrapped as `{"data": ..., "error": ...}` via `Envelope[T]`.

## Endpoints

| Method | Path              | Notes                                                            |
|--------|-------------------|-------------------------------------------------------------------|
| GET    | `/patients`       | Optional `last_name`, `date_of_birth` (ISO `YYYY-MM-DD`), `phone_number` filters |
| GET    | `/patients/{id}`  | 404 if missing or soft-deleted                                    |
| POST   | `/patients`       | 201 + created record; 422 on validation failure                   |
| PUT    | `/patients/{id}`  | Partial update — only send fields that changed                    |
| DELETE | `/patients/{id}`  | Soft delete (`deleted_at`), not a hard delete                     |

## Technology choices

- **uv** for dependency/venv management — single lockfile, fast installs, already the
  scaffold in this repo.
- **SQLite over Postgres**: single-table schema, no concurrent-writer concerns for a take-home
  demo — Postgres would add deployment overhead with no functional benefit here.
- **No Alembic**: the schema is fixed for this assessment; `Base.metadata.create_all` on
  startup is sufficient. Add Alembic the moment a second migration is needed.
- **No auth**: not in scope per the assessment spec.

## Known limitations / trade-offs

- Dates are ISO 8601 on the wire; the voice agent must convert spoken dates before calling this API.
- `phone_number` is not unique-constrained — duplicate-caller detection is done via
  `GET /patients?phone_number=...` and left to the calling agent to act on (the bonus
  "existing patient" flow), not enforced at the DB level.
- No rate limiting or auth — acceptable for a reviewer-facing demo, not for production.
- `service.create_patient` logs the full patient payload (name, DOB, phone, address) at
  INFO level, per spec §7's "log at minimum the final collected data payload" requirement.
  This is only acceptable because the assessment explicitly forbids using real patient data
  (spec §13). A production system would log identifiers only and route full-payload audit
  logging to an access-controlled sink.

## Testing

```bash
cd api
uv run pytest tests/ -v
```
