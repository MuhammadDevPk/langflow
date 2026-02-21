# 🎙️ Voxhive Voice AI Dental Agent: A Production-Ready Conversational System

[![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen)]()
[![Voice Interface](https://img.shields.io/badge/voice-enabled-blue)]()
[![AI Powered](https://img.shields.io/badge/AI-Langflow%20%2B%20OpenAI-purple)]()
[![Twilio & Web](https://img.shields.io/badge/availability-Web%20%7C%20Phone-orange)]()

## 🌟 Executive Summary

The **Voxhive Voice AI Agent** is not just a chatbot—it is a full-stack, state-of-the-art conversational AI system engineered to completely automate the dental appointment scheduling process. By orchestrating ultra-low latency Speech-to-Text (STT), hyper-realistic Text-to-Speech (TTS), and an advanced Large Language Model (LLM), it handles natural, multi-turn conversations with patients and dynamically books appointments directly into Google Calendar.

### What Problems Does This Solve?

- **Front-Desk Bottlenecks**: Alleviates high call volumes by handling routine scheduling, rescheduling, and general inquiries 24/7.
- **Fragile AI Workflows**: Visual AI builders (like Langflow) often struggle with complex, multi-path conditional logic. This project solves that via an innovative **Unified Agent Architecture**—compressing a VAPI state machine into a single, dynamically generated Langflow system prompt, drastically improving reliability.
- **Siloed Systems**: Eliminates the disconnect between phone lines (Twilio), web widgets, and booking software (Google Calendar) by providing one centralized AI brain.

### Why Use It? (Core Benefits)

- **Zero-Friction Integrations**: Actually executes code. The agent can check live availability and write directly to Google Calendar using Service Accounts.
- **Bulletproof Uptime & Fallbacks**: Built-in failovers (e.g., automatically routing to Google TTS if ElevenLabs throttles) ensure the system never goes down during patient calls.
- **Exceptional Developer Experience (DX)**: Zero manual workflow wiring. A custom Python script automatically converts VAPI JSON flows into Langflow nodes, injects tool code, and configures the environment.

---

## 🧠 Engineering & Expertise Displayed

This repository serves as a showcase of advanced Agentic Engineering and Full-Stack capability:

1. **Advanced LLM Prompt Engineering**: Migrating rigid state-machine logic into a robust, context-aware system prompt (`unified_agent_builder.py`).
2. **Audio Data Pipelines**: Bridging Web Audio APIs in the browser with FastAPI websockets and external STT/TTS providers (Deepgram/ElevenLabs).
3. **Automated Tool Injection**: Creating custom Langflow `CustomComponent` definitions on the fly and wiring them into API requests mathematically, without human GUI interaction.
4. **Third-Party API Mastery**: Seamlessly authenticating and integrating Twilio for telephony, Google Cloud for calendar management, and OpenAI for orchestration.

---

## 🎯 System Architecture & Tech Stack

- **Backend / API Gateway**: **Python 3.11+, FastAPI, Uvicorn**
- **Agent Orchestrator**: **[Langflow](https://langflow.org)** (with dynamic Flow ID management)
- **LLM Brain**: **OpenAI GPT-4o**
- **Speech-to-Text (STT)**: **[Deepgram](https://deepgram.com)**
- **Text-to-Speech (TTS)**: **[ElevenLabs](https://elevenlabs.io)** (Google TTS Fallback)
- **Tooling Integrations**: **Google Calendar API, Twilio Voice**
- **Package Management**: **`uv`** (for lightning-fast isolated environments)

---

## 🚀 Complete Guide to Testing

Follow this comprehensive guide to get the AI agent running on your local machine in under 10 minutes.

### 1. Prerequisites

You will need the following accounts/tools:

- **Python 3.11+**
- **[uv](https://github.com/astral-sh/uv)** installed.
- API Keys for **OpenAI**, **Deepgram**, and **Langflow** (if running via cloud).
- _(Optional)_ **ElevenLabs** API Key for ultra-realistic voices.

### 2. Environment Configuration

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd langflow
uv sync
```

Create a `.env` file in the project root:

```env
# Required API Keys
OPENAI_API_KEY=sk-...
DEEPGRAM_API_KEY=...
LANGFLOW_API_KEY=sk-...

# Google Calendar Configuration (See Section 3)
GOOGLE_CALENDAR_ID=your-calendar-id@group.calendar.google.com
GOOGLE_SERVICE_ACCOUNT_FILE=credentials.json

# Optional Keys
ELEVENLABS_API_KEY=...

# App Configuration
LANGFLOW_BASE_URL=http://localhost:7860
```

### 3. Google Calendar Setup (For active booking)

To let the AI book real appointments, you need a Google Service Account.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/), create a project, and enable the **Google Calendar API**.
2. Go to **IAM & Admin > Service Accounts**, create an account, and generate a **JSON Key**. Save this file as `credentials.json` in your project root.
3. Open your real [Google Calendar](https://calendar.google.com/), go to **Settings and sharing**, copy the **Calendar ID**, and share it with the email address inside `credentials.json` (grant "Make changes to events" permissions).
4. Run the tester script to verify your setup:
   ```bash
   uv run test_calendar.py
   ```

### 4. Setup the Langflow Brain

You must start Langflow on port 7860 for the backend to communicate with it.

```bash
uv run langflow run --port 7860
```

In a _new terminal_, automate the flow import. This script creates the agent, saves the flow ID, and configures everything.

```bash
uv run agent_management/import_flows.py --api-key YOUR_LANGFLOW_API_KEY
```

**Final step in Langflow:**

1. Open [http://localhost:7860](http://localhost:7860).
2. Open the newly imported **"Appointment Scheduler (Unified)"** flow.
3. Locate the **OpenAI Component** and paste your `OPENAI_API_KEY` directly inside the GUI, then click **Save**.

### 5. Run the Application

Start the FastAPI voice backend:

```bash
uv run app.py
```

1. Open [http://localhost:8000](http://localhost:8000) in a Chrome browser.
2. Click **"Click to Speak"** and allow microphone access.
3. **Talk to it!** Example prompt:
   > _"Hi, I'd like to book a dental cleaning for next Tuesday at 2 PM. My name is Daniel and my number is 555-0192."_
4. The AI will extract variables, confirm details, invoke the `CalendarTool`, and create an actual event in your Google Calendar!

---

## 📊 Live Feature Status

| Core Capability                  | Status  | Description                                                                  |
| :------------------------------- | :-----: | :--------------------------------------------------------------------------- |
| **Real-time Voice Web UI**       | ✅ 100% | Low latency Web Audio interface parsing Deepgram streams.                    |
| **Unified Agent Scripting**      | ✅ 100% | Automated conversion of state logic into LLM System Prompts.                 |
| **Google Calendar Booking**      | ✅ 100% | End-to-end tooling logic for checking availability and booking.              |
| **Automated Flow ID Management** | ✅ 100% | `import_flows.py` intelligently syncs application IDs.                       |
| **Twilio Phone Integration**     | ⏳ 80%  | Backend endpoints (`/incoming_call`) created; pending active number testing. |
| **Email/SMS Confirmation**       |  ⏳ 0%  | Scheduled integration for SendGrid/Twilio POST-booking.                      |

---

## 📞 Support & Community

If you encounter issues mapping audio inputs, ensure you are accessing the app via `http://localhost:8000` (Modern browsers block microphones on raw IPs like `0.0.0.0`).

For logic debugging, view the comprehensive prompt structures inside `agent_management/vapi_converter/unified_agent_builder.py`.

**Maintained by**: VoxHive Team  
**Version**: 2.0.0 - _Production Ready_
