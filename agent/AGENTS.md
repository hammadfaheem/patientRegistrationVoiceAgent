# AGENTS.md

## Purpose

This document defines how the coding assistant should build and maintain **LiveKit AI Agents** in this project.

The LiveKit documentation already available in the project should be used for LiveKit-specific APIs, configuration, and implementation details. This document focuses on the **agent design principles** that must be followed when creating or modifying an agent.

---

## 1. Agent Architecture

An AI agent should be thought of as having three major parts:

1. **System Prompt** — defines the agent's behavior and instructions.
2. **Tools** — provide the agent with external functionality and the ability to interact with APIs/services.
3. **Models & Runtime Configuration** — defines the LLM, STT, TTS, RLM/reasoning models, and other runtime components used by the agent.

The **system prompt and tools are especially important** because they strongly influence how reliably and accurately the agent behaves.

---

## 2. System Prompt

The system prompt is the primary place where the agent's behavior is defined.

When creating a system prompt:

* Clearly define the agent's role and responsibilities.
* Define how the agent should communicate with users.
* Define what the agent should and should not do.
* Define important business rules and constraints.
* Define how the agent should behave in different situations.
* Define when the agent should use a tool.
* Define what information the agent should collect before calling a tool.
* Keep instructions explicit and unambiguous.
* Avoid unnecessary instructions that can conflict with the agent's actual behavior.

The system prompt should describe **behavior and decision-making**, while tools should handle actual external functionality.

For example:

```text
You are a customer support voice agent.

Your responsibilities are:
- Help customers understand their account.
- Retrieve account information when necessary.
- Never invent account information.
- Ask for missing information before calling a tool.
- Use the appropriate tool whenever account data is required.

When a tool returns an error:
- Do not expose internal implementation details.
- Explain the issue clearly to the customer.
- Retry only when it is safe and appropriate.
```

Do not put API implementation details into the prompt when they belong in a tool.

---

## 3. Tools

Tools are the agent's interface to the outside world.

Use tools for:

* External API calls
* Database operations
* Fetching information
* Creating or updating records
* Sending messages
* Scheduling operations
* Performing business actions
* Any functionality that requires deterministic external execution

A tool should have a **clear responsibility**.

Prefer small, focused tools over one large tool that performs many unrelated operations.

### Tool Design

Each tool should:

* Have a clear and descriptive name.
* Have a clear description explaining when and why it should be used.
* Accept strongly typed parameters.
* Validate its inputs.
* Return useful, structured results.
* Handle errors appropriately.
* Avoid exposing unnecessary implementation details to the LLM.

Example:

```python
from datetime import date, time

async def book_appointment(
    appointment_date: date,
    appointment_time: time,
    customer_email: str,
):
    ...
```

The tool description should explain the meaning and constraints of each parameter so the model can make the correct tool call.

---

## 4. Use Strong Python Types for Tool Parameters

**Do not default to primitive `str` types when a more specific Python type already exists.**

Use the most appropriate type available.

For example, instead of:

```python
async def book_appointment(
    appointment_date: str,
    appointment_time: str,
):
    ...
```

prefer:

```python
from datetime import date, time

async def book_appointment(
    appointment_date: date,
    appointment_time: time,
):
    ...
```

This gives the model and the surrounding tooling more semantic information about what the parameter actually represents.

### Examples

Use:

```python
from datetime import date, datetime, time
```

for:

```python
date
datetime
time
```

Use appropriate typed models when an object contains multiple related fields:

```python
from pydantic import BaseModel

class Customer(BaseModel):
    name: str
    email: str
    phone: str
```

Prefer structured and semantically meaningful types whenever possible.

---

## 5. Annotated Types

Use existing Python/Pydantic typing capabilities to make tool parameters as precise as possible.

For example:

```python
from typing import Annotated

from pydantic import Field

customer_email: Annotated[
    str,
    Field(description="The customer's email address")
]
```

Similarly, constraints can be expressed through types and annotations where appropriate.

The goal is to give the agent framework and the LLM **better schema information**.

Better schemas generally lead to better tool-call results.

### Principle

> **Give the model the most accurate type/schema information available instead of representing everything as `str`.**

If a parameter has a known semantic type, use that type.

---

## 6. Email and Other Specialized Types

When a specialized type is available through the project's typing/validation stack, prefer it over a generic string.

For example, for email addresses, use the project's supported email type rather than treating an email as an arbitrary string.

```python
from pydantic import EmailStr

async def send_email(
    recipient: EmailStr,
    subject: str,
):
    ...
```

This makes the expected input explicit and provides stronger validation/schema information.

Apply the same principle to other structured values whenever an appropriate type exists.

---

## 7. Models and Runtime Components

The agent may use multiple models/components, for example:

```text
User Voice
    ↓
STT
    ↓
LLM / RLM
    ↓
Tool Calls
    ↓
External Services
    ↓
LLM / RLM
    ↓
TTS
    ↓
User Voice
```

When configuring these components:

* Use the models appropriate for the project's requirements.
* Keep model configuration separate from business logic.
* Do not hard-code credentials.
* Use environment variables/configuration for secrets.
* Follow the existing project architecture.
* Refer to the project's LiveKit documentation for the correct APIs and lifecycle patterns.

The coding assistant should not introduce a new model/provider unnecessarily when an existing project abstraction already supports the required functionality.

---

## 8. General Rules for the Coding Assistant

When creating or modifying a LiveKit agent:

1. **Understand the system prompt first.**
2. **Identify the tools the agent needs.**
3. **Design tools with clear responsibilities.**
4. **Use strong, semantic Python types for tool parameters.**
5. **Prefer `date`, `time`, `datetime`, Pydantic models, `EmailStr`, `Annotated`, and other appropriate types over generic strings when applicable.**
6. **Provide useful descriptions and constraints for tool parameters.**
7. **Keep agent behavior in the system prompt.**
8. **Keep external functionality in tools.**
9. **Keep model/runtime configuration separate from business logic.**
10. **Follow the existing LiveKit project structure and documentation.**
11. **Do not invent LiveKit APIs when the project's documentation or existing implementation provides the correct pattern.**
12. **Prefer simple, explicit, strongly typed implementations over clever abstractions.**

---

## Core Principle

The quality of a LiveKit agent depends heavily on the quality of its **instructions and tool definitions**.

A good agent should therefore have:

```text
Clear System Prompt
        +
Well-designed Tools
        +
Strongly Typed Tool Schemas
        +
Correct Models / Runtime Configuration
        =
Reliable AI Agent
```

When in doubt, make the agent's behavior explicit in the system prompt and make the tool's inputs as strongly typed and semantically precise as possible.
