# Railway Deployment Guide - FIXED (Timeout Issue Solved)

This guide fixes the build timeout issue and adds better error handling.

---

## 🔧 What Was Fixed

### Problem
- ❌ Build timed out when installing Langflow
- ❌ Langflow is too large for standard pip install
- ❌ Insufficient error handling and logging

### Solution
- ✅ Use Docker deployment for Langflow (faster, more reliable)
- ✅ Use enhanced bridge with better error handling
- ✅ Add comprehensive logging and debugging

---

## 📦 New Files Created

1. **`Dockerfile.langflow`** - Docker configuration for Langflow
2. **`twilio_bridge_production.py`** - Enhanced bridge with error handling
3. **`requirements.txt`** - Already exists

---

## 🚀 DEPLOYMENT METHOD 1: Docker (Recommended)

This method uses Docker to avoid timeout issues.

### Step 1: Commit New Files

```bash
# Add new files
git add Dockerfile.langflow twilio_bridge_production.py

# Commit
git commit -m "Add Docker deployment and enhanced bridge"

# Push
git push origin main
```

### Step 2: Deploy Langflow with Docker

#### 2.1 Create Railway Project

1. Go to **https://railway.app**
2. Login with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your repository

#### 2.2 Configure Langflow Service (Docker)

**Set Docker configuration:**
1. Click "Settings" tab
2. Find "Source" section
3. **Dockerfile Path**: `Dockerfile.langflow`
4. **Docker Build Context**: `.` (root directory)

**Add Environment Variables:**
Click "Variables" tab:

```
LANGFLOW_DATABASE_URL=sqlite:///./langflow.db
LANGFLOW_AUTO_LOGIN=false
LANGFLOW_SUPERUSER=admin
LANGFLOW_SUPERUSER_PASSWORD=admin123
PORT=7860
```

**Deploy:**
1. Railway automatically builds Docker image
2. Wait 5-7 minutes (Docker is faster than pip install)
3. Check "Deployments" → Should show "Success"

#### 2.3 Get Langflow URL

1. Settings → Networking → "Generate Domain"
2. Copy URL: `https://langflow-production-xxxx.up.railway.app`
3. Test in browser → Login with admin/admin123

✅ **Langflow deployed!**

### Step 3: Deploy Bridge Service

#### 3.1 Create Second Service

1. Railway dashboard → Click "New"
2. "GitHub Repo" → Select same repository
3. Railway creates second service

#### 3.2 Configure Bridge

**Set Build & Start Commands:**
1. Settings → Deploy
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `gunicorn twilio_bridge_production:app`

**Add Environment Variables:**
```
LANGFLOW_URL=https://langflow-production-xxxx.up.railway.app
DEFAULT_FLOW_ID=9c7c075b-85da-4dfd-ae0c-bcb322851b04
LANGFLOW_API_KEY=sk-SlAQGa_sWQnLcJHEHW2WLIFkv17xjpGLdj3EhRV5bmY
DEFAULT_VOICE_INTRO=Hi, this is your Voxie agent. How can I help you today?
DEFAULT_VOICE_TYPE=Polly.Matthew
AGENT_MAPPINGS={}
DEBUG_MODE=true
PORT=5000
```

**Important:**
- Replace `LANGFLOW_URL` with YOUR Langflow URL!
- Set `DEBUG_MODE=true` for better logs during testing

#### 3.3 Deploy

1. Click "Deploy"
2. Wait 2-3 minutes
3. Generate domain: `https://bridge-production-xxxx.up.railway.app`

✅ **Bridge deployed!**

---

## 🚀 DEPLOYMENT METHOD 2: Official Langflow Image (Alternative)

If Docker build still times out, use Langflow's official image.

### Step 1: Deploy Langflow from Official Image

#### 1.1 In Railway

1. Click "New Project"
2. Select **"Empty Project"**
3. Click "Deploy"

#### 1.2 Configure

1. Settings → Service Settings
2. **Source**: Select "Docker Image"
3. **Image**: `langflowai/langflow:latest`

