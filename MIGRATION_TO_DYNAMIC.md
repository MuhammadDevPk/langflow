# Migration Guide: Static to Dynamic Multi-Agent

Guide to migrate from single static agent to dynamic multi-agent system.

**Current Setup:** One Twilio number → One hotel agent (static)
**After Migration:** Multiple Twilio numbers → Multiple agents (dynamic routing)

---

## 🎯 What Changes

### Before (Static)
```
Customer calls (472) 230-2360
  ↓
Always routes to Hotel Agent
  ↓
Uses: flow_id 9c7c075b-85da-4dfd-ae0c-bcb322851b04
```

### After (Dynamic)
```
Customer calls (472) 230-2360 → Hotel Agent (Joanna voice)
Customer calls (555) 123-4567 → Car Rental Agent (Matthew voice)
Customer calls (555) 987-6543 → Doctor Assistant (Amy voice)
                              ↓
                    Automatic routing based on number!
```

---

## ✅ Prerequisites

Before starting:
- [ ] Static system deployed and working (see `RAILWAY_DEPLOYMENT_GUIDE.md`)
- [ ] Railway Bridge service is running
- [ ] You have new agents built in Langflow
- [ ] You have their Flow IDs ready

---

## 📋 Step-by-Step Migration

### Step 1: Create New Agents in Langflow

**For each new agent:**

1. Open Langflow UI: `https://your-langflow.up.railway.app`
2. Login with `admin` / `admin123`
3. Create new agent flow:
   - Example: Car Rental Agent
   - Example: Doctor Assistant
   - Example: Marketing Agent
4. **Get the Flow ID:**
   - Open the agent
   - Look at URL: `https://...../flow/FLOW-ID-HERE`
   - Copy the Flow ID

**Example Flow IDs you might create:**
- Car Agent: `07b8cc4a-79e3-4b4f-b185-c665aa386937`
- Doctor Agent: `6d865c0e-2921-443e-9990-9da168b06308`
- Marketing Agent: `a606ba58-4cf6-4d2d-a21b-42ab3d9f3d7f`

---

### Step 2: Buy New Twilio Numbers

**For each agent, you need a dedicated number:**

1. Go to: **https://console.twilio.com/us1/develop/phone-numbers/manage/search**
2. Select country (US recommended)
3. Filter by **Voice** capability
4. Click **"Buy"** on a number
5. Confirm purchase
6. **Note the number** (e.g., `+1-555-123-4567`)
7. Repeat for each agent you want to deploy

**Example:**
- Hotel Agent: `+1-472-230-2360` (existing)
- Car Agent: `+1-555-123-4567` (new)
- Doctor Agent: `+1-555-987-6543` (new)

---

### Step 3: Update Bridge Configuration

#### 3.1 Prepare Agent Mappings

Create a JSON mapping of phone numbers to agents:

```json
{
  "14722302360": {
    "flow_id": "9c7c075b-85da-4dfd-ae0c-bcb322851b04",
    "intro": "Hi, this is your hotel booking assistant. How can I help you today?",
    "voice": "Polly.Joanna"
  },
  "15551234567": {
    "flow_id": "07b8cc4a-79e3-4b4f-b185-c665aa386937",
    "intro": "Welcome to our car rental service. What can I do for you?",
    "voice": "Polly.Matthew"
  },
  "15559876543": {
    "flow_id": "6d865c0e-2921-443e-9990-9da168b06308",
    "intro": "Hello, this is Doctor Pawel's personal assistant. How may I assist you?",
    "voice": "Polly.Amy"
  }
}
```

**Important Notes:**
- Remove `+` and `-` from phone numbers (only digits)
- Use your actual Flow IDs
- Customize intro message for each agent
- Choose different voices for variety

**Available Voices:**
- `Polly.Joanna` - Female, US English
- `Polly.Matthew` - Male, US English
- `Polly.Amy` - Female, British English
- `Polly.Brian` - Male, British English
- `Polly.Joey` - Male, US English
- `Polly.Kendra` - Female, US English
- Or simple: `man`, `woman`, `alice`

#### 3.2 Update Railway Environment Variable

