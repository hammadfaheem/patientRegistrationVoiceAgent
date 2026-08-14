"""The patient registration Agent: prompt + tools, wired together."""

from livekit.agents import Agent

from prompts.patient import PATIENT_REGISTRATION_INSTRUCTIONS
from tools.patient import create_patient, lookup_patient_by_phone, update_patient


class PatientRegistrationAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=PATIENT_REGISTRATION_INSTRUCTIONS,
            tools=[lookup_patient_by_phone, create_patient, update_patient],
        )