**Add Environment Variables:**
```
LANGFLOW_DATABASE_URL=sqlite:///./langflow.db
LANGFLOW_AUTO_LOGIN=false
LANGFLOW_SUPERUSER=admin
LANGFLOW_SUPERUSER_PASSWORD=admin123
PORT=7860
```

#### 1.3 Start Command

Settings → Deploy → **Start Command**:
```
langflow run --host 0.0.0.0 --port $PORT
```

#### 1.4 Deploy

1. Railway pulls official image (very fast!)
2. Starts in 1-2 minutes
3. Generate domain and test

### Step 2: Import Your Flows

Since this uses official image without your flows:

1. Open Langflow UI
2. Login with admin/admin123
3. Click "Import" → Select your flow JSON files from `flows/` folder
4. Import all agents

### Step 3: Deploy Bridge

Follow same steps as Method 1, Step 3.

---

## 🧪 Testing & Debugging

### Test Health Endpoint

```bash
# Bridge health
curl https://your-bridge.railway.app/health

# Should return detailed status:
{
  "status": "healthy",
  "langflow_status": "connected",  # ← Check this!
  "mode": "single-agent",
  "debug_mode": true
}
```

### Test Agent Listing

```bash
curl https://your-bridge.railway.app/agents
```

### View Debug Info (if DEBUG_MODE=true)

```bash
curl https://your-bridge.railway.app/debug

# Shows all environment variables and configuration
```

### Check Logs

**Railway Logs:**
1. Dashboard → Select service → Deployments
2. Click latest deployment
3. See real-time logs

**Look for these indicators:**

✅ Good logs:
```
✅ Multi-agent mode: 0 agents configured
✅ Single-agent mode: Using default agent
📞 CALL [CAxxxx] From: +1234 To: +1472...
🤖 CALL [CAxxxx] Using Flow: 9c7c075b...
💬 CALL [CAxxxx] User said: I want to book a hotel
✅ CALL [CAxxxx] Agent replied successfully
```

❌ Error logs:
```
❌ Authentication failed - Invalid API key
❌ Flow not found: 9c7c075b...
❌ Connection error: Connection refused
⏱️  Request timeout
```

---

## 🔗 Configure Twilio

Same as before:

1. https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Click your number
3. Webhook: `https://your-bridge.railway.app/voice`
4. Method: **POST**
5. Save

---

## 🐛 Enhanced Error Handling Features

### 1. Detailed Logging

Every call is logged with:
- Call SID (unique identifier)
- Caller and called numbers
- Which agent/flow is used
- User's speech input
- Agent's response
- Any errors that occur

### 2. Multiple Response Extraction Strategies

The bridge tries 4 different ways to extract agent response:
- Strategy 1: Nested outputs structure
- Strategy 2: Simple outputs structure
- Strategy 3: Direct text field
- Strategy 4: Messages array

If one fails, it tries the next!

### 3. Specific Error Messages

Different errors give different voice responses:
- **Authentication error**: "I'm having authentication issues"
- **Flow not found**: "The agent you're trying to reach is not available"
- **Timeout**: "I'm taking too long to respond"
- **Connection error**: "I'm having trouble connecting"

### 4. Langflow Connectivity Check

Health endpoint checks if Langflow is reachable:
```json
{
  "langflow_status": "connected"  // or "disconnected: reason"
}
```

### 5. Debug Mode

Set `DEBUG_MODE=true` to get:
- Extra detailed logs
- `/debug` endpoint with full configuration
- Response data logging

**Turn off in production:** Set `DEBUG_MODE=false`

---

## 📊 Comparison: Old vs New Bridge

