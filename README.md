# 🎙️ Voxhive Voice AI Dental Agent

**An intelligent, multi-turn voice interface for dental appointment scheduling powered by Langflow, Deepgram, and ElevenLabs.**

[![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen)]()
[![Voice Interface](https://img.shields.io/badge/voice-enabled-blue)]()
[![AI Powered](https://img.shields.io/badge/AI-Langflow%20%2B%20OpenAI-purple)]()

---

## 🌟 Overview

Voxhive Dental Agent is a production-ready Voice AI system designed to handle dental appointment scheduling with natural, human-like conversation. It automates the intake process, captures patient details, and provides a seamless scheduling experience over the web or phone.

By combining **Deepgram** for lightning-fast speech-to-text, **ElevenLabs** for realistic text-to-speech, and **Langflow** for intelligent agent orchestration, this project demonstrates a modern approach to Voice AI agents.

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

# Optional API Keys
ELEVENLABS_API_KEY=... # Falls back to Google TTS if missing

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

_This script will auto-configure your `flow_config.json` with the correct Flow ID._

#### Step C: Add OpenAI Key in Langflow UI

1. Open [http://localhost:7860](http://localhost:7860).
2. Open the imported **"Appointment Scheduler (Unified)"** flow.
3. Locate the **OpenAI Component** and paste your API key.
4. Click **Save** in the Langflow UI.

---

## 🎤 Running the Application

Once Langflow is set up, start the Voice Interface backend:

```bash
uv run app.py
```

1. Open [http://localhost:8000](http://localhost:8000) in your browser.
2. Click **"Click to Speak"** and allow microphone access.
3. Start a conversation (e.g., _"I'd like to book a cleaning for next Tuesday"_).

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

- **Booking**: _"I'm a new patient and I need a check-up."_
- **Rescheduling**: _"I have an appointment on Monday but I need to move it to Wednesday."_
- **Information**: _"What are your office hours and where are you located?"_
- **Interruption**: Speak while the agent is talking to test Voice Activity Detection (VAD).

---

## 🚨 Troubleshooting

| Issue                      | Solution                                                                                                 |
| :------------------------- | :------------------------------------------------------------------------------------------------------- |
| **"Microphone not found"** | Ensure you are using `localhost:8000` (not `0.0.0.0`). Browsers require a secure context for mic access. |
| **"No Flow ID found"**     | Run `uv run agent_management/import_flows.py` to generate `flow_config.json`.                            |
| **Agent not responding**   | Verify Langflow is running on port 7860 and your OpenAI key is saved in the flow.                        |
| **Audio quality issues**   | Check your internet connection and ensure your `DEEPGRAM_API_KEY` is valid.                              |

---

## 📞 Support & Community

- **Maintainer**: Voxhive Team
- **Version**: 2.1.0
- **Last Updated**: February 20, 2026

---

**Ready to transform your dental clinic?** Get started with Voxhive today! 🦷✨
