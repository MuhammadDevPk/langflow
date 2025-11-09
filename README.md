# LangVoice - AI Voice Agent System

A production-ready AI voice agent system that allows users to call a phone number and have natural conversations with AI agents powered by Langflow and OpenAI.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Flow Management](#flow-management)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)

---

## 🎯 Overview

**LangVoice** enables phone-based interactions with AI agents. Users can:

1. **Call a Twilio phone number** (e.g., +1-472-230-2360)
2. **Speak naturally** - Twilio transcribes speech to text
3. **AI agent responds** - Langflow processes the request using GPT models
4. **Hear the response** - Twilio converts agent response to natural speech
5. **Continue conversation** - Multi-turn conversations supported

**Use Cases:**
- Hotel booking assistance
- Car rental services
- Customer support
- Appointment scheduling
- FAQ automation
- Any voice-based AI interaction

---

## 🏗️ Architecture

```
┌─────────────┐
│   Caller    │
│   (Phone)   │
└──────┬──────┘
       │
       ↓
┌─────────────────┐
│  Twilio Voice   │  (Receives call, transcribes speech)
│  Phone Number   │
└────────┬────────┘
         │
         ↓
┌────────────────────┐
│  Railway (Cloud)   │  (Twilio Bridge - deployed)
│  twilio_bridge_    │  - Handles Twilio webhooks
│  production.py     │  - Routes to correct agent
└────────┬───────────┘
         │
         ↓
┌─────────────────┐
│  Ngrok Tunnel   │  (Exposes local Langflow to internet)
└────────┬────────┘
         │
         ↓
┌──────────────────────┐
│  Langflow (Local)    │  (AI agent processing)
│  - Processes queries │  - Uses OpenAI GPT models
│  - Manages agents    │  - Generates responses
└──────────────────────┘
```

**Why this architecture?**
- ✅ **Free for testing** - Langflow runs locally (no cloud costs)
- ✅ **Fast iteration** - Change agents instantly, no redeployment
- ✅ **Scalable** - Easy to move Langflow to cloud later
- ✅ **Cost-effective** - Only pay for Twilio calls and Railway bridge

---

## ✨ Features

### Current Features:
- ✅ **Voice Conversations** - Natural phone-based interactions
- ✅ **Speech Recognition** - Automatic speech-to-text via Twilio
- ✅ **Text-to-Speech** - Natural voice responses (AWS Polly voices)
- ✅ **Multi-turn Conversations** - Agents remember context
- ✅ **Multiple Agents** - Hotel, car rental, customer support, etc.
- ✅ **Dynamic Routing** - Route calls to different agents (ready but not active)
- ✅ **Flow Management** - Version control for AI agent flows
- ✅ **Production Ready** - Deployed bridge on Railway
- ✅ **Error Handling** - Comprehensive logging and error recovery

### Supported Voices:
- Polly.Matthew (Male, US English)
- Polly.Joanna (Female, US English)
- Polly.Amy (Female, British English)
- And many more AWS Polly voices

---

## 📋 Prerequisites

### Required:
- **Python 3.11+** (project uses 3.11)
- **UV package manager** ([Install UV](https://docs.astral.sh/uv/))
- **Git** for version control
- **GitHub account** for code hosting

### Accounts Needed:
- **Twilio Account** - For phone number and voice services
  - Sign up: https://www.twilio.com/try-twilio
  - Free trial: $15 credit (~100+ calls)

- **Railway Account** - For deploying the bridge
  - Sign up: https://railway.app
  - Free tier: $5/month credit

- **Ngrok Account** - For exposing local Langflow
  - Sign up: https://dashboard.ngrok.com/signup
  - Free tier: Unlimited usage

- **OpenAI API Key** - For AI agents
  - Get key: https://platform.openai.com/api-keys
  - Pay-per-use pricing

---

## 🚀 Getting Started

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/langflow.git
cd langflow
```

### Step 2: Install Dependencies

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### Step 3: Set Up Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and fill in your values (see [Environment Variables](#environment-variables) section).

### Step 4: Start Langflow

```bash
uv run langflow run --port 7860
```

You should see:
```
✓ Launching Langflow...
🟢 Open Langflow → http://localhost:7860
```

Keep this terminal running!

### Step 5: Import Flows

**In a new terminal:**

```bash
# Generate API key in Langflow UI first:
# 1. Open http://localhost:7860
# 2. Settings → API Keys → Generate new key

# Import all flows with one command:
python import_flows.py --api-key YOUR_LANGFLOW_API_KEY
```

The smart import script will:
- ✅ Detect or create "LangVoice Flows" folder
- ✅ Import all 25+ agent flows
- ✅ Skip flows that already exist
- ✅ Open your browser automatically

### Step 6: Add OpenAI API Keys to Flows

**Important:** API keys are removed from exported flows for security.

For each imported flow:
1. Open flow in Langflow UI
2. Find the OpenAI/Agent component
3. Add your OpenAI API key
4. Save the flow

### Step 7: Set Up Ngrok

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/download

# Set auth token (get from https://dashboard.ngrok.com/get-started/your-authtoken)
ngrok config add-authtoken YOUR_NGROK_TOKEN

# Start ngrok (in a new terminal)
ngrok http 7860
```

Copy the `https://....ngrok-free.app` URL - you'll need it for deployment!

---

## 📦 Flow Management

### Exporting Flows (After Making Changes)

Whenever you modify flows in Langflow, export them to Git:

```bash
# Export all flows
python export_flows.py --api-key YOUR_LANGFLOW_API_KEY

# Commit to Git
git add flows/
git commit -m "Update flows: description of changes"
git push
```

**What gets exported:**
- ✅ All flow configurations as JSON
- ✅ Agent prompts and settings
- ❌ API keys (automatically scrubbed for security)

### Importing Flows (On New Machine)

```bash
# 1. Start Langflow
uv run langflow run

# 2. Import flows
python import_flows.py --api-key YOUR_LANGFLOW_API_KEY

# 3. Add your OpenAI API keys to each flow
```

### Force Re-import All Flows

```bash
python import_flows.py --api-key YOUR_LANGFLOW_API_KEY --force
```

---

## 🌐 Deployment

### Deploy Bridge to Railway

The Twilio bridge (`twilio_bridge_production.py`) runs on Railway cloud platform.

**Complete deployment guide:** See `RENDER_DEPLOYMENT.md` (works for Railway too!)

**Quick Steps:**

#### 1. Push Code to GitHub

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### 2. Create Railway Service

1. Go to **https://railway.app**
2. Sign in with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository
5. Railway creates the service

#### 3. Configure Railway

**Settings → Build:**
```
Build Command: pip install -r requirements.txt
```

**Settings → Deploy:**
```
Start Command: gunicorn twilio_bridge_production:app
```

#### 4. Add Environment Variables

Go to **Variables** tab and add (see [Environment Variables](#environment-variables) for details):

```
LANGFLOW_URL=https://your-ngrok-url.ngrok-free.app
DEFAULT_FLOW_ID=your-flow-id-from-langflow
LANGFLOW_API_KEY=your-langflow-api-key
DEFAULT_VOICE_INTRO=Hi, this is your LangVoice agent. How can I help you today?
DEFAULT_VOICE_TYPE=Polly.Matthew
AGENT_MAPPINGS={}
DEBUG_MODE=true
PORT=5000
```

**Important:** Use your actual ngrok URL from Step 7 above!

#### 5. Deploy

Railway auto-deploys. Wait 1-2 minutes.

#### 6. Get Railway URL

Settings → Networking → **"Generate Domain"**

Copy: `https://your-service.railway.app`

#### 7. Configure Twilio

1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Click your Twilio phone number
3. Under "Voice Configuration" → "A call comes in":
   - Webhook: `https://your-service.railway.app/voice`
   - Method: **POST**
4. **Save**

#### 8. Test!

Call your Twilio number and start chatting with the AI agent!

---

## 🔑 Environment Variables

### For Local Development (.env)

Copy `.env.example` to `.env` and fill in:

```bash
# Langflow API Key (get from Langflow UI → Settings → API Keys)
LANGFLOW_API_KEY=sk-xxxxxxxxxxxxx

# Ngrok auth token (get from ngrok.com dashboard)
NGROK_AUTH_TOKEN=xxxxxxxxxxxxx
```

### For Railway Deployment

Add these in Railway dashboard → Variables tab:

| Variable | Description | Example |
|----------|-------------|---------|
| `LANGFLOW_URL` | Your ngrok URL exposing local Langflow | `https://abc-123.ngrok-free.app` |
| `DEFAULT_FLOW_ID` | Flow ID of your agent (from Langflow URL) | `9c7c075b-85da-4dfd-ae0c-bcb322851b04` |
| `LANGFLOW_API_KEY` | Langflow API key for authentication | `sk-xxxxxxxxxxxxx` |
| `DEFAULT_VOICE_INTRO` | Greeting message when call starts | `Hi, this is your LangVoice agent...` |
| `DEFAULT_VOICE_TYPE` | AWS Polly voice to use | `Polly.Matthew` |
| `AGENT_MAPPINGS` | JSON mapping for multi-agent routing | `{}` (empty for single agent) |
| `DEBUG_MODE` | Enable detailed logging | `true` or `false` |
| `PORT` | Port for Railway to run on | `5000` |

**How to get DEFAULT_FLOW_ID:**
1. Open your agent flow in Langflow
2. Look at browser URL: `http://localhost:7860/flow/FLOW-ID-HERE`
3. Copy the Flow ID from URL

---

## 🐛 Troubleshooting

### "I pulled the repo but see no flows in Langflow"

Flows are stored as JSON files in Git but need to be imported:

```bash
python import_flows.py --api-key YOUR_LANGFLOW_API_KEY
```

### "Flows are failing with API key errors"

API keys are removed from exported flows for security. Add your OpenAI API key to each flow:

1. Open flow in Langflow UI
2. Find OpenAI/Agent component
3. Add your API key
4. Save

### "Langflow won't start - port 7860 in use"

Check if Langflow is already running:

```bash
# Find what's using port 7860
lsof -i :7860

# Kill old Langflow instance
kill -9 <PID>
```

### "Ngrok command not found"

Install ngrok:

```bash
# macOS
brew install ngrok

# Or download from https://ngrok.com/download
```

### "Railway deployment failed"

Check Railway logs:
1. Railway dashboard → Your service → Deployments
2. Click latest deployment → View logs
3. Look for error messages

Common issues:
- Missing environment variables
- Wrong LANGFLOW_URL
- Incorrect Flow ID

### "Voice calls not working"

**Check this order:**

1. **Is Langflow running?**
   ```bash
   curl http://localhost:7860/health
   # Should return: {"status": "ok"}
   ```

2. **Is Ngrok running?**
   ```bash
   # Check Terminal 2 - should show "Session Status: online"
   ```

3. **Is Railway bridge healthy?**
   ```bash
   curl https://your-service.railway.app/health
   # Should return: "langflow_status": "connected"
   ```

4. **Is Twilio webhook correct?**
   - Check webhook URL ends with `/voice`
   - Check method is POST

### "Agent not responding intelligently"

Check OpenAI API key is set in your Langflow flow:
1. Open flow in Langflow
2. Check OpenAI component has API key
3. Test flow directly in Langflow UI first

### "Ngrok URL changed and calls stopped working"

When you restart ngrok, the URL changes (free tier):

1. Copy new ngrok URL
2. Railway → Variables → Update `LANGFLOW_URL`
3. Wait 30 seconds for Railway to restart

**Solution:** Get ngrok paid plan ($8/month) for static URL that never changes.

---

## 📁 Project Structure

```
langflow/
├── .env.example                      # Environment variables template
├── README.md                         # This file
├── RENDER_DEPLOYMENT.md              # Deployment guide
├── requirements.txt                  # Python dependencies for bridge
├── pyproject.toml                    # Project configuration
├── uv.lock                           # Dependency lock file
│
├── twilio_bridge_production.py      # Production Twilio bridge (DEPLOY THIS!)
│
├── flows/                            # Langflow agent flows (Git-tracked)
│   ├── Main Agent_*.json             # Main agent that creates others
│   ├── Basic Agent Blue Print_*.json # Template for new agents
│   ├── LangVoice Agent*.json         # Various specialized agents
│   └── manifest.json                 # Flow metadata
│
├── export_flows.py                   # Export flows from Langflow
├── import_flows.py                   # Import flows to Langflow
├── scrub_secrets.py                  # Remove API keys from flows
├── list_flows.py                     # List all flows
│
└── src/                              # Langflow source code
    └── ...
```

### Key Files:

| File | Purpose |
|------|---------|
| `twilio_bridge_production.py` | Production bridge - handles Twilio calls, routes to agents |
| `requirements.txt` | Python dependencies for the bridge |
| `export_flows.py` | Exports all flows to JSON files |
| `import_flows.py` | Imports flows from JSON files to Langflow |
| `.env.example` | Template for environment variables |
| `RENDER_DEPLOYMENT.md` | Complete deployment guide |

---

## 🔐 Security Notes

### Secrets Management:

- ✅ API keys are **automatically removed** when exporting flows
- ✅ `.env` file is **gitignored** (never committed)
- ✅ Use `.env.example` as template (no actual values)
- ✅ Set API keys in Railway as environment variables

### Best Practices:

1. **Never commit** `.env` file
2. **Always scrub** secrets before sharing flows
3. **Use environment variables** for all sensitive data
4. **Rotate API keys** regularly
5. **Use different keys** for development and production

---

## 💰 Cost Breakdown

### Development/Testing (FREE):
- ✅ Langflow: Free (running locally)
- ✅ Railway: $5/month credit (free tier)
- ✅ Ngrok: Free (unlimited usage)
- ✅ Twilio: $15 trial credit (~100 calls)
- **Total: $0** for testing!

### Production (Monthly):
- Railway bridge: $0-7 (free tier covers basic usage)
- Langflow: $0 (local) or $50+ (cloud hosting)
- Ngrok Pro: $8 (for static URL - optional)
- Twilio: ~$1.15/month + $0.013/minute for calls
- OpenAI: Pay per API call (~$0.01 per conversation)

**Estimated:** $10-30/month for moderate usage

---

## 🤝 Contributing

### For Developers:

1. **Clone** the repository
2. **Create a branch** for your feature
3. **Make changes** to flows or code
4. **Export flows** before committing:
   ```bash
   python export_flows.py --api-key YOUR_KEY
   ```
5. **Commit and push**:
   ```bash
   git add .
   git commit -m "Add: description of changes"
   git push origin your-branch
   ```
6. **Create Pull Request**

### Flow Development:

1. Make changes in Langflow UI
2. Test thoroughly in UI first
3. Export flows: `python export_flows.py`
4. Commit and push
5. Others can import with: `python import_flows.py`

---

## 📚 Additional Resources

### Documentation:
- **Langflow Docs**: https://docs.langflow.org
- **Twilio Voice Docs**: https://www.twilio.com/docs/voice
- **Railway Docs**: https://docs.railway.app
- **Ngrok Docs**: https://ngrok.com/docs

### Get Help:
- **Langflow Discord**: https://discord.gg/langflow
- **Twilio Support**: https://support.twilio.com
- **Check logs** in Railway dashboard for errors

---

## 🎉 Quick Start Checklist

New developer setup:

- [ ] Clone repository
- [ ] Install UV: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] Copy `.env.example` to `.env` and fill in values
- [ ] Start Langflow: `uv run langflow run`
- [ ] Get Langflow API key from UI
- [ ] Import flows: `python import_flows.py --api-key YOUR_KEY`
- [ ] Add OpenAI API keys to each flow
- [ ] Install ngrok: `brew install ngrok`
- [ ] Set ngrok token: `ngrok config add-authtoken YOUR_TOKEN`
- [ ] Start ngrok: `ngrok http 7860`
- [ ] Deploy to Railway (see Deployment section)
- [ ] Configure Twilio webhook
- [ ] Test with phone call!

**Total setup time:** ~30 minutes

---

**Built with ❤️ using Langflow, Twilio, and OpenAI**
