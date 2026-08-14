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
uv run python src/agent.py console   # talk to it in your terminal
uv run python src/agent.py dev       # connect to LiveKit for frontend/telephony testing
uv run python src/agent.py start     # production mode
```

## Testing

```bash
uv run pytest
```

Tests run against LiveKit Inference directly, so `LIVEKIT_API_KEY` /
`LIVEKIT_API_SECRET` must be set (in `.env.local` or the environment) even
though no LiveKit room connection is made.

## Architecture

- `src/agent.py` — `AgentServer` with a single `@server.rtc_session` entrypoint
  (`agent_name="patient-registration-agent"`, must match the dispatch rule
  configured for the inbound phone number). Voice pipeline uses LiveKit
  Inference (STT, LLM, TTS, turn detection) — no separate provider API keys.
- Patient-registration conversation logic (system prompt, tools calling the
  `api/` service) is not implemented yet — this is the scaffold only.

## Telephony setup (one-time, not app code)

1. `lk number search` / `lk number purchase` — get a LiveKit Phone Number.
2. Create a dispatch rule that dispatches to `agent_name="patient-registration-agent"`.
3. `lk number update --sip-dispatch-rule-id <id>` — attach the number to the rule.
