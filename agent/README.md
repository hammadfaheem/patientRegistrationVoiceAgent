# Patient Registration Voice Agent

LiveKit Agents (Python) voice AI agent that answers inbound phone calls and
registers patients via the REST API in `../api/`.

## Setup

```bash
cd agent
uv sync
cp .env.example .env.local
```

Fill in `.env.local` with your LiveKit Cloud project credentials:

| Variable              | Description                                      |
|-----------------------|---------------------------------------------------|
| `LIVEKIT_URL`         | Your LiveKit Cloud project's WebSocket URL         |
| `LIVEKIT_API_KEY`     | LiveKit Cloud API key                              |
| `LIVEKIT_API_SECRET`  | LiveKit Cloud API secret                           |
| `API_BASE_URL`        | Base URL of the `api/` service (defaults to local) |

## Running

```bash
uv run python src/main.py console   # talk to it in your terminal
uv run python src/main.py dev       # connect to LiveKit for frontend/telephony testing
uv run python src/main.py start     # production mode
```

## Testing

```bash
uv run pytest
```

Tests run against LiveKit Inference directly, so `LIVEKIT_API_KEY` /
`LIVEKIT_API_SECRET` must be set (in `.env.local` or the environment) even
though no LiveKit room connection is made.

## Architecture

- `src/main.py` — entrypoint: `AgentServer` with a single `@server.rtc_session`
  entrypoint (`agent_name="patient-registration-agent"`, must match the
  dispatch rule configured for the inbound phone number). Voice pipeline uses
  LiveKit Inference (STT, LLM, TTS, turn detection) — no separate provider API
  keys. Run this file, not `agent.py`, to start the server.
- `src/agent.py` — defines `PatientRegistrationAgent`, composing the system
  prompt and tools.
- `src/prompts/patient.py` — the system prompt.
- `src/tools/patient.py` — the `@function_tool()`s the LLM can call
  (`lookup_patient_by_phone`, `create_patient`, `update_patient`). Tools own
  the domain logic (phone-number normalization, payload shaping, `ToolError`
  messages) and call into the API client rather than making HTTP requests
  themselves.
- `src/plugins/patient.py` — `PatientApiClient`, the HTTP client for the
  `api/` service's `/patients` endpoints. This is the only place that knows
  the API's URLs and HTTP verbs.
- `src/utils/` — cross-cutting helpers: env loading, app config, shared
  logger, and the generic `make_api_request` HTTP helper that
  `PatientApiClient` is built on. Phone number normalization lives in the
  `api/` service, since it owns the stored/matched format.

> Note: LiveKit's own tooling (Dockerfiles, deploy docs) defaults to
> assuming `src/agent.py` is the entrypoint. Since this project runs
> `src/main.py` instead, update any Dockerfile/deploy config accordingly
> when you add one.

## Telephony setup (one-time, not app code)

1. `lk number search` / `lk number purchase` — get a LiveKit Phone Number.
2. Create a dispatch rule that dispatches to `agent_name="patient-registration-agent"`.
3. `lk number update --sip-dispatch-rule-id <id>` — attach the number to the rule.
