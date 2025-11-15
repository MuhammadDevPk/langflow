# Deploy Bridge to Render (Langflow runs locally with Ngrok)

Simple guide to deploy the Twilio bridge to Render while keeping Langflow local.

---

## 🎯 What We're Deploying

**Render (Cloud):**
- `twilio_bridge_production.py` - Handles Twilio calls

**Your Computer (Local):**
- Langflow - Processes agent requests
- Ngrok - Exposes Langflow to internet

---

## 📋 Prerequisites

- ✅ Langflow running locally
- ✅ Ngrok running and exposing Langflow
- ✅ GitHub account
- ✅ Code pushed to GitHub

---

## 🚀 Deployment Steps

### Step 1: Sign Up for Render

1. Go to **https://render.com**
2. Click **"Get Started"**
3. Sign up with **GitHub** (easiest)
4. Authorize Render to access your repositories

**Free tier:** 750 hours/month (enough for testing!)

---

### Step 2: Create New Web Service

1. Click **"New +"** (top right)
2. Select **"Web Service"**
3. Click **"Connect a repository"**
4. Find and select: **`MuhammadDevPk/langflow`**
5. Click **"Connect"**

---

### Step 3: Configure Service

Render shows a configuration page. Fill in:

#### Basic Settings:

**Name:**
```
twilio-langflow-bridge
```

**Region:**
```
Oregon (US West) or Singapore
```

**Branch:**
```
main
```

**Root Directory:**
```
(leave empty)
```

**Runtime:**
```
Python 3
```

#### Build Settings:

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
gunicorn twilio_bridge_production:app
```

#### Instance Type:

**Select:** Free (512 MB RAM, shared CPU)

---

### Step 4: Add Environment Variables

Scroll down to **"Environment Variables"** section.

Click **"Add Environment Variable"** and add these:

```
Key: LANGFLOW_URL
Value: https://your-ngrok-url.ngrok-free.app
```

```
Key: DEFAULT_FLOW_ID
Value: 9c7c075b-85da-4dfd-ae0c-bcb322851b04
```

```
Key: LANGFLOW_API_KEY
Value: sk-SlAQGa_sWQnLcJHEHW2WLIFkv17xjpGLdj3EhRV5bmY
```

```
Key: DEFAULT_VOICE_INTRO
Value: Hi, this is your Voxie agent. How can I help you today?
```

```
Key: DEFAULT_VOICE_TYPE
Value: Polly.Matthew
```

```
Key: AGENT_MAPPINGS
Value: {}
```

```
Key: DEBUG_MODE
Value: true
```

```
Key: PORT
Value: 5000
```

**Important:** Replace `LANGFLOW_URL` value with YOUR actual ngrok URL!

---

### Step 5: Deploy

1. Click **"Create Web Service"** button (bottom)
2. Render starts deploying
3. Watch the logs in real-time
4. Wait 2-3 minutes

**Expected logs:**
```
Building...
Installing requirements...
Successfully installed flask, twilio, requests, gunicorn
Deploy succeeded!
```

**Your service URL:**
```
https://twilio-langflow-bridge.onrender.com
```

Copy this URL!

---

### Step 6: Configure Twilio

1. Go to: **https://console.twilio.com/us1/develop/phone-numbers/manage/incoming**
2. Click your phone number: **(472) 230-2360**
3. Scroll to **"Voice Configuration"**
4. Under **"A call comes in":**
   - Select: **Webhook**
   - URL: `https://twilio-langflow-bridge.onrender.com/voice`
   - HTTP Method: **POST**
5. Click **"Save Configuration"**

---

### Step 7: Test!

**Make a test call:**
1. Call your Twilio number from a verified phone
2. You should hear: "Hi, this is your Voxie agent..."
3. Speak your question
4. Agent should respond intelligently!

---

## 🔍 Testing Endpoints

**Health Check:**
```bash
curl https://twilio-langflow-bridge.onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "langflow_status": "connected",
  "mode": "single-agent"
}
```

**List Agents:**
```bash
curl https://twilio-langflow-bridge.onrender.com/agents
```

**Simulate Call:**
```bash
curl -X POST https://twilio-langflow-bridge.onrender.com/voice \
  -d "SpeechResult=test message"
```

---

## 🔧 Managing Your Deployment

### View Logs

1. Render Dashboard → Select your service
2. Click **"Logs"** tab
3. See real-time logs

**Look for:**
- ✅ `✅ Single-agent mode: Using default agent`
- ✅ `📞 CALL [CAxxxx] From: +1234...`
- ✅ `✅ Agent replied successfully`
- ❌ `❌ Connection error` (check ngrok!)

### Update Environment Variable

1. Dashboard → Your service
2. Click **"Environment"** (left sidebar)
3. Click variable to edit
4. Update value
5. Service auto-redeploys (~1 minute)

**When to update LANGFLOW_URL:**
- Every time you restart ngrok (free tier)
- Ngrok URL changes on restart
- Just copy new URL and update!

### Redeploy

1. Dashboard → Your service
2. Click **"Manual Deploy"** → **"Deploy latest commit"**

**Or** push to GitHub - Render auto-deploys!

---

## 🖥️ Local Setup (Keep Running)

