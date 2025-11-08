# Railway Deployment Guide - Static Single Agent

Complete guide to deploy your Twilio Voice Bridge and Langflow to Railway (both services).

---

## 📋 What You're Deploying

- **Service 1:** Langflow (AI agent platform)
- **Service 2:** Twilio Bridge (connects calls to agents)
- **Result:** Single hotel booking agent accessible via Twilio phone number

---

## 📦 Files You Need

✅ Already created:
- `twilio_bridge_dynamic.py` - The bridge code (works as static single agent now)
- `requirements.txt` - Python dependencies

---

## 🚀 Step 1: Commit to GitHub

```bash
# Add files to git
git add requirements.txt twilio_bridge_dynamic.py

# Commit
git commit -m "Add Railway deployment files"

# Push to GitHub
git push origin main
```

---

## 🌐 Step 2: Deploy Langflow to Railway

### 2.1 Create Railway Account

1. Go to: **https://railway.app**
2. Click "Login" → "Login with GitHub"
3. Authorize Railway
4. You get **$5 free credit/month** (no card needed)

### 2.2 Create Langflow Service

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: `Voxhive/langflow`
4. Railway creates the service

### 2.3 Configure Langflow

**Set Build & Start Commands:**
1. Click "Settings" tab
2. Scroll to "Deploy" section
3. **Build Command:**
   ```
   pip install langflow
   ```
4. **Start Command:**
   ```
   langflow run --host 0.0.0.0 --port $PORT
   ```

**Add Environment Variables:**
1. Click "Variables" tab
2. Click "New Variable"
3. Add these variables one by one:

```
LANGFLOW_DATABASE_URL=sqlite:///./langflow.db
LANGFLOW_AUTO_LOGIN=false
LANGFLOW_SUPERUSER=admin
LANGFLOW_SUPERUSER_PASSWORD=admin123
PORT=7860
```

### 2.4 Deploy

1. Click "Deploy" (or deployment starts automatically)
2. Wait 3-5 minutes
3. Check "Deployments" tab - should show "Success"

### 2.5 Get Langflow URL

1. Click "Settings" tab
2. Scroll to "Networking" section
3. Click **"Generate Domain"**
4. Railway creates URL like: `https://langflow-production-xxxx.up.railway.app`
5. **Copy this URL** - you'll need it!

### 2.6 Test Langflow

1. Open the URL in browser
2. You should see Langflow login page
3. Login:
   - Username: `admin`
   - Password: `admin123`
4. You should see your flows/agents

✅ **Langflow deployed successfully!**

---

## 🔗 Step 3: Deploy Twilio Bridge to Railway

### 3.1 Create Bridge Service

1. In Railway dashboard, click **"New"** button (top right)
2. Select **"GitHub Repo"**
3. Choose **SAME repository** again: `Voxhive/langflow`
4. Railway creates a second service

### 3.2 Configure Bridge

**Set Build & Start Commands:**
1. Click "Settings" tab
2. Scroll to "Deploy" section
3. **Build Command:**
   ```
   pip install -r requirements.txt
   ```
4. **Start Command:**
   ```
   gunicorn twilio_bridge_dynamic:app
   ```

**Add Environment Variables:**
1. Click "Variables" tab
2. Add these variables:

```
LANGFLOW_URL=https://langflow-production-xxxx.up.railway.app
DEFAULT_FLOW_ID=9c7c075b-85da-4dfd-ae0c-bcb322851b04
LANGFLOW_API_KEY=sk-SlAQGa_sWQnLcJHEHW2WLIFkv17xjpGLdj3EhRV5bmY
DEFAULT_VOICE_INTRO=Hi, this is your Voxie agent. How can I help you today?
DEFAULT_VOICE_TYPE=Polly.Matthew
AGENT_MAPPINGS={}
PORT=5000
```

**⚠️ IMPORTANT:** Replace `LANGFLOW_URL` with YOUR actual Langflow URL from Step 2.5!

### 3.3 Deploy

1. Click "Deploy" (or starts automatically)
2. Wait 2-3 minutes
3. Check "Deployments" tab - should show "Success"

### 3.4 Get Bridge URL

