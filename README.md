# Voice AI Dental Agent

**Intelligent voice interface for dental appointment scheduling powered by Langflow, Deepgram, and ElevenLabs**

[![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen)]()
[![Voice Interface](https://img.shields.io/badge/voice-enabled-blue)]()
[![AI Powered](https://img.shields.io/badge/AI-Langflow%20%2B%20OpenAI-purple)]()

---

## 📊 Feature Implementation Status

| Feature | Implementation | Status | Notes |
|---------|---------------|--------|-------|
| **1. Variable Extraction** | ✅ 100% | **COMPLETE** | Handled via Unified Agent system prompt |
| **2. Conversation Flow** | ✅ 100% | **COMPLETE** | First messages & transitions in system prompt |
| **3. Basic Chat** | ✅ 100% | **COMPLETE** | Full STT → Agent → TTS pipeline working |
| **4. Conditional Routing** | ✅ 100% | **COMPLETE** | LLM-driven routing via Unified Agent approach |
| **5. Tool Integration** | ⏳ 0% | **PLANNED** | Calendar booking, call transfer (future) |
| **Overall Progress** | **80%** | **4/5 Complete** | Core voice system ready, tools pending |

### What's Working Now
- ✅ **Voice conversations** with real-time STT/TTS
- ✅ **Smart routing** - Agent follows conversation flow intelligently
- ✅ **Variable extraction** - Agent captures customer info
- ✅ **Multi-turn dialogue** - Maintains context across conversation
- ✅ **Greeting handling** - Plays custom greeting on connect

### What's Next
- ⏳ **Google Calendar integration** - For appointment booking
- ⏳ **Call transfer** - Route to human agents
- ⏳ **SMS notifications** - Appointment confirmations

---

## 🎯 Overview

A complete voice AI system that enables natural conversation for dental appointment scheduling. Built with:

- **Voice Interface** (Web & Phone)
- **Speech Recognition** (Deepgram)
- **AI Agent** (Langflow + OpenAI GPT-4)
- **Text-to-Speech** (ElevenLabs with Google TTS fallback)
- **VAPI to Langflow Conversion** (Unified Agent approach)

**Use Case:** Replace traditional phone systems with intelligent voice AI for appointment scheduling, rescheduling, and general inquiries.

---

## 🚀 Quick Start - Testing the Dental Agent

### Prerequisites

- Python 3.11+
- Node.js (for uv package manager)
- OpenAI API key
- Deepgram API key
- ElevenLabs API key (optional, Google TTS works as fallback)
- Langflow API key

### Step 1: Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd langflow

# Install dependencies
uv sync
```

### Step 2: Configure Environment

Create a `.env` file:

```bash
# Required API Keys
OPENAI_API_KEY=sk-...
DEEPGRAM_API_KEY=...
ELEVENLABS_API_KEY=...  # Optional, fallback to Google TTS
LANGFLOW_API_KEY=sk-...

# Langflow Configuration
LANGFLOW_BASE_URL=http://localhost:7860
```

### Step 3: Start Langflow

```bash
# Start Langflow (must run on port 7860)
uv run langflow run
```

**Important:** Langflow MUST run on port 7860 for the system to work.

### Step 4: Import the Dental Agent

```bash
# Import flows to Langflow
python3 agent_management/import_flows.py --api-key YOUR_LANGFLOW_API_KEY
```

This will:
- Import the "Appointment Scheduler (Unified)" flow
- Save the Flow ID to `flow_config.json`
- Auto-configure the connection

**Manual Alternative:** If you prefer to generate the agent from Vapi JSON:

```bash
python3 agent_management/vapi_converter/vapi_to_langflow_realnode_converter.py \
  agent_management/json/inputs/daniel_dental_agent.json \
  agent_management/flows/Appointment_Scheduler_Unified.json
```

### Step 5: Add OpenAI Key in Langflow

1. Open http://localhost:7860
2. Navigate to your imported "Appointment Scheduler (Unified)" flow
3. Click on the OpenAI component
4. Add your OpenAI API key
5. Save the flow

### Step 6: Start the Voice Interface

```bash
# Start the web voice interface
uv run app.py
```

### Step 7: Test the Agent

1. Open http://localhost:8000 in your browser
2. Click the **"Click to Speak"** button
3. Allow microphone access
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

```
/
├── app.py                              # Main web voice interface
├── twilio_bridge_production.py         # Twilio phone integration
├── static/                              # Frontend assets
│   ├── script.js                       # Voice UI logic
│   └── style.css                       # UI styling
├── templates/
│   └── index.html                      # Main HTML page
├── .env                                 # API keys (gitignored)
├── flow_config.json                     # Auto-generated Flow ID
│
└── agent_management/                    # Agent utilities
    ├── flows/                           # Exported Langflow flows
    ├── json/                            # Vapi JSON workflows
    │   └── inputs/
    │       └── daniel_dental_agent.json # Dental agent workflow
    ├── import_flows.py                  # Import to Langflow
    ├── export_flows.py                  # Export from Langflow
    └── vapi_converter/                  # Conversion utilities
        ├── vapi_to_langflow_realnode_converter.py
        └── unified_agent_builder.py
```

---

## 🎯 How It Works

### Voice Conversation Flow

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

| Service | Required | Fallback | Purpose |
|---------|----------|----------|---------|
| OpenAI | ✅ Yes | None | Agent intelligence |
| Deepgram | ✅ Yes | None | Speech-to-Text |
| Langflow | ✅ Yes | None | Agent platform |
| ElevenLabs | ⚠️ Optional | Google TTS | Text-to-Speech |

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

## 🎯 Next Steps

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
- ⏳ Google Calendar integration
- ⏳ Appointment booking tool
- ⏳ Call transfer tool
- ⏳ SMS notifications
- ⏳ Phone integration (Twilio)

---

## 📊 Build Progress

| Component | Status | Notes |
|-----------|--------|-------|
| Voice UI | ✅ 100% | Web interface complete |
| STT (Deepgram) | ✅ 100% | Working |
| TTS (ElevenLabs) | ✅ 100% | With Google TTS fallback |
| Langflow Agent | ✅ 100% | Unified approach |
| VAPI Converter | ✅ 100% | Generates Unified Agent |
| Import/Export | ✅ 100% | Auto-detects directories |
| Dynamic Flow ID | ✅ 100% | Auto-configuration |
| Google Calendar | ⏳ 0% | Planned |
| Tool Calling | ⏳ 0% | Planned |
| Phone (Twilio) | ✅ 80% | Backend ready, needs testing |

---

## 📞 Support

### Documentation
- `VOICE_SETUP_GUIDE.md` - Voice interface setup
- `walkthrough.md` - Complete feature walkthrough
- `google_calendar_setup.md` - Calendar integration guide

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
