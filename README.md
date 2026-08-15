# Patient Registration Voice AI Agent

A caller dials a real US phone number, registers as a patient through a
natural voice conversation, and the record is persisted and queryable through
a REST API. Calling back with the same phone number is recognized as a
returning patient, offering to update the existing record instead of creating
a duplicate.

**Live demo**

| | |
|---|---|
| Phone number | `+1 (484) 518-2089` |
| API base URL | `https://patient-registration-production-f139.up.railway.app` |
| API docs | `https://patient-registration-production-f139.up.railway.app/docs` |

No credentials are required to call the number or hit the API — see
[Known limitations](#known-limitations).

## Architecture

```text
Caller
  ↕ PSTN
LiveKit Phone Number (SIP)
  ↕
Voice AI Agent  ──────────────►  Patients REST API  ──────────────►  PostgreSQL
(agent/, LiveKit Agents,            (api/, FastAPI)                  (Railway)
 LiveKit Inference for
 STT/LLM/TTS/turn detection)
```

Two independently deployable services, each with its own README:

- **[`agent/`](agent/README.md)** — the voice AI agent. Answers the call,
  runs the conversation (prompt in
  [`src/prompts/patient.py`](agent/src/prompts/patient.py)), and calls the
  `api/` service through a small typed client — it never touches the
  database directly.
- **[`api/`](api/README.md)** — the REST API and the only thing that owns
  the patient schema and persistence.

This split mirrors spec §8.3 ("clear separation of concerns... between
telephony, LLM logic, data layer, and API"): the agent can be redeployed,
re-prompted, or swapped for a different voice platform without touching the
data layer, and the API can be tested and validated independently of any
phone call.

### Call flow

1. LiveKit's SIP service answers the call and dispatches it, via a [SIP
   dispatch rule](agent/README.md#telephony-setup-one-time-not-app-code), to
   the agent worker (`agent_name="patient-registration-agent"`).
2. The agent greets the caller and, as soon as it has a phone number, calls
   `GET /patients?phone_number=...` to check for an existing record (the
   duplicate-detection bonus in spec §6/§9).
3. It collects the required fields conversationally, re-prompting on
   invalid input (spec §3.1), and offers the optional fields (insurance,
   emergency contact, preferred language) once.
4. It reads everything back and waits for explicit confirmation.
5. On confirmation, it calls `POST /patients` (new caller) or
   `PUT /patients/{id}` (returning caller).
6. Success or failure is reported back to the caller in plain language —
   never silently.

## Setup

Each service has its own environment and dependencies (both use `uv`):

```bash
# API
cd api
uv sync
cp .env.example .env
uv run uvicorn src.main:app --reload --port 8000

# Agent (in a second terminal)
cd agent
uv sync
cp .env.example .env.local   # fill in LiveKit Cloud credentials
uv run python src/main.py console   # talk to it in the terminal, no telephony needed
```

Full instructions, including one-time telephony setup (LiveKit phone number
+ SIP dispatch rule) and running/testing each service, are in
[`agent/README.md`](agent/README.md) and [`api/README.md`](api/README.md).

## Environment variables

**`api/`**

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./patients.db` | Async SQLAlchemy connection string. Production (Railway) uses Postgres; a `postgres(ql)://` URL is automatically rewritten to the `asyncpg` driver — see [`src/config.py`](api/src/config.py). |
| `LOG_LEVEL` | `INFO` | Python `logging` level |

**`agent/`**

| Variable | Description |
|---|---|
| `LIVEKIT_URL` | LiveKit Cloud project WebSocket URL |
| `LIVEKIT_API_KEY` / `LIVEKIT_API_SECRET` | LiveKit Cloud API credentials |
| `API_BASE_URL` | Base URL of the `api/` service (the deployed Railway URL in production) |

## Technology stack & justification

| Layer | Choice | Why |
|---|---|---|
| Telephony + voice pipeline | LiveKit Cloud (LiveKit Phone Numbers + LiveKit Agents) | One platform for SIP telephony, STT/LLM/TTS/turn-detection (via LiveKit Inference), and hosting — avoids stitching together a separate telephony provider, speech vendor, and hosting story under a time limit. |
| LLM | `google/gemma-4-31b-it` via LiveKit Inference | Fast, no separate API key/billing relationship to manage — Inference is billed through the same LiveKit Cloud account. |
| Backend API | Python + FastAPI | Async-native, automatic request validation (Pydantic) and OpenAPI docs satisfy spec §5's "validate all inputs server-side" with very little code. |
| Database | SQLite (dev) / PostgreSQL (prod, Railway addon) | SQLite is zero-setup for local development; Railway's container filesystem is ephemeral, so production uses a real Postgres addon instead — see [Known limitations](#known-limitations). |
| Agent hosting | LiveKit Cloud (`lk agent create`) | Keeps the always-on worker off a personal machine, matching spec §7's "must be running and callable at the time of review." |
| API hosting | Railway | Fast to stand up from a Dockerfile, free Postgres addon, matches spec §10's suggested hosting list. |

## Known limitations

- **No authentication** on the API or the phone number — explicitly out of
  scope per spec §13 ("do not store real patient data"; this is a technical
  assessment, not a production system).
- **`phone_number` is not unique-constrained** at the database level;
  duplicate-caller detection is done by the agent calling
  `GET /patients?phone_number=...` before registering, not enforced as a DB
  constraint.
- **Dashboard bonus (spec §9) not built** — there's no patient-facing web
  UI, only the voice agent and the REST API (browsable via the `/docs`
  Swagger UI at the API base URL).
- **No call recording/transcript persistence** (bonus, not implemented) —
  the final collected payload is logged at `INFO` level per spec §7's
  observability requirement, but full transcripts aren't stored.
- **No multi-language support** — the agent speaks English only.
- Full trade-off list, including the SQLite→Postgres reasoning and error
  logging rationale, is in [`api/README.md`](api/README.md#known-limitations--trade-offs).

## Next steps

Given more time, in priority order: a lightweight patient dashboard (bonus
§9), a unique constraint + proper conflict response for duplicate phone
numbers instead of agent-side detection only, call transcript storage linked
to `patient_id`, and Spanish-language support (the prompt and turn detector
already support a `language="multi"` STT model, but the system prompt itself
is English-only).
