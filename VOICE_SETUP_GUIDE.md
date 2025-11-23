# Voice AI Interface - Setup & Usage Guide

## Prerequisites
Before running the voice interface, ensure:

### 1. Langflow is Running
The voice interface needs Langflow to process requests.

**Check if Langflow is running:**
```bash
curl http://localhost:7860/health
```

**If NOT running, start Langflow:**
```bash
# Navigate to your Langflow installation
langflow run
# OR
python -m langflow run
```

### 2. Import Your Flow
1. Open Langflow UI: `http://localhost:7860`
2. Import `daniel_dental_agent_unified.json`
3. Copy the Flow ID from the URL (it's the UUID in the browser address bar)
4. Update `.env` with: `LANGFLOW_FLOW_ID=<your-flow-id>`

### 3. Verify API Keys in `.env`
```bash
# Check your .env file has:
OPENAI_API_KEY=sk-proj-...
DEEPGRAM_API_KEY=5856da53bcd039cfaa15d9baf95ccf4c405d0255
ELEVENLABS_API_KEY=sk_380f5cef0243e621c9a28129bf301292b64df1d5185b521a
LANGFLOW_FLOW_ID=ec2db58a-812e-461c-ba83-8054092225bc
LANGFLOW_BASE_URL=http://localhost:7860
```

## Running the Voice Interface

### Step 1: Kill Any Existing Servers
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Step 2: Start the FastAPI Server
```bash
cd /Users/muhammad/Personal/Projects/Personal\ Projects/pawel/Voxhive/langflow
python3 app.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### Step 3: Open the Interface
Open your browser to: `http://localhost:8000`

### Step 4: Test the Voice AI
1. Click the **microphone button** (it will turn red)
2. **Speak** your request: "I want to book an appointment"
3. Click the button again to **stop recording**
4. Wait for:
   - Transcript to appear (what you said)
   - Agent's text response
   - Agent's voice response to play automatically

## Troubleshooting

### "Address already in use"
```bash
lsof -ti:8000 | xargs kill -9
python3 app.py
```

### "No response from agent"
- Check Langflow is running: `curl http://localhost:7860/health`
- Verify Flow ID matches the one in Langflow UI
- Check browser console (F12) for errors

### "Could not transcribe audio"
- Grant microphone permission in browser
- Speak clearly and wait 2-3 seconds before stopping
- Check Deepgram API key is valid

### "Audio doesn't play"
- Check browser console for errors
- Verify ElevenLabs API key is valid
- Try clicking the chat message to replay audio

## Architecture Flow

```
User speaks → Browser captures audio → FastAPI backend
                                            ↓
                                    Deepgram STT
                                            ↓
                                    Text transcript
                                            ↓
                                    Langflow Agent (port 7860)
                                            ↓
                                    Agent response text
                                            ↓
                                    ElevenLabs TTS
                                            ↓
Browser plays audio ← Response sent ← Audio + Text
```

## Quick Start (All-in-One)

```bash
# 1. Kill existing servers
lsof -ti:8000 | xargs kill -9

# 2. Ensure Langflow is running (in another terminal)
# langflow run

# 3. Start voice interface
cd /Users/muhammad/Personal/Projects/Personal\ Projects/pawel/Voxhive/langflow
python3 app.py

# 4. Open browser
# http://localhost:8000
```
