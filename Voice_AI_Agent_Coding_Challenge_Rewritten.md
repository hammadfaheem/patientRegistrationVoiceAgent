# Voice AI Agent — Patient Registration System

## Take-Home Technical Assessment

**Role:** Voice AI / Conversational AI Engineer  
**Time Limit:** 3 Hours (Maximum)  
**Difficulty:** Intermediate — Advanced  

> **CONFIDENTIAL — FOR CANDIDATE USE ONLY**

---

## 1. Overview

Build a voice-based AI agent accessible via a real phone number that collects standard U.S. patient demographic information through natural conversation, persists that data to a database, and exposes it through a lightweight web service.

When a caller dials the number, they should be able to speak naturally with the agent to register a new patient. If they call back, the data from the previous call must still be available.

This challenge evaluates the ability to integrate multiple systems — telephony, LLM, database, and API — into a cohesive, production-oriented solution under time pressure.

---

## 2. System Architecture

The expected high-level flow is:

```text
Caller
  ↕
Voice AI Agent
(LLM + Telephony)
  ↕
Persistent Database
  ↓
Web Service
(REST API)
```

The voice AI agent should:

1. Answer the incoming phone call.
2. Greet the caller.
3. Collect the required patient demographics conversationally.
4. Confirm all collected information with the caller.
5. Save the confirmed record to persistent storage.
6. Provide a completion message.
7. End the call gracefully.

The REST API should allow stored patient records to be queried and viewed.

---

# 3. Functional Requirements

## 3.1 Telephony & Voice Agent

### Phone Number

Provision a real, dialable U.S. phone number using a telephony provider such as:

- Twilio
- Vonage
- Vapi
- Retell
- Bland.ai

### Voice Interaction

The agent must conduct a natural, conversational flow.

It should **not** behave like a rigid IVR menu. The experience should feel similar to speaking with a human intake coordinator.

### LLM-Powered Conversation

Use any suitable LLM, including:

- OpenAI
- Anthropic
- Google
- Open-source models

The LLM must be able to:

- Understand varied phrasing.
- Ask clarifying questions.
- Handle corrections.
- Maintain the conversational context.

### Confirmation

Before saving the patient record, the agent must read the collected information back to the caller and ask them to confirm or correct any field.

### Error Handling

If invalid information is provided, the agent must specifically re-prompt for that field.

Examples:

- Invalid 3-digit phone number.
- Future date of birth.
- Invalid state abbreviation.
- Invalid ZIP code.

---

## 3.2 Patient Demographic Data Model

The agent must collect and store the following standard minimum demographic dataset.

| Field | Type | Validation Rules | Required |
|---|---|---|---|
| `first_name` | String | 1–50 chars, alphabetic + hyphens/apostrophes | Yes |
| `last_name` | String | 1–50 chars, alphabetic + hyphens/apostrophes | Yes |
| `date_of_birth` | Date | Valid date, not in future, MM/DD/YYYY | Yes |
| `sex` | Enum | Male, Female, Other, Decline to Answer | Yes |
| `phone_number` | String | Valid U.S. 10-digit phone number | Yes |
| `email` | String | Valid email format | No |
| `address_line_1` | String | Street address | Yes |
| `address_line_2` | String | Apt/Suite/Unit if applicable | No |
| `city` | String | 1–100 characters | Yes |
| `state` | String | Valid 2-letter U.S. state abbreviation | Yes |
| `zip_code` | String | 5-digit or ZIP+4 U.S. format | Yes |
| `insurance_provider` | String | Name of insurance company | No |
| `insurance_member_id` | String | Alphanumeric member/subscriber ID | No |
| `preferred_language` | String | Default: English | No |
| `emergency_contact_name` | String | Full name | No |
| `emergency_contact_phone` | String | Valid U.S. 10-digit phone number | No |
| `created_at` | Timestamp | Auto-generated at creation (UTC) | Auto |
| `updated_at` | Timestamp | Auto-generated on modification (UTC) | Auto |
| `patient_id` | UUID | Auto-generated unique identifier | Auto |

### Optional Fields

The agent does not need to ask for every optional field on every call.

After collecting the required fields, it should offer the caller the option to provide:

- Insurance information
- Emergency contact
- Preferred language

Example:

> "I can also collect your insurance information, emergency contact, and preferred language. Would you like to provide any of those?"

The caller should be allowed to opt in.

---

# 4. Persistent Database

## Requirements

Any relational or document database may be used, including:

- PostgreSQL
- SQLite
- MySQL
- MongoDB

