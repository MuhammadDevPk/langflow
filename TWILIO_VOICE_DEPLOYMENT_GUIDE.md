# Twilio Voice Agent Deployment Guide

Complete guide to deploy your Langflow agents to Twilio voice calls, allowing users to call a phone number and interact with your AI agents via voice.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Twilio Setup](#twilio-setup)
- [Running the Application](#running-the-application)
- [Testing Your Agent](#testing-your-agent)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

---

## Overview

This setup allows users to:
1. **Call a Twilio phone number**
2. **Speak their query** (Twilio transcribes speech to text)
3. **Langflow agent processes** the query using your custom agent
4. **Twilio speaks the response** back using text-to-speech
5. **Continue the conversation** or end the call

### Architecture

```
User Phone Call → Twilio → [Transcribe Speech]
                              ↓
                         Flask Server (twilio_langflow_bridge.py)
                              ↓
                         Langflow API → Your Agent
                              ↓
                         Agent Response → Flask
                              ↓
                         Twilio [Text-to-Speech] → User hears response
```

---

## Prerequisites

### 1. System Requirements
- **Python 3.11+** (you're using 3.11)
- **Langflow 1.6.5** installed and running
- **Active internet connection**

### 2. Accounts Needed
- **Twilio Account** (free trial available)
  - Sign up at: https://www.twilio.com/try-twilio
  - Free trial includes $15 credit (covers ~100+ test calls)
- **Ngrok Account** (free tier works)
  - Sign up at: https://dashboard.ngrok.com/signup

### 3. Dependencies (Already Installed)
Your project already has these installed via `uv`:
```bash
flask>=3.1.2
twilio>=9.8.5
requests>=2.32.5
ngrok>=1.4.0
```

---

## Installation

### Step 1: Verify Dependencies

```bash
# Check if all dependencies are installed
uv pip list | grep -E "flask|twilio|requests|ngrok"
```

If any are missing:
```bash
uv add flask twilio requests ngrok
```

### Step 2: Get Your Langflow Flow ID

1. **Start Langflow** (if not running):
   ```bash
   langflow run --port 7860
   ```

2. **Open Langflow UI**: http://localhost:7860

3. **Find your agent flow**:
   - Go to "Flows" or open the agent you want to deploy
   - Look at the URL in your browser
   - The Flow ID is the UUID after `/flow/`

   Example:
   ```
   http://localhost:7860/flow/abc-123-def-456
                              ^^^^^^^^^^^^^^^^
                              This is your FLOW_ID
   ```

4. **Copy the Flow ID** - you'll need it for configuration

---

## Configuration

### Option 1: Environment Variables (Recommended)

Create a `.env` file in your project root:

```bash
# .env file
FLOW_ID="your-flow-id-here"
LANGFLOW_URL="http://localhost:7860"
NGROK_AUTH_TOKEN="your-ngrok-auth-token"
LANGFLOW_API_KEY=""  # Optional: only if your Langflow requires auth

# Voice settings
VOICE_INTRO="Hi, this is your Voxie agent. How can I help you today?"
VOICE_TYPE="Polly.Matthew"  # Options: man, woman, alice, Polly.Matthew, Polly.Joanna, etc.
```

**Get your Ngrok auth token:**
1. Sign up at https://dashboard.ngrok.com/signup
2. Go to: https://dashboard.ngrok.com/get-started/your-authtoken
3. Copy your token

### Option 2: Update Code Directly

Edit `twilio_langflow_bridge.py` lines 10-17:

```python
LANGFLOW_URL = "http://localhost:7860"
FLOW_ID = "your-flow-id-here"  # REQUIRED - paste your flow ID
NGROK_AUTH_TOKEN = "your-ngrok-token-here"  # Get from ngrok.com
```

---

## Twilio Setup

### Step 1: Create Twilio Account

1. Go to: https://www.twilio.com/try-twilio
2. **Sign up** with your email
3. **Verify your phone number** (you'll receive an SMS code)

### Step 2: Get a Phone Number (FREE on Trial)

1. Log in to **Twilio Console**: https://console.twilio.com
2. Go to: **Phone Numbers** → **Manage** → **Buy a number**
   - Or direct link: https://console.twilio.com/us1/develop/phone-numbers/manage/search
3. Select country (US numbers work best on trial)
4. Filter by: **Voice** capability
5. **Click "Buy"** on any number (uses trial credit, no charge)
6. **Confirm purchase**

You now have a Twilio phone number! Example: `+1-555-123-4567`

### Step 3: Get Twilio Credentials (Optional for Advanced)

While not required for basic setup, you can find these in your Twilio Console:
- **Account SID**: Dashboard → Account Info
- **Auth Token**: Dashboard → Account Info → Auth Token

---

## Running the Application

### Step 1: Start Langflow

Make sure Langflow is running:

```bash
langflow run --port 7860
```

Keep this terminal open.

### Step 2: Run the Bridge Server

Open a **new terminal** in your project directory:

```bash
# Set environment variables if using .env approach
export FLOW_ID="your-flow-id-here"
export NGROK_AUTH_TOKEN="your-ngrok-token"

# Run the bridge
uv run python twilio_langflow_bridge.py
```

**What happens:**
1. The script validates your configuration
2. Starts an ngrok tunnel automatically
3. Displays the **public URL** you need for Twilio
4. Starts the Flask server

**Expected output:**

```
✅ Configuration loaded:
   Langflow URL: http://localhost:7860
   Flow ID: abc-123-def-456

============================================================
🚀 Ngrok tunnel started!
📞 Public URL: https://abc123.ngrok-free.app
============================================================

⚙️  Next steps:
1. Copy the public URL above
2. Go to Twilio Console: https://console.twilio.com/...
3. Select your phone number
4. Under 'Voice Configuration' -> 'A call comes in'
5. Set webhook URL to: https://abc123.ngrok-free.app/voice
6. Set HTTP method to: POST
7. Save your changes

📱 Call your Twilio number to test!

🌐 Starting Flask server on http://0.0.0.0:5000
```

**IMPORTANT**: Copy the **Public URL** (the ngrok URL) - you'll need it in the next step!

### Step 3: Configure Twilio Webhook

1. **Go to Twilio Console**: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming

2. **Click on your phone number**

3. Scroll to **"Voice Configuration"** section

4. Under **"A call comes in"**:
   - Select: **Webhook**
   - HTTP method: **POST**
   - URL: **`https://your-ngrok-url.ngrok-free.app/voice`**
     - Replace with YOUR ngrok URL from Step 2
     - Make sure to add `/voice` at the end!

5. **Save configuration**

---

## Testing Your Agent

### Quick Test

1. **Call your Twilio number** from any phone
2. You should hear: *"Hi, this is your Voxie agent. How can I help you today?"*
3. **Speak your question**, for example:
   - "I want to book a hotel room"
   - "Tell me about your services"
   - "Help me with my order"
4. The agent will:
   - Process your speech (transcribed by Twilio)
   - Send to Langflow agent
   - Get agent response
   - Speak the response back to you
5. The agent will ask: *"Is there anything else I can help you with?"*
6. You can continue the conversation or hang up

### Test Different Agents

To test different Langflow agents:

1. **Get the Flow ID** of the agent you want to test (from Langflow UI)
2. **Stop the server** (Ctrl+C)
3. **Update FLOW_ID**:
   ```bash
   export FLOW_ID="new-flow-id-here"
   ```
4. **Restart the server**:
   ```bash
   uv run python twilio_langflow_bridge.py
   ```
5. **Call the number again** - now it uses the new agent!

### Monitor Live Calls

**In your terminal**, you'll see real-time logs:

```
Langflow API error: 500 - {...}  # If something goes wrong
Error calling Langflow: Connection timeout  # Network issues
```

**In Langflow UI**:
- Go to your flow
- Click **"Logs"** or **"Messages"** tab
- See all incoming messages and agent responses

**In Twilio Console**:
- Go to: https://console.twilio.com/us1/monitor/logs/voice
- See all call logs, durations, errors

---

## Troubleshooting

### Error: "FLOW_ID not set!"

**Solution**: You forgot to set the Flow ID.

```bash
# Set it before running
export FLOW_ID="your-actual-flow-id"
uv run python twilio_langflow_bridge.py
```

Or edit `twilio_langflow_bridge.py` line 11 directly.

---

### Error: "Could not start ngrok tunnel"

**Possible causes:**

1. **No ngrok auth token set**
   ```bash
   export NGROK_AUTH_TOKEN="your-token-from-ngrok.com"
   ```

2. **Invalid token**
   - Go to: https://dashboard.ngrok.com/get-started/your-authtoken
   - Copy the correct token

3. **Ngrok not installed**
   ```bash
   uv add ngrok
   ```

**Alternative**: Use ngrok CLI separately:
```bash
# Install ngrok CLI (optional)
brew install ngrok  # macOS
# or download from: https://ngrok.com/download

# Run separately in another terminal
ngrok http 5000

# Copy the URL and set FLOW_ID, then run bridge without ngrok integration
```

---

### Agent Not Responding / Timeout Errors

**Check Langflow:**

1. Is Langflow running?
   ```bash
   # Check if running
   curl http://localhost:7860/health
   ```

2. Test the API manually:
   ```bash
   curl -X POST http://localhost:7860/api/v1/run/YOUR_FLOW_ID \
     -H "Content-Type: application/json" \
     -d '{"input_value": "test message"}'
   ```

3. Check Flow ID is correct:
   - Open Langflow UI
   - Verify the ID in the URL matches your FLOW_ID

**Check Agent Configuration:**

1. Open your flow in Langflow
2. Make sure:
   - **ChatInput** node exists
   - **Agent** or **ChatOutput** node exists
   - All nodes are connected properly
   - OpenAI API key is set (if using GPT models)

---

### Twilio Says "We're sorry, an application error has occurred"

**Possible causes:**

1. **Webhook URL is wrong**
   - Check: Does it end with `/voice`?
   - Check: Is it the correct ngrok URL?
   - Check: Is HTTP method set to POST?

2. **Ngrok tunnel expired**
   - Free ngrok tunnels expire when you restart the server
   - Copy the NEW ngrok URL each time you restart
   - Update Twilio webhook with the new URL

3. **Server not running**
   - Check terminal: Is Flask server running?
   - Look for: "Starting Flask server on http://0.0.0.0:5000"

**Debug steps:**

1. Check Twilio error logs:
   - https://console.twilio.com/us1/monitor/logs/voice

2. Check your server logs in terminal

3. Test webhook manually:
   ```bash
   curl -X POST https://your-ngrok-url.ngrok-free.app/voice \
     -d "SpeechResult=test"
   ```

---

### Voice Sounds Bad / Speech Not Recognized

**Improve speech recognition:**

1. Edit `twilio_langflow_bridge.py` line 34:
   ```python
   speech_model='phone_call'  # Already optimized
   ```

2. Try different Twilio voices (line 17):
   ```python
   # American English voices
   VOICE_TYPE = "Polly.Matthew"  # Male
   VOICE_TYPE = "Polly.Joanna"   # Female
   VOICE_TYPE = "Polly.Joey"     # Male

   # British English
   VOICE_TYPE = "Polly.Emma"     # Female
   VOICE_TYPE = "Polly.Brian"    # Male

   # Simple options
   VOICE_TYPE = "man"    # Basic male
   VOICE_TYPE = "woman"  # Basic female
   VOICE_TYPE = "alice"  # Enhanced female
   ```

3. Adjust speech timeout (line 109):
   ```python
   speech_timeout='3',  # Seconds to wait after speech ends
   # Try: '5' for slower speakers, 'auto' for automatic
   ```

---

### "Session Expired" or Memory Issues

If your agent doesn't remember previous messages in the same call:

**Check Agent Configuration:**

1. Open your flow in Langflow
2. Click on the **Agent** node
3. Under **Memory Settings**:
   - Enable: **"Store Messages"**
   - Set **"Number of Messages"** to 10+ (line 10 messages remembered)

**Alternatively**, add a Memory node:
- Add **"Chat Memory"** component to your flow
- Connect it to your Agent node

---

### Trial Account Limitations

**Twilio Free Trial Restrictions:**

1. **Can only call/SMS verified numbers**
   - Solution: Verify your test phone numbers at:
   - https://console.twilio.com/us1/develop/phone-numbers/manage/verified

2. **Calls prefixed with "You have a call from a Twilio trial account"**
   - Solution: Upgrade to paid account (not necessary for testing)

3. **Limited to one phone number**
   - Solution: Upgrade to add more numbers

**Free tier is perfect for:**
- Testing and development
- Demos
- Small-scale deployments
- ~100+ calls with $15 credit

---

## Production Deployment

For production use (real users, 24/7 availability):

### Option 1: Deploy to Cloud (Recommended)

**Deploy Flask app to a cloud service:**

#### Render.com (Free Tier Available)

1. Create account: https://render.com
2. Create new **Web Service**
3. Connect your GitHub repo
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python twilio_langflow_bridge.py`
   - **Environment Variables**:
     ```
     FLOW_ID=your-flow-id
     LANGFLOW_URL=https://your-langflow-url
     ```
5. Deploy - you get a permanent URL like: `https://yourapp.onrender.com`
6. Update Twilio webhook to: `https://yourapp.onrender.com/voice`

#### Railway.app

Similar to Render, very easy deployment:
- https://railway.app
- Connect GitHub
- Deploy in minutes

#### Heroku

Classic option, easy to use:
- https://heroku.com
- Use free dyno for testing

### Option 2: Deploy Langflow to Cloud

If you want Langflow also in the cloud:

1. **Langflow Cloud**: https://www.langflow.org/cloud
   - Official hosted solution
   - No maintenance required

2. **DataStax Langflow**: https://www.datastax.com/products/langflow
   - Enterprise-ready
   - Built-in scaling

3. **Self-hosted on VPS**:
   - DigitalOcean, AWS, GCP, Azure
   - Run both Langflow + Flask bridge on same server

### Option 3: Use Static Ngrok URL (Paid)

**Ngrok Paid Plans** ($8-20/month):
- Static URLs that don't change
- No need to update Twilio webhook
- Good for small production uses

Upgrade at: https://dashboard.ngrok.com/billing/subscription

---

## Advanced Configuration

### Multiple Agents

To handle multiple agents on different numbers:

```python
# twilio_langflow_bridge.py - modify to use different flows

AGENT_FLOWS = {
    "+15551234567": "flow-id-for-hotel-agent",
    "+15559876543": "flow-id-for-car-agent",
}

@app.route('/voice', methods=['POST'])
def voice_webhook():
    phone_number = request.values.get('To', '')
    flow_id = AGENT_FLOWS.get(phone_number, FLOW_ID)

    # Use flow_id for this specific number
    ...
```

### Custom Greeting Per Agent

Set environment variables for different greetings:

```bash
export VOICE_INTRO="Welcome to our hotel booking service. How can I assist you?"
export VOICE_TYPE="Polly.Joanna"
```

### Session Management

To maintain conversation context across multiple calls from the same user:

```python
# Use caller's phone number as session ID
caller_number = request.values.get('From', '')

lf_payload = {
    "input_value": speech,
    "session_id": caller_number,  # Maintains history
}
```

---

## Cost Estimates

### Development/Testing (FREE)
- Twilio trial: $15 credit = ~100+ calls
- Ngrok free tier: 1 tunnel, unlimited usage
- Langflow: Free locally
- **Total: $0**

### Production (Monthly)

**Small Scale (100-500 calls/month):**
- Twilio: ~$10-50/month (depends on call duration)
- Ngrok Pro: $8/month (for static URL)
- Or Deploy Flask: Free (Render/Railway free tier)
- **Total: ~$10-50/month**

**Medium Scale (1,000+ calls/month):**
- Twilio: ~$100-500/month
- Cloud hosting (Render/Railway): $7-15/month
- Langflow Cloud: $50-200/month (optional)
- **Total: ~$150-700/month**

---

## Support & Resources

### Documentation
- **Langflow Docs**: https://docs.langflow.org
- **Twilio Voice Docs**: https://www.twilio.com/docs/voice
- **Ngrok Docs**: https://ngrok.com/docs

### Troubleshooting Checklist

Before asking for help, verify:
- [ ] Langflow is running (`http://localhost:7860` accessible)
- [ ] Flask server is running (check terminal output)
- [ ] Ngrok tunnel is active (URL shown in logs)
- [ ] Twilio webhook URL is correct (includes `/voice`)
- [ ] FLOW_ID is correct (matches Langflow URL)
- [ ] Agent flow has proper input/output nodes
- [ ] OpenAI API key is set (if using GPT models)

### Getting Help

**Twilio Issues:**
- Error logs: https://console.twilio.com/us1/monitor/logs/voice
- Support: https://support.twilio.com

**Langflow Issues:**
- GitHub: https://github.com/langflow-ai/langflow
- Discord: https://discord.gg/langflow

**This Project:**
- Check terminal logs for errors
- Test Langflow API manually with curl
- Verify Twilio webhook receives requests

---

## Quick Reference

### Start Everything

```bash
# Terminal 1: Start Langflow
langflow run --port 7860

# Terminal 2: Start Voice Bridge
export FLOW_ID="your-flow-id"
export NGROK_AUTH_TOKEN="your-token"
uv run python twilio_langflow_bridge.py
```

### Important URLs

- **Langflow UI**: http://localhost:7860
- **Twilio Console**: https://console.twilio.com
- **Ngrok Dashboard**: https://dashboard.ngrok.com
- **Twilio Phone Numbers**: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
- **Twilio Call Logs**: https://console.twilio.com/us1/monitor/logs/voice

### Files Reference

- **Bridge Server**: `twilio_langflow_bridge.py` - Main application
- **This Guide**: `TWILIO_VOICE_DEPLOYMENT_GUIDE.md`
- **Agent Flows**: `flows/` directory - Your Langflow agents
- **Main Agent**: `flows/Main Agent_*.json` - Creates other agents
- **Template**: `flows/Basic Agent Blue Print_*.json` - Template for new agents

---

## What's Next?

After successfully deploying your voice agent:

1. **Test with real users** - Get feedback on agent responses
2. **Improve prompts** - Update system prompts in Langflow for better responses
3. **Add more agents** - Create specialized agents for different use cases
4. **Monitor usage** - Check Twilio logs to see call patterns
5. **Scale up** - Deploy to cloud when ready for production
6. **Add features**:
   - SMS support (easy with same setup)
   - WhatsApp integration
   - Call recording
   - Analytics dashboard

---

**Happy Deploying!** 🚀📞

For questions specific to your setup, check the troubleshooting section or review the terminal logs for error messages.
