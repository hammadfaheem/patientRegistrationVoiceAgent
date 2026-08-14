import pytest
from livekit.agents import AgentSession, inference

from agent import Assistant


@pytest.mark.asyncio
async def test_assistant_greeting() -> None:
    async with (
        inference.LLM(model="google/gemma-4-31b-it") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(Assistant())

        result = await session.run(user_input="Hello")

        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .judge(llm, intent="Makes a friendly introduction and offers assistance.")
        )

        result.expect.no_more_events()