1. Go to **Railway Dashboard**
2. Select **Bridge Service** (twilio-bridge)
3. Click **"Variables"** tab
4. Find `AGENT_MAPPINGS` variable
5. Click **Edit** (pencil icon)
6. **Replace the value** with your JSON (minified, one line):

```json
{"14722302360":{"flow_id":"9c7c075b-85da-4dfd-ae0c-bcb322851b04","intro":"Hi, this is your hotel booking assistant. How can I help you today?","voice":"Polly.Joanna"},"15551234567":{"flow_id":"07b8cc4a-79e3-4b4f-b185-c665aa386937","intro":"Welcome to our car rental service. What can I do for you?","voice":"Polly.Matthew"},"15559876543":{"flow_id":"6d865c0e-2921-443e-9990-9da168b06308","intro":"Hello, this is Doctor Pawel's personal assistant. How may I assist you?","voice":"Polly.Amy"}}
```

7. Click **"Save"** or hit Enter
8. **Railway automatically restarts** the service (takes ~10 seconds)

✅ **No code changes needed! No redeployment needed!**

---

### Step 4: Configure Twilio Webhooks

**For EACH Twilio number:**

1. Go to: **https://console.twilio.com/us1/develop/phone-numbers/manage/incoming**
2. Click the phone number
3. Scroll to **"Voice Configuration"**
4. Under **"A call comes in"**:
   - Webhook: `https://your-bridge-url.up.railway.app/voice`
   - **NOTE:** Same URL for all numbers!
   - HTTP Method: **POST**
5. Click **"Save"**
6. Repeat for all numbers

**Important:** All numbers use the **SAME webhook URL**. The bridge automatically routes to the correct agent based on which number was called!

---

### Step 5: Test Each Agent

**Test Hotel Agent:**
```bash
# Call (472) 230-2360 from verified number
# Should hear: "Hi, this is your hotel booking assistant..."
# Ask: "I want to book a room"
```

**Test Car Agent:**
```bash
# Call (555) 123-4567 from verified number
# Should hear: "Welcome to our car rental service..."
# Ask: "I need to rent a car"
```

**Test Doctor Agent:**
```bash
# Call (555) 987-6543 from verified number
# Should hear: "Hello, this is Doctor Pawel's personal assistant..."
# Ask: "I need to schedule an appointment"
```

---

## 🔍 Verify Migration

### Check Bridge Status

```bash
# Health check
curl https://your-bridge-url.up.railway.app/health

# Should show:
{
  "status": "healthy",
  "default_flow_id": "9c7c075b-85da-4dfd-ae0c-bcb322851b04",
  "mode": "multi-agent",              # Changed from "single-agent"!
  "agents_mapped": 3,                 # Shows number of agents
  "langflow_url": "https://..."
}
```

### List All Agents

```bash
curl https://your-bridge-url.up.railway.app/agents

# Returns all configured agents:
{
  "mode": "multi-agent",
  "default_agent": {...},
  "mapped_agents": {
    "14722302360": {...},
    "15551234567": {...},
    "15559876543": {...}
  }
}
```

### Check Logs

**Railway Dashboard:**
1. Select Bridge service
2. Click "Deployments" → Latest deployment
3. See logs showing:
```
📞 Call from +1234567890 to +14722302360
🤖 Using Flow: 9c7c075b-85da-4dfd-ae0c-bcb322851b04
```

---

## 📝 What Changed vs What Didn't

### ✅ Changed

| Item | Before | After |
|------|--------|-------|
| Mode | Single-agent | Multi-agent |
| Routing | Static (one agent) | Dynamic (phone-based) |
| Numbers | 1 Twilio number | Multiple numbers |
| Agents | 1 agent | Multiple agents |
| Voices | One voice | Different per agent |
| Config | Hardcoded | Environment variable |

### ❌ Didn't Change (No redeployment needed!)

- ✅ Code remains exactly the same
- ✅ Railway deployment stays the same
- ✅ Webhook URL stays the same
- ✅ No downtime during migration
- ✅ Existing hotel agent keeps working

---

## 🎯 Adding More Agents Later

**To add a new agent in the future:**

### Quick 4-Step Process:

1. **Build agent in Langflow** → Get Flow ID
2. **Buy new Twilio number** → Get phone number
3. **Update AGENT_MAPPINGS** on Railway:
   - Add new entry to JSON
   - Railway auto-restarts
