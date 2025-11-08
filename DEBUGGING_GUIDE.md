# Quick Debugging Guide

Fast reference for troubleshooting your deployment.

---

## 🔍 Quick Health Check Commands

```bash
# Check if services are alive
curl https://your-bridge.railway.app/
curl https://your-langflow.railway.app/health

# Detailed bridge health
curl https://your-bridge.railway.app/health

# List configured agents
curl https://your-bridge.railway.app/agents

# Debug info (if DEBUG_MODE=true)
curl https://your-bridge.railway.app/debug
```

---

## 📊 Reading Health Check Output

### ✅ Healthy Bridge
```json
{
  "status": "healthy",
  "langflow_status": "connected",  ← GOOD!
  "mode": "single-agent",
  "agents_mapped": 0,
  "debug_mode": true
}
```

### ❌ Unhealthy Bridge
```json
{
  "status": "healthy",
  "langflow_status": "disconnected: Connection refused",  ← BAD!
  ...
}
```

**Fix:** Check Langflow URL in environment variables

---

## 🔥 Common Error Messages & Fixes

### 1. "Build timed out"

**Cause:** Langflow installation takes too long

**Fix:**
- Use Docker deployment (`Dockerfile.langflow`)
- OR use official Langflow image
- See `RAILWAY_DEPLOYMENT_FIXED.md` Method 1 or 2

### 2. "langflow_status: disconnected"

**Cause:** Bridge can't reach Langflow

**Check:**
```bash
# Test Langflow directly
curl https://your-langflow-url.railway.app/health
```

**Fix:**
- Verify Langflow service is running
- Check `LANGFLOW_URL` environment variable
- Remove trailing slash from URL
- Ensure both services are in same Railway project

### 3. "Authentication failed - Invalid API key"

**Cause:** Wrong or missing API key

**Fix:**
1. Open Langflow UI
2. Go to Settings → API Keys
3. Create new key
4. Update `LANGFLOW_API_KEY` in Bridge environment variables

**OR** disable auth in Langflow:
```
LANGFLOW_AUTO_LOGIN=true
```

### 4. "Flow not found"

**Cause:** Flow ID doesn't exist or is wrong

**Fix:**
1. Open Langflow UI
2. Open your agent flow
3. Check URL: `https://.../flow/FLOW-ID-HERE`
4. Copy correct Flow ID
5. Update `DEFAULT_FLOW_ID` in Bridge environment variables

### 5. "I'm having trouble thinking right now"

**Cause:** Agent errors or timeout

**Check Railway logs:**
```
Bridge service → Deployments → Click deployment → View logs
```

**Look for:**
- `⏱️ Request timeout` - Increase timeout in code
- `❌ API error 500` - Check Langflow logs
- `💥 Unexpected error` - See full error in logs

### 6. Twilio says "Application error has occurred"

**Cause:** Webhook not reachable or returning error

**Fix:**
1. Verify webhook URL is correct
2. Check it ends with `/voice`
3. Check Bridge service is running
4. Test webhook manually:
```bash
curl -X POST https://your-bridge.railway.app/voice
```

---

## 📝 Log Patterns to Look For

### ✅ Good Logs (Everything Working)

```
✅ Single-agent mode: Using default agent
📞 CALL [CAxxxx] From: +12345 To: +14722...
🤖 CALL [CAxxxx] Using Flow: 9c7c075b...
💬 CALL [CAxxxx] User said: I want to book hotel
🔄 Calling Langflow API: http://...
📡 Langflow API status: 200
✅ Agent replied: Great! I'd be happy...
📤 CALL [CAxxxx] Response sent
```

### ❌ Bad Logs (Errors)

```
❌ Error parsing AGENT_MAPPINGS: JSON decode error
❌ Authentication failed - Invalid API key
❌ Flow not found: 9c7c075b...
🔌 Connection error: Connection refused
⏱️ Request timeout
💥 Unexpected error: ...
```

---

## 🧪 Testing Endpoints

### Test 1: Root endpoint
```bash
curl https://your-bridge.railway.app/

# Expected:
{
  "status": "running",
  "service": "Twilio-Langflow Bridge",
  "mode": "single-agent"
}
```

### Test 2: Health check
```bash
curl https://your-bridge.railway.app/health

# Check: langflow_status should be "connected"
```

### Test 3: List agents
```bash
curl https://your-bridge.railway.app/agents

# Shows all configured agents
```

### Test 4: Voice endpoint (simulate call)
```bash
curl -X POST https://your-bridge.railway.app/voice

# Should return TwiML XML with greeting
```

### Test 5: Voice with speech (simulate conversation)
```bash
curl -X POST https://your-bridge.railway.app/voice \
  -d "SpeechResult=I want to book a hotel" \
  -H "Content-Type: application/x-www-form-urlencoded"

# Should return TwiML XML with agent response
```

---

## 🔍 Where to Find Logs

### Railway Logs

1. Go to Railway dashboard
2. Click service (Bridge or Langflow)
3. Click "Deployments" tab
4. Click latest deployment
5. See live logs

**Tip:** Keep this open in a tab while testing!

### Twilio Logs

1. Go to: https://console.twilio.com/us1/monitor/logs/voice
2. See all calls with:
   - Duration
   - Status (completed, failed, etc.)
   - Error messages (if any)