### Persistence

Data must survive server restarts.

For example, if `"Jane Doe"` is registered during Call 1, the patient must still exist when queried during Call 2.

### Schema

The database schema must enforce the required data model using appropriate:

- Column/data types
- Constraints
- Validation rules

### Seed Data

Optionally include 1–2 seed patient records for demonstration purposes.

---

# 5. Web Service — REST API

Expose the following endpoints.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/patients` | List all patients. Supports optional `last_name`, `date_of_birth`, and `phone_number` query parameters. |
| `GET` | `/patients/:id` | Retrieve a single patient by `patient_id` UUID. |
| `POST` | `/patients` | Create a new patient and return the created record with `patient_id`. |
| `PUT` | `/patients/:id` | Update an existing patient record. Partial updates are allowed. |
| `DELETE` | `/patients/:id` | Soft-delete a patient by setting `deleted_at`; do not hard-delete. |

## API Standards

The API must:

- Return appropriate HTTP status codes:
  - `200`
  - `201`
  - `400`
  - `404`
  - `422`
  - `500`
- Validate all inputs server-side.
- Not rely solely on voice-agent validation.
- Return JSON responses using a consistent envelope:

```json
{
  "data": {},
  "error": null
}
```

---

# 6. Voice Agent ↔ Database Integration

The voice agent must persist patient records through the REST API or an equivalent shared service layer.

### Required Flow

After the caller confirms the collected information:

```text
Caller Confirmation
        ↓
POST /patients
        ↓
Database
        ↓
Success / Failure
        ↓
Voice Agent
        ↓