| Feature | Old (`twilio_bridge_dynamic.py`) | New (`twilio_bridge_production.py`) |
|---------|----------------------------------|-------------------------------------|
| Error Handling | Basic try/catch | Comprehensive with specific errors |
| Logging | Minimal print statements | Structured logging with levels |
| Status Codes | Generic errors | Specific HTTP status handling |
| Debug Info | None | Full debug endpoint |
| Health Check | Basic | Detailed with Langflow connectivity |
| Response Extraction | 3 strategies | 4 strategies with fallbacks |
| Call Tracking | None | Every call logged with Call SID |
| User Feedback | Generic errors | Specific error messages |

---

## ⚠️ Troubleshooting Guide

### Issue: "Build timed out"

**Solutions:**
1. ✅ Use Method 1 (Docker) - faster than pip install
2. ✅ Use Method 2 (Official image) - fastest
3. ✅ Don't use pip install langflow directly

### Issue: "langflow_status: disconnected"

**Check:**
```bash
curl https://your-langflow.railway.app/health
```

**Solutions:**
- Verify Langflow service is running in Railway
- Check `LANGFLOW_URL` environment variable is correct
- Make sure URL has no trailing slash

### Issue: "Flow not found"

**Check logs for:**
```
❌ Flow not found: 9c7c075b...
```

**Solutions:**
- Verify Flow ID is correct
- Open Langflow UI and check flow exists
- Copy Flow ID from browser URL
- Update `DEFAULT_FLOW_ID` environment variable

### Issue: "Authentication failed"

**Check logs for:**
```
❌ Authentication failed - Invalid API key
```

**Solutions:**
- Get new API key from Langflow UI
- Update `LANGFLOW_API_KEY` environment variable
- Or set `LANGFLOW_AUTO_LOGIN=true` in Langflow service

### Issue: Agent responds but says "technical issue"

**Check:**
- Bridge logs for exact error
- Langflow logs for processing errors
- Flow configuration in Langflow UI
- Try testing flow directly in Langflow

---

## 🎯 Quick Debugging Checklist

When something doesn't work:

- [ ] Check Railway deployments - both services showing "Success"?
- [ ] Test Langflow URL in browser - loads UI?
- [ ] Login to Langflow - see your flows?
- [ ] Test `/health` endpoint - shows "connected"?
- [ ] Check bridge logs - any error messages?
- [ ] Test `/agents` endpoint - shows correct config?
- [ ] Verify Twilio webhook URL - correct and has `/voice`?
- [ ] Check Twilio logs - calls reaching webhook?
- [ ] Is DEBUG_MODE=true for detailed logs?

---

## 💰 Cost

**Railway (both services):**
- Free tier: $5/month credit
- Docker deployment uses slightly more resources
- Estimate: ~$3-5/month for both services
- **Should fit in free tier for testing!**

**Twilio:**
- Free trial: $15 credit
- ~100+ test calls

---

## 🎉 Success Indicators

Your deployment is working when:

✅ Both services show "Success" in Railway
✅ Langflow UI loads and you can login
✅ `/health` shows `langflow_status: connected`
✅ Test call plays greeting
✅ Agent responds to your question
✅ Logs show successful call flow
✅ No error messages in logs

---

## 📝 Next Steps After Successful Deployment

1. **Test thoroughly** - Make multiple test calls
2. **Review logs** - Understand the call flow
3. **Tune agent** - Improve prompts in Langflow
4. **Turn off debug** - Set `DEBUG_MODE=false` for production
5. **Monitor usage** - Check Railway usage in dashboard
6. **Plan scaling** - When ready, upgrade Railway plan

---

## 🔄 Switching Bridges

Currently you have two bridge files:

- `twilio_bridge_dynamic.py` - Original, basic
- `twilio_bridge_production.py` - New, enhanced

**Which to use?**

- **For production:** `twilio_bridge_production.py` (better errors, logging)
- **For testing/simple:** `twilio_bridge_dynamic.py` (simpler code)

**To switch:** Just change the start command in Railway:
```
# Production
gunicorn twilio_bridge_production:app

# Dynamic (original)
gunicorn twilio_bridge_dynamic:app
```

---

**Deployment should now succeed! 🚀**

Follow Method 1 (Docker) or Method 2 (Official Image) to avoid timeout issues.