4. **Configure Twilio webhook** for new number → Done!

**Example - Adding Marketing Agent:**

Edit `AGENT_MAPPINGS` on Railway, add:
```json
"15551112222": {
  "flow_id": "marketing-agent-flow-id",
  "intro": "Hi, this is your marketing assistant",
  "voice": "Polly.Kendra"
}
```

Configure Twilio number `(555) 111-2222` with same webhook URL.

**Done!** New agent is live in 2 minutes!

---

## 🐛 Troubleshooting

### Wrong agent responds

**Problem:** Call hotel number but get car agent response

**Solution:**
1. Check phone number format in `AGENT_MAPPINGS` (no `+`, `-`, or spaces)
2. Verify Twilio shows correct "To" number in logs
3. Check Railway logs to see which flow_id was selected

### Agent not found / uses default

**Problem:** Always uses default agent even with mappings

**Solution:**
1. Verify JSON syntax is correct (use JSON validator)
2. Check Railway actually saved the variable (refresh page)
3. Check Railway logs - service should restart after variable change
4. Verify phone number format matches exactly

### Different voice not working

**Problem:** All agents sound the same

**Solution:**
1. Check voice type spelling: `Polly.Joanna` (capital P, capital J)
2. Try different voices to ensure Twilio supports them
3. Check Railway logs for any voice-related errors

---

## 💡 Best Practices

### Naming Convention

Use descriptive intro messages:
```json
"intro": "Hi, this is [Service Name]. [What I do]. How can I help?"
```

Examples:
- ✅ "Hi, this is your hotel booking assistant. I can help you find and book rooms. What can I do for you?"
- ❌ "Hello" (too generic)

### Voice Selection

Match voice to service personality:
- **Professional services** (legal, medical): British voices (Amy, Brian)
- **Casual services** (booking, support): US voices (Joanna, Matthew)
- **Sales/Marketing**: Energetic voices (Joey, Kendra)

### Flow ID Organization

Keep a document with all your agents:
```
Hotel Agent:
  - Number: (472) 230-2360
  - Flow ID: 9c7c075b-85da-4dfd-ae0c-bcb322851b04
  - Voice: Joanna

Car Agent:
  - Number: (555) 123-4567
  - Flow ID: 07b8cc4a-79e3-4b4f-b185-c665aa386937
  - Voice: Matthew
```

---

## 📊 Comparison: Static vs Dynamic

| Feature | Static Setup | Dynamic Setup |
|---------|-------------|---------------|
| Code Changes | None | **None** |
| Deployment | Once | Once (same deployment) |
| Add New Agent | Edit code + redeploy | Edit env variable only |
| Downtime | Yes (redeploy) | **No** (hot reload) |
| Time to Add Agent | 10+ minutes | **2 minutes** |
| Complexity | Simple | Simple |
| Scalability | Limited | **Unlimited** |

---

## ✅ Migration Checklist

- [ ] Created new agents in Langflow
- [ ] Got Flow IDs for all agents
- [ ] Bought Twilio numbers for each agent
- [ ] Prepared JSON mapping
- [ ] Updated `AGENT_MAPPINGS` on Railway
- [ ] Verified Bridge restarted (check logs)
- [ ] Configured webhooks for all numbers
- [ ] Tested each agent with phone call
- [ ] Verified logs show correct routing
- [ ] Checked `/health` shows multi-agent mode
- [ ] Documented agent mappings

---

## 🎉 Migration Complete!

Your system is now fully dynamic:
- ✅ Multiple agents running
- ✅ Automatic routing by phone number
- ✅ Easy to add more agents
- ✅ No code changes ever needed
- ✅ Professional multi-service setup

**Adding agents is now a 2-minute task instead of redeployment!** 🚀

---

## 📞 Support

**Check these if issues occur:**
- Railway logs (Bridge service → Deployments)
- Twilio logs (https://console.twilio.com/us1/monitor/logs/voice)
- Test endpoints: `/health` and `/agents`
- Verify environment variables saved correctly

**Common issues:**
- JSON syntax errors → Use JSON validator
- Phone number format → Remove all non-digits
- Flow ID wrong → Verify in Langflow URL
- Voice not changing → Check spelling and capitalization
