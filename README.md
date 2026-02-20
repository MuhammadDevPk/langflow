# 🎙️ Voxhive Voice AI Dental Agent

**An intelligent, multi-turn voice interface for dental appointment scheduling powered by Langflow, Deepgram, and ElevenLabs.**

[![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen)]()
[![Voice Interface](https://img.shields.io/badge/voice-enabled-blue)]()
[![AI Powered](https://img.shields.io/badge/AI-Langflow%20%2B%20OpenAI-purple)]()

---

## 🌟 Overview

Voxhive Dental Agent is a production-ready Voice AI system designed to handle dental appointment scheduling with natural, human-like conversation. It automates the intake process, captures patient details, and provides a seamless scheduling experience over the web or phone.

By combining **Deepgram** for lightning-fast speech-to-text, **ElevenLabs** for realistic text-to-speech, and **Langflow** for intelligent agent orchestration, this project demonstrates a modern approach to Voice AI agents.
| Feature | Implementation | Status | Notes |
| -------------------------- | -------------- | --------------------- | --------------------------------------------- |
| **1. Variable Extraction** | ✅ 100% | **COMPLETE** | Handled via Unified Agent system prompt |
| **2. Conversation Flow** | ✅ 100% | **COMPLETE** | First messages & transitions in system prompt |
| **3. Basic Chat** | ✅ 100% | **COMPLETE** | Full STT → Agent → TTS pipeline working |
| **4. Conditional Routing** | ✅ 100% | **COMPLETE** | LLM-driven routing via Unified Agent approach |
| **5. Tool Integration** | ✅ 100% | **COMPLETE** | Google Calendar booking and availability |
| **Overall Progress** | **100%** | **All Core Complete** | Voice system and tool integrations ready. |

### What's Working Now

- ✅ **Full Google Calendar Integration** - Book, check availability, and cancel dental appointments.
- ✅ **Voice conversations** with real-time STT/TTS.
- ✅ **Smart routing** - Agent follows conversation flow intelligently.
- ✅ **Variable extraction** - Agent captures patient info (name, phone, email, etc.).
- ✅ **Multi-turn dialogue** - Maintains context across conversation.
- ✅ **Greeting handling** - Plays custom greeting on connect.

### What's Next

- ⏳ **Call transfer** - Route to human agents.
- ⏳ **SMS/Email notifications** - Real appointment confirmations via SendGrid/Twilio.
- ⏳ **Advanced Availability** - Multi-doctor scheduling.

---

## ✨ Key Features

- ✅ **Real-time Voice Conversation**: Low-latency STT/TTS pipeline for natural dialogue.
- ✅ **Dynamic Context Management**: Maintains conversation state across multiple turns.
- ✅ **Unified Agent Architecture**: Simplified Langflow structure for higher reliability and faster responses.
- ✅ **Automated Extraction**: Intelligently captures patient names, appointment types, and preferences.
- ✅ **Multi-channel Ready**: Web interface included, with Twilio integration for phone calls.
- ✅ **Smart Fallbacks**: Automatic fallback to Google TTS if ElevenLabs quota is exceeded.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **Agent Orchestration**: [Langflow](https://langflow.org)
- **Large Language Model**: OpenAI GPT-4
- **Speech-to-Text (STT)**: [Deepgram](https://deepgram.com)
- **Text-to-Speech (TTS)**: [ElevenLabs](https://elevenlabs.io)
- **Package Management**: `uv` (Fast Python package installer)

---

## 🚀 Getting Started

Follow these steps to set up and run the Dental Agent locally.

### 1. Prerequisites

Before you begin, ensure you have the following:

- **Python 3.11+** installed.
- **[uv](https://github.com/astral-sh/uv)** installed (for fast dependency management).
- **API Keys** for the following services:
  - [OpenAI](https://platform.openai.com/)
  - [Deepgram](https://console.deepgram.com/)
  - [ElevenLabs](https://elevenlabs.io/) (Optional, fallback provided)
  - [Langflow](https://langflow.org) (If running remotely)

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd langflow

# Install project dependencies using uv
uv sync
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
# Required API Keys
OPENAI_API_KEY=sk-...
DEEPGRAM_API_KEY=...
LANGFLOW_API_KEY=sk-...

# Google Calendar Configuration
GOOGLE_CALENDAR_ID=your-calendar-id@group.calendar.google.com
GOOGLE_SERVICE_ACCOUNT_FILE=credentials.json

# Optional API Keys (Fallback to Google TTS if not provided)
ELEVENLABS_API_KEY=...

# Configuration
LANGFLOW_BASE_URL=http://localhost:7860
```

### 4. Setup Langflow

#### Step A: Start Langflow

The agent requires a local Langflow instance running on port 7860.

```bash
uv run langflow run --port 7860
```

#### Step B: Import the Dental Agent

In a new terminal window, run the import script to automatically upload the necessary flows to Langflow:

```bash
uv run agent_management/import_flows.py --api-key YOUR_LANGFLOW_API_KEY
```

This will:

- Import the "Appointment Scheduler (Unified)" flow
- Save the Flow ID to `flow_config.json`
- Auto-configure the connection

#### Step C: Add OpenAI Key in Langflow UI

1. Open [http://localhost:7860](http://localhost:7860).
2. Open the imported **"Appointment Scheduler (Unified)"** flow.
3. Locate the **OpenAI Component** and paste your API key.
4. Click **Save** in the Langflow UI.

---

## 📅 Google Calendar Setup

To enable appointment booking, you must set up a Google Cloud Service Account:

### 1. Create Google Cloud Project

- Go to [Google Cloud Console](https://console.cloud.google.com/).
- Create a new project and enable the **Google Calendar API**.

### 2. Create Service Account

- Navigate to **IAM & Admin > Service Accounts**.
- Create a service account and generate a **JSON Key**.
- Rename the downloaded file to `credentials.json` and place it in the project root.

### 3. Share Calendar

- Open [Google Calendar](https://calendar.google.com/).
- Create a new calendar for the agent or use an existing one.
- Go to **Settings and sharing**.
- Get the **Calendar ID** (usually an email-like string).
- Under **Share with specific people**, add the Service Account email (found in your `credentials.json`) with **Make changes to events** permission.

### 4. Verify Connection

Run the verification script to ensure the agent can connect:

```bash
uv run test_calendar.py
```

---

## 🎤 Running the Application

Once Langflow and Google Calendar are set up, start the Voice Interface backend:

```bash
uv run app.py
```

### Step 5: Test the Agent

1. Open [http://localhost:8000](http://localhost:8000) in your browser.
2. Click **"Click to Speak"** and allow microphone access.
3. **How to Book an Appointment**:
   - Provide your name, phone number, and email.
   - Specify the type of appointment (e.g., "Cleaning").
   - Suggest a date (YYYY-MM-DD) and time (HH:MM).
   - The agent will confirm the details and call the `book_appointment` tool.
   - Check your Google Calendar to see the new event!
4. Start speaking!

**Example conversation:**

```
Agent: "Thank you for calling Wellness Partners. This is Riley, your scheduling assistant. How may I help you today?"

You: "I need to book an appointment"

Agent: "I'd be happy to help you book an appointment! Are you a new patient or an existing patient?"

You: "I'm a new patient"

Agent: "Great! What type of appointment do you need?"
```

---

## ✨ Features

### 1. Voice Interface ✅ Production Ready

**Web Interface:**

- Real-time voice conversation
- Voice Activity Detection (VAD)
- Visual feedback (monitoring, recording, agent speaking)
- Automatic greeting on connect

**Phone Interface (Twilio):**

- Incoming call handling
- Multi-agent support
- TwiML response generation

**Tech Stack:**

- Frontend: Vanilla JavaScript with Web Audio API
- Backend: FastAPI + Python
- STT: Deepgram API
- TTS: ElevenLabs (with Google TTS fallback)

---

### 2. Unified Agent Architecture ✅ Production Ready

**Conversion Approach:**

- Converts VAPI JSON workflows to single Unified Agent
- All conversation logic in one comprehensive system prompt
- Avoids Langflow's conditional routing limitations
- Simpler, more reliable execution

**Generated Structure:**

- 1 ChatInput node
- 1 OpenAI Model node (Unified Agent)
- 1 ChatOutput node
- Simple linear flow

**Why Unified?**

- ✅ Avoids Langflow's If-Else component bugs
- ✅ Simpler to maintain and debug
- ✅ Better conversation context handling
- ✅ Faster response times

---

### 3. Dynamic Flow ID Management ✅ Production Ready

**Problem Solved:** Flow IDs change when importing to different Langflow instances

**Solution:**

- `import_flows.py` saves Flow ID to `flow_config.json`
- `app.py` automatically reads from config
- No manual ID copying needed

**Benefits:**

- 🎯 Works for all team members after import
- 🎯 No code changes needed
- 🎯 Clear warning if ID is missing

---

### 4. Agent Management Tools ✅ Production Ready

**Export Flows:**

```bash
python3 agent_management/export_flows.py --api-key YOUR_API_KEY
```

**Import Flows:**

```bash
python3 agent_management/import_flows.py --api-key YOUR_API_KEY
```

**Convert Vapi to Langflow:**

```bash
python3 agent_management/vapi_converter/vapi_to_langflow_realnode_converter.py \
  agent_management/json/inputs/daniel_dental_agent.json \
  agent_management/flows/output.json
```

**All scripts:**

- Auto-detect correct directories
- Work from any location
- Save configs to project root

---

## 📁 Project Structure

```text
.
├── app.py                  # FastAPI Backend & Orchestration
├── agent_management/       # Agent flows, scripts & conversion tools
│   ├── flows/              # Exported Langflow JSON files
│   ├── import_flows.py     # Automated flow importer
│   └── vapi_converter/     # Tools to convert VAPI JSON to Langflow
├── static/                 # Frontend CSS and JavaScript
├── templates/              # HTML Templates (index.html)
├── .env.example            # Template for environment variables
└── pyproject.toml          # Project dependencies (managed by uv)
```

---

## 🧪 Testing Scenarios

Try these conversations to test the agent's capabilities:

```
1. User clicks microphone
   ↓
2. Greeting plays (from Vapi JSON)
   ↓
3. User speaks → Audio recorded
   ↓
4. Deepgram transcribes audio → Text
   ↓
5. Langflow processes with GPT-4 → Response text
   ↓
6. ElevenLabs synthesizes → Audio
   ↓
7. Audio plays to user
   ↓
8. Repeat from step 3
```

### Multi-Turn Conversation

- Langflow maintains conversation context
- Each message includes history
- Agent remembers previous responses
- Seamless multi-turn dialogue

---

## 🧪 Testing

### Test Scenarios

**Scenario 1: New Appointment**

```
You: "I need to book an appointment"
Expected: Agent asks if new/existing patient
```

**Scenario 2: Reschedule**

```
You: "I need to reschedule my appointment"
Expected: Agent asks for appointment details
```

**Scenario 3: General Info**

```
You: "What are your office hours?"
Expected: Agent provides information
```

**Scenario 4: Cancellation**

```
You: "I need to cancel my appointment"
Expected: Agent handles cancellation flow
```

### Error Handling Tests

**Empty Audio:**

- Speak nothing → "Could not transcribe audio. Please speak clearly."

**Invalid API Key:**

- App shows warning at startup
- Langflow errors shown in response

**Network Errors:**

- Graceful error messages
- Fallback TTS if ElevenLabs fails

---

## 🔧 Configuration

### API Keys Required

| Service    | Required    | Fallback   | Purpose            |
| ---------- | ----------- | ---------- | ------------------ |
| OpenAI     | ✅ Yes      | None       | Agent intelligence |
| Deepgram   | ✅ Yes      | None       | Speech-to-Text     |
| Langflow   | ✅ Yes      | None       | Agent platform     |
| ElevenLabs | ⚠️ Optional | Google TTS | Text-to-Speech     |

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...
DEEPGRAM_API_KEY=...
LANGFLOW_API_KEY=sk-...

# Optional
ELEVENLABS_API_KEY=...
LANGFLOW_BASE_URL=http://localhost:7860
```

---

## 🚨 Troubleshooting

### "No LANGFLOW_FLOW_ID found"

**Solution:**

```bash
python3 agent_management/import_flows.py --api-key YOUR_API_KEY
```

### "Could not access microphone"

**Solution:** Access via http://localhost:8000 (not http://0.0.0.0:8000)

### "404: /get_greeting"

**Solution:** Restart app.py to reload the endpoint

### Langflow not responding

**Solution:** Ensure Langflow is running on port 7860:

```bash
uv run langflow run
```

---

## 📞 Support & Community

### Current Features (Complete)

- ✅ Voice interface (web)
- ✅ Unified agent architecture
- ✅ Dynamic Flow ID management
- ✅ Speech recognition (Deepgram)
- ✅ Text-to-speech (ElevenLabs + Google TTS)
- ✅ Multi-turn conversations
- ✅ Greeting message
- ✅ Auto-import/export tools

### Planned Features

- ⏳ **Call transfer tool**
- ⏳ **SMS/Email notifications** (Real sending via SendGrid/Twilio)
- ⏳ **Native Twilio Integration**

---

## 📊 Build Progress

| Component        | Status  | Notes                        |
| ---------------- | ------- | ---------------------------- |
| Voice UI         | ✅ 100% | Web interface complete       |
| STT (Deepgram)   | ✅ 100% | Working                      |
| TTS (ElevenLabs) | ✅ 100% | With Google TTS fallback     |
| Langflow Agent   | ✅ 100% | Unified approach             |
| VAPI Converter   | ✅ 100% | Generates Unified Agent      |
| Import/Export    | ✅ 100% | Auto-detects directories     |
| Dynamic Flow ID  | ✅ 100% | Auto-configuration           |
| Google Calendar  | ✅ 100% | Book, check & cancel logic   |
| Tool Calling     | ✅ 100% | Automated tool injection     |
| Phone (Twilio)   | ✅ 80%  | Backend ready, needs testing |

---

## 📞 Support

### Documentation

- [README.md](file:///Users/muhammad/Personal/Projects/Personal%20Projects/pawel/Voxhive/langflow/README.md) - Main guide
- [walkthrough.md](file:///Users/muhammad/.gemini/antigravity/brain/fc80fdd6-1900-4f4a-b2af-86d81ab25094/walkthrough.md) - Feature walkthrough

### Common Issues

**Microphone not working:**

- Use http://localhost:8000 (browsers require secure context)

**Agent not responding:**

- Check OpenAI key in Langflow UI
- Verify Langflow is running on port 7860

**Import fails:**

- Ensure Langflow is running
- Check API key is valid

---

## 🙏 Credits

Built with:

- [Langflow](https://langflow.org) - Visual AI workflow builder
- [OpenAI](https://openai.com) - GPT-4 language model
- [Deepgram](https://deepgram.com) - Speech-to-Text API
- [ElevenLabs](https://elevenlabs.io) - Text-to-Speech API
- [FastAPI](https://fastapi.tiangolo.com) - Web framework
- [Twilio](https://twilio.com) - Phone integration

---

**Version:** 2.0.0
**Last Updated:** November 26, 2025
**Status:** Production Ready
**Maintained by:** VoxHive Team

---

## 🚀 Get Started Now

```bash
# 1. Start Langflow
uv run langflow run

# 2. Import agent
python3 agent_management/import_flows.py --api-key YOUR_KEY

# 3. Start voice interface
uv run app.py

# 4. Open browser
http://localhost:8000
```

**That's it!** Click "Click to Speak" and start talking! 🎤
