"""Entrypoint: initializes the AgentServer and starts a session per call."""

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import (
    AgentServer,
    AgentSession,
    TurnHandlingOptions,
    inference,
    room_io,
)
from livekit.plugins import ai_coustics

from agent import PatientRegistrationAgent

load_dotenv(".env.local")

server = AgentServer()


@server.rtc_session(agent_name="patient-registration-agent")
async def patient_registration_agent(ctx: agents.JobContext):
    session = AgentSession(
        stt=inference.STT(model="deepgram/nova-3", language="multi"),
        llm=inference.LLM(model="google/gemma-4-31b-it"),
        tts=inference.TTS(
            model="inworld/inworld-tts-2",
            voice="Ashley",
        ),
        turn_handling=TurnHandlingOptions(
            turn_detection=inference.TurnDetector(),
        ),
    )

    await session.start(
        room=ctx.room,
        agent=PatientRegistrationAgent(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=ai_coustics.audio_enhancement(
                    model=ai_coustics.EnhancerModel.QUAIL_VF_S
                ),
            ),
        ),
    )

    await session.generate_reply(
        instructions=(
            "Greet the caller warmly, introduce yourself as the practice's patient "
            "registration assistant, and ask how you can help."
        )
    )


if __name__ == "__main__":
    agents.cli.run_app(server)