Caller
```

### Success

If the database write succeeds, the agent should provide a confirmation to the caller.

### Failure

If the database write fails, the agent should provide a graceful error message rather than remaining silent.

### Bonus: Existing Patient Detection

If the caller provides a phone number that matches an existing patient, the agent should recognize the existing record and ask whether the caller wants to update their information.

Example:

> "It looks like we already have a record for [First Name] [Last Name]. Would you like to update your information instead?"

---

# 7. Non-Functional Requirements

## Deployment

The system must be running and callable at the time of review.

The phone number must be live and the reviewers must be able to call it.

Possible hosting options include:

- Railway
- Render
- Fly.io
- Replit
- AWS
- GCP
- ngrok

## Code Quality

The code should be:

- Clean
- Readable
- Well organized
- Intentionally structured

Perfection is not expected within the three-hour time limit, but the architecture and organization should demonstrate deliberate engineering decisions.

## README

The project README must include:

- Setup instructions
- Architecture description
- Technology-stack justification
- Required environment variables
- Known limitations
- Trade-offs

## Security

- Do not hardcode API keys or credentials.
- Use environment variables.
- Apply basic input sanitization to the API.

## Observability

Log agent conversations, at minimum the final collected data payload, to:

- stdout, or
- a log file.

---

# 8. Evaluation Criteria

The submission is evaluated across five equally weighted dimensions.

## 8.1 Working System — 20%

Questions considered:

- Can the reviewer call the number and complete patient registration?
- Is the data persisted?
- Can the data be retrieved through the API?
- Does the system handle a second call without losing data?

## 8.2 Conversational Quality — 20%

The voice agent should:

- Sound natural rather than robotic or scripted.
- Handle corrections gracefully.
- Confirm information before saving.
- Handle interruptions.
- Handle out-of-order responses.

Example correction:

> "Actually, my last name is spelled D-A-V-I-S, not D-A-V-I-E-S."

## 8.3 Technical Architecture — 20%

The implementation should demonstrate:

- Clear separation of concerns.
- Separation between telephony, LLM logic, data layer, and API.
- A well-designed database schema.
- Appropriate data types and constraints.
- RESTful and properly validated API endpoints.
- Thoughtful and documented prompt engineering.

## 8.4 Code Quality & Documentation — 20%

The reviewers will consider:

- Whether another engineer could pick up the project.
- Code organization.
- Readability.
- Consistency.
- README completeness and accuracy.
- Documentation of trade-offs and limitations.
- Inclusion and documentation of the LLM system prompt.

## 8.5 Edge Cases & Resilience — 20%

The system should consider:

- Invalid dates of birth.
- Telephony connection drops.
- Database write failures.
- What the caller hears when a database write fails.
- A caller requesting to start over during a conversation.

---

# 9. Bonus Challenges

These are not required but demonstrate additional depth.

## Duplicate Detection

Recognize returning callers by phone number and offer to update their existing record instead of creating a duplicate.

## Appointment Scheduling

After registration, offer to schedule a first appointment.

Mock data is acceptable.

## Multi-language Support

If the caller says:

> "Hablo español"

the agent can switch to Spanish.

## Call Recording / Transcript

Store a transcript or summary of each call linked to the patient record.

## Dashboard

Build a simple web UI displaying registered patients.

## Automated Tests

Add unit or integration tests for the API layer.

---

# 10. Recommended Technology Stack

The following technologies are suggestions only. Candidates may use technologies they are comfortable with.

| Layer | Options |
|---|---|
| Telephony + Voice AI | Vapi, Retell AI, Bland.ai, Twilio + Deepgram/ElevenLabs, Vonage |
| LLM | OpenAI GPT-4o / GPT-4o-mini, Anthropic Claude, Google Gemini, Groq + Llama |
| Backend | Node.js (Express/Fastify), Python (FastAPI/Flask), Go, Ruby on Rails |
| Database | PostgreSQL, SQLite, MongoDB, Supabase |
| Hosting | Railway, Render, Fly.io, Replit, Vercel + serverless DB, ngrok |

### Recommended Approach

Platforms such as Vapi and Retell abstract much of the telephony, STT, and TTS complexity.

This allows the candidate to focus primarily on:

- LLM prompt engineering
- Tool definitions
- Backend integration
- Database persistence
- API design

This is considered the fastest path to a working implementation within the three-hour time constraint.

---

# 11. Submission Instructions

## Repository

Push the code to a public or private GitHub/GitLab repository.

If the repository is private, grant access to the reviewer emails provided separately.

## Live Demo

The following must be live and accessible during review:

- Phone number
- API endpoint

Both must be included in the README.

## Deadline

Submit within **3 hours** of receiving the challenge.

Partial submissions are accepted.

A working but incomplete system is preferable to a non-functional but ambitious system.

## Submission Details

Send:

1. Repository URL
2. Phone number to call
3. API base URL
4. Any credentials or notes required for testing

Example API base URL:

```text
https://your-app.railway.app
```

---

# 12. What the Assessment Is Really Looking For

This is not a trick question.

The goal is **not** to build a production healthcare system with HIPAA compliance and 99.99% uptime.

The assessment is designed to evaluate whether the engineer can:

### Integrate Multiple Systems

Integrate telephony, voice AI, LLMs, databases, and APIs under time pressure.

### Make Smart Trade-offs

Know when to choose a shortcut and when to invest engineering effort.

Examples:

- SQLite instead of PostgreSQL when appropriate.
- ngrok instead of a full cloud deployment.
- More effort on prompt engineering and error handling.

### Build End-to-End

The system should actually work as a complete flow rather than only demonstrating isolated components.

### Think About User Experience

The person on the phone is the end user.

A technically perfect system with a poor voice experience is still considered a failure.

### Communicate Clearly

Demonstrate architectural decisions through:

- Code
- Documentation
- README
- Architecture
- Trade-off explanations

> **A simple system that works flawlessly is preferred over an over-engineered system that crashes on the first call.**

---

# 13. FAQs

## Can I use a voice AI platform such as Vapi or Retell?

Yes.

The assessment explicitly allows these platforms. The goal is to assess integration and system-design skills rather than the ability to implement speech-to-text from scratch.

## Do I need HIPAA compliance?

No.

This is a technical assessment, not a production healthcare system.

**Do not store real patient data.**

## What if I cannot provision a phone number in time?

Document:

- What you tried.
- Why provisioning failed.
- The blocker you encountered.

Provide a working local setup with clear testing instructions.

Vendor issues will not result in a penalty, but the way the blocker is handled will be evaluated.

## Can I use AI coding assistants?

Yes.

Tools such as:

- GitHub Copilot
- Cursor
- Claude
- Other AI coding assistants

are allowed.

The important factors are:

- The quality of the final output.
- Your understanding of the implementation.
- Your ability to explain your decisions.

## What if I run out of time?

Submit what you have.

Document what you would have implemented next in the README under a **Next Steps** section.

Partial, working submissions are valued.

---

# 14. Key Principle

> **Build a simple, reliable, end-to-end voice registration system within the time limit.**

Prioritize:

1. Working phone call
2. Natural conversation
3. Correct data collection
4. Confirmation before persistence
5. Reliable database storage
6. Working REST API
7. Validation and error handling
8. Clean architecture
9. Clear README
10. Optional bonus features only after the core flow works

**Good luck.**
