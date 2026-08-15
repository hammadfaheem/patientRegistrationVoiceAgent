import pytest
from livekit.agents import AgentSession, inference, mock_tools

from agent import PatientRegistrationAgent


def _mock_lookup_no_match(phone_number: str) -> dict:
    return {"found": False, "patient": None}


def _mock_lookup_found_match(phone_number: str) -> dict:
    return {
        "found": True,
        "patient": {
            "patient_id": "11111111-1111-1111-1111-111111111111",
            "first_name": "Jane",
            "last_name": "Doe",
        },
    }


def _mock_lookup_failure() -> RuntimeError:
    return RuntimeError("Patient records service unavailable")


@pytest.mark.asyncio
async def test_assistant_greeting() -> None:
    async with (
        inference.LLM(model="google/gemma-4-31b-it") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(PatientRegistrationAgent())

        result = await session.run(user_input="Hello")

        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .judge(
                llm,
                intent=(
                    "Introduces itself as a patient registration assistant and "
                    "offers to help register the caller."
                ),
            )
        )

        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_agent_looks_up_phone_number_and_continues_when_no_match() -> None:
    async with (
        inference.LLM(model="google/gemma-4-31b-it") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(PatientRegistrationAgent())

        with mock_tools(
            PatientRegistrationAgent, {"lookup_patient_by_phone": _mock_lookup_no_match}
        ):
            result = await session.run(user_input="Hi, my phone number is 555-123-4567.")

            result.expect.next_event().is_function_call(name="lookup_patient_by_phone")
            result.expect.next_event().is_function_call_output()

            await (
                result.expect.next_event()
                .is_message(role="assistant")
                .judge(
                    llm,
                    intent=(
                        "Continues the registration conversation, such as asking for "
                        "more information, without claiming an existing record was found."
                    ),
                )
            )


@pytest.mark.asyncio
async def test_agent_offers_update_when_existing_patient_found() -> None:
    async with (
        inference.LLM(model="google/gemma-4-31b-it") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(PatientRegistrationAgent())

        with mock_tools(
            PatientRegistrationAgent, {"lookup_patient_by_phone": _mock_lookup_found_match}
        ):
            result = await session.run(user_input="Hi, my phone number is 555-123-4567.")

            result.expect.next_event().is_function_call(name="lookup_patient_by_phone")
            result.expect.next_event().is_function_call_output()

            await (
                result.expect.next_event()
                .is_message(role="assistant")
                .judge(
                    llm,
                    intent=(
                        "Tells the caller a record already exists for Jane Doe and asks "
                        "whether they'd like to update their information instead of "
                        "registering as a new patient."
                    ),
                )
            )


@pytest.mark.asyncio
async def test_agent_handles_lookup_failure_gracefully() -> None:
    async with (
        inference.LLM(model="google/gemma-4-31b-it") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(PatientRegistrationAgent())

        with mock_tools(
            PatientRegistrationAgent, {"lookup_patient_by_phone": _mock_lookup_failure}
        ):
            result = await session.run(user_input="Hi, my phone number is 555-123-4567.")

            result.expect.next_event().is_function_call(name="lookup_patient_by_phone")
            result.expect.next_event().is_function_call_output()

            await (
                result.expect.next_event()
                .is_message(role="assistant")
                .judge(
                    llm,
                    intent=(
                        "Continues the conversation gracefully despite an internal error, "
                        "without exposing technical details to the caller."
                    ),
                )
            )