1. Click "Settings" tab
2. Scroll to "Networking"
3. Click **"Generate Domain"**
4. Railway creates URL like: `https://twilio-bridge-production-xxxx.up.railway.app`
5. **Copy this URL** - you'll need it for Twilio!

### 3.5 Test Bridge

```bash
# Test health endpoint
curl https://your-bridge-url.up.railway.app/health

# Should return:
{
  "status": "healthy",
  "default_flow_id": "9c7c075b-85da-4dfd-ae0c-bcb322851b04",
  "mode": "single-agent",
  "agents_mapped": 0,
  "langflow_url": "https://your-langflow-url.up.railway.app"
}
```

✅ **Bridge deployed successfully!**

---

## 📞 Step 4: Configure Twilio

### 4.1 Update Webhook

1. Go to: **https://console.twilio.com/us1/develop/phone-numbers/manage/incoming**
2. Click your phone number: **(472) 230-2360**
3. Scroll to **"Voice Configuration"** section
4. Under **"A call comes in"**:
   - Select: **Webhook**
   - URL: `https://your-bridge-url.up.railway.app/voice`
   - HTTP Method: **POST**
5. **Click "Save Configuration"**

✅ **Twilio configured!**

---

## 🧪 Step 5: Test Everything

### Test 1: Call from Verified Number

1. **Call your Twilio number** from a verified phone
2. You should hear: "Hi, this is your Voxie agent. How can I help you today?"
3. **Speak:** "I want to book a hotel room"
4. Agent should respond intelligently
5. Continue conversation

### Test 2: Check Logs

**Railway Logs:**
1. Go to Railway dashboard
2. Click Bridge service
3. Click "Deployments" → Click latest deployment
4. See live logs showing calls

**Twilio Logs:**
1. Go to: https://console.twilio.com/us1/monitor/logs/voice
2. See call records with duration, status

---

## ✅ Deployment Complete!

Your system is now live:

```
Phone Call → Twilio → Railway Bridge → Railway Langflow → AI Response
```

**Your URLs:**
- Langflow UI: `https://langflow-production-xxxx.up.railway.app`
- Bridge API: `https://twilio-bridge-production-xxxx.up.railway.app`
- Twilio Number: `(472) 230-2360`

---

## 💰 Cost

**Railway Free Tier:**
- $5 credit/month
- Covers both services for testing/demos
- No credit card required initially

**Twilio:**
- Free trial: $15 credit
- After trial: ~$0.01-0.04 per minute

**Total for testing:** **$0** (using free credits)

---

## 🔧 Managing Deployment

### View Logs
- Railway Dashboard → Select Service → Deployments → Click deployment
- See real-time logs

### Update Code
```bash
git add .
git commit -m "Update code"
git push origin main
# Railway auto-deploys!
```

### Update Environment Variables
- Railway Dashboard → Select Service → Variables → Edit
- Service auto-restarts

### Restart Service
- Railway Dashboard → Select Service → Settings → Restart

---

## 🐛 Troubleshooting

### Bridge can't connect to Langflow
- Check `LANGFLOW_URL` is correct in Bridge variables
- Test Langflow URL in browser - should open Langflow UI
- Check Langflow service is running in Railway dashboard

### Twilio says "Application Error"
- Check Bridge service is running
- Verify webhook URL ends with `/voice`
- Check Bridge logs for errors
- Test: `curl https://your-bridge-url.up.railway.app/health`

### Agent not responding correctly
- Check `DEFAULT_FLOW_ID` matches your Langflow flow
- Check `LANGFLOW_API_KEY` is correct
- Test Langflow directly in UI with same query

---

## 📚 Useful Endpoints

```bash
# Health check
curl https://your-bridge-url.up.railway.app/health

# List agents
curl https://your-bridge-url.up.railway.app/agents

# Test voice endpoint
curl -X POST https://your-bridge-url.up.railway.app/voice \
  -d "SpeechResult=Hello test"
```

---

## 🎯 Next Steps

- ✅ System is deployed and working as single static agent
- ✅ One Twilio number routes to one hotel agent
- ✅ Ready for production testing

**When ready for multiple agents:** See `MIGRATION_TO_DYNAMIC.md`

---

**Deployment complete! 🚀**