---

## 🎯 Debugging Workflow

**When something doesn't work:**

1. **Check Railway Dashboard**
   - Are both services showing green (deployed)?
   - Any deployment errors?

2. **Test Langflow**
   ```bash
   curl https://your-langflow.railway.app/health
   ```
   - Should return `{"status": "ok"}`

3. **Test Bridge Health**
   ```bash
   curl https://your-bridge.railway.app/health
   ```
   - Check `langflow_status`
   - Should be "connected"

4. **Check Environment Variables**
   - Railway → Bridge service → Variables
   - Verify all are set correctly
   - Especially `LANGFLOW_URL` and `DEFAULT_FLOW_ID`

5. **Review Logs**
   - Bridge logs for errors
   - Look for emoji indicators (❌, ✅, 🔌, ⏱️, etc.)

6. **Test Voice Endpoint**
   ```bash
   curl -X POST https://your-bridge.railway.app/voice \
     -d "SpeechResult=test"
   ```
   - Should return TwiML XML

7. **Make Test Call**
   - Call Twilio number
   - Watch Railway logs in real-time
   - See the call flow

8. **If Still Broken**
   - Enable DEBUG_MODE=true
   - Check `/debug` endpoint
   - Share logs for help

---

## 🚨 Emergency Fixes

### Quick Restart

**Railway Dashboard:**
1. Select service
2. Settings → Scroll down
3. Click "Restart"

### Rollback to Previous Version

**Railway Dashboard:**
1. Select service
2. Deployments tab
3. Click previous successful deployment
4. Click "Redeploy"

### Change Environment Variable Quickly

**Railway Dashboard:**
1. Select service
2. Variables tab
3. Click variable to edit
4. Press Enter to save
5. Service auto-restarts (takes ~10 seconds)

---

## 📞 Debug a Live Call

**While on call with Twilio:**

1. **Keep Railway logs open** (Bridge service)
2. **Make the call**
3. **Watch logs in real-time:**

```
📞 CALL [CAxxxx] From: +1234... To: +1472...
🤖 CALL [CAxxxx] Using Flow: 9c7c075b...
🎙️ CALL [CAxxxx] Sending initial greeting
💬 CALL [CAxxxx] User said: <your speech>
🔄 Calling Langflow API: ...
📡 Langflow API status: 200
✅ CALL [CAxxxx] Agent replied successfully
📤 CALL [CAxxxx] Response sent
```

If you see ❌ anywhere, that's the problem!

---

## 🔧 Environment Variables Checklist

### Bridge Service - Required Variables

- [ ] `LANGFLOW_URL` - Your Langflow Railway URL (no trailing slash)
- [ ] `DEFAULT_FLOW_ID` - Your agent's flow ID from Langflow
- [ ] `LANGFLOW_API_KEY` - API key from Langflow (or empty if auth disabled)
- [ ] `PORT` - Set to 5000
- [ ] `AGENT_MAPPINGS` - Set to `{}` for single agent

### Bridge Service - Optional Variables

- [ ] `DEFAULT_VOICE_INTRO` - Custom greeting
- [ ] `DEFAULT_VOICE_TYPE` - Voice type (Polly.Matthew, etc.)
- [ ] `DEBUG_MODE` - Set to `true` for detailed logs

### Langflow Service - Required Variables

- [ ] `PORT` - Set to 7860
- [ ] `LANGFLOW_DATABASE_URL` - `sqlite:///./langflow.db`
- [ ] `LANGFLOW_AUTO_LOGIN` - `false` or `true`
- [ ] `LANGFLOW_SUPERUSER` - `admin`
- [ ] `LANGFLOW_SUPERUSER_PASSWORD` - Your password

---

## 💡 Pro Tips

### 1. Always Use DEBUG_MODE During Setup

```
DEBUG_MODE=true
```

See detailed logs for every step. Turn off for production.

### 2. Test Incrementally

Don't test everything at once:
1. ✅ Deploy Langflow → Test UI
2. ✅ Deploy Bridge → Test `/health`
3. ✅ Configure Twilio → Test call

### 3. Keep Logs Open

Keep Railway logs open in browser while testing. See issues immediately.

### 4. Use Call SID for Tracking

Every call has unique Call SID (starts with CA). Use it to track specific calls in logs:

```bash
# Search logs for specific call
# Look for: CALL [CAxxxx]
```

### 5. Save Working Configuration

Once it works, document your environment variables. Makes it easy to redeploy.

---

## 📱 Quick Reference Card

```
✅ Everything works:
   - Both services deployed ✓
   - /health shows langflow_status: connected ✓
   - Test call succeeds ✓

❌ Common issues:
   - Build timeout → Use Docker
   - langflow_status: disconnected → Check LANGFLOW_URL
   - Flow not found → Check DEFAULT_FLOW_ID
   - Auth error → Check LANGFLOW_API_KEY

🔍 Quick tests:
   curl https://bridge.railway.app/health
   curl https://bridge.railway.app/agents
   curl -X POST https://bridge.railway.app/voice

📊 Watch logs:
   Railway → Service → Deployments → Click deployment

🆘 Emergency:
   Railway → Service → Settings → Restart
```

---

**Keep this guide handy while deploying!** 📖