### Terminal 1 - Start Langflow:
```bash
cd "/Users/muhammad/Personal/Projects/Personal Projects/pawel/Voxhive/langflow"
uv run langflow run --port 7860
```

Keep this running!

### Terminal 2 - Start Ngrok:
```bash
ngrok http 7860
```

**Copy the URL:**
```
Forwarding: https://abc-123-def.ngrok-free.app
```

**Update Render:**
1. Render Dashboard → Environment
2. Update `LANGFLOW_URL` with new ngrok URL
3. Wait 1 minute for redeploy

Keep this running!

---

## ⚠️ Important Notes

### Free Tier Limitations

**Render Free Tier:**
- ✅ 750 hours/month (enough for 24/7 testing!)
- ✅ Shared CPU (slower but works)
- ✅ 512 MB RAM (enough for bridge)
- ⚠️ Service sleeps after 15 min inactivity
- ⚠️ First call after sleep takes ~30 seconds to wake up

**Ngrok Free Tier:**
- ⚠️ URL changes when you restart
- ⚠️ Must update Render env variable after restart
- ✅ Unlimited usage

**Twilio Free Trial:**
- ✅ $15 credit (~100+ calls)
- ⚠️ Can only call verified numbers
- ⚠️ Cannot call from Pakistan to US number

### Service Sleep (Free Tier)

Render free tier sleeps after 15 min inactivity.

**What happens:**
1. No calls for 15 minutes
2. Service goes to sleep
3. Next call wakes it up (~30 seconds)
4. Caller hears silence for 30 sec, then greeting

**Solutions:**
- Upgrade to paid plan ($7/month - never sleeps)
- Or accept the 30-second wake time

---

## 🐛 Troubleshooting

### "Application failed to respond"

**Check:**
1. Is Langflow running locally?
2. Is ngrok running?
3. Is `LANGFLOW_URL` correct in Render?

**Test:**
```bash
curl https://your-ngrok-url.ngrok-free.app/health
```

Should return: `{"status": "ok"}`

### "langflow_status: disconnected"

**Problem:** Render can't reach Langflow

**Fix:**
1. Check ngrok is running
2. Copy ngrok URL
3. Update `LANGFLOW_URL` in Render
4. Wait 1 minute for redeploy

### Agent not responding

**Check Render logs:**
- Look for error messages
- Look for ❌ symbols

**Check Langflow logs:**
- Is Langflow processing requests?
- Any errors in terminal?

### Twilio says "error"

**Check Twilio webhook:**
- Is URL correct?
- Does it end with `/voice`?
- Is method POST?

**Test webhook:**
```bash
curl -X POST https://your-bridge.onrender.com/voice
```

Should return TwiML XML.

---

## 💰 Cost Breakdown

**Development/Testing (100% FREE):**
- ✅ Render: 750 hours/month free
- ✅ Ngrok: Unlimited free
- ✅ Langflow: Free locally
- ✅ Twilio: $15 trial credit

**Total: $0**

**Production (Optional Upgrades):**
- Render paid: $7/month (no sleep, faster)
- Ngrok paid: $8/month (static URL)
- Twilio: Pay per call (~$0.02/min)

---

## 🎯 Complete System

```
📱 Phone Call
    ↓
☁️ Twilio (receives call)
    ↓
☁️ Render (your bridge - always online)
    ↓
🌐 Ngrok (tunnel to your computer)
    ↓
💻 Langflow (your computer - processes request)
    ↓
🤖 AI Agent (generates response)
    ↓
← Response flows back up
    ↓
📱 Caller hears agent voice
```

---

## ✅ Success Checklist

- [ ] Render service deployed successfully
- [ ] Health check returns "connected"
- [ ] Langflow running locally
- [ ] Ngrok running and URL copied
- [ ] LANGFLOW_URL updated in Render
- [ ] Twilio webhook configured
- [ ] Test call works
- [ ] Agent responds intelligently

---

## 🔄 Daily Workflow

**Each day when you want to test:**

1. **Start Langflow:**
   ```bash
   uv run langflow run --port 7860
   ```

2. **Start Ngrok:**
   ```bash
   ngrok http 7860
   ```

3. **Update Render:**
   - Copy new ngrok URL
   - Update LANGFLOW_URL in Render
   - Wait 1 minute

4. **Test call!**

**That's it!** Render bridge stays running 24/7.

---

## 🚀 Next Steps

### For Demo/Testing:
- ✅ Current setup is perfect!
- ✅ Free tier covers everything
- ✅ Test with your boss

### For Production Later:

**Option 1 - Upgrade Ngrok ($8/month):**
- Get static URL (never changes)
- No need to update Render
- Simplest upgrade

**Option 2 - Deploy Langflow to Cloud:**
- Use Langflow Cloud (hosted)
- Or deploy to Render/Railway
- No local computer needed

**Option 3 - Upgrade Render ($7/month):**
- No sleep time
- Faster response
- Better for production

---

## 📞 Support

**Render Docs:** https://render.com/docs
**Twilio Docs:** https://www.twilio.com/docs/voice
**Ngrok Docs:** https://ngrok.com/docs

**Check Logs First:**
- Render: Dashboard → Logs
- Langflow: Terminal output
- Twilio: https://console.twilio.com/us1/monitor/logs/voice

---

**Deployment complete!** 🎉

Your bridge is live on Render, Langflow runs locally, and you can make calls!
