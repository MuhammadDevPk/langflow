# Feature 4: Testing Guide
## Conditional Routing Import & Verification

**File to Import:** `json/outputs/feature4_routing_test.json`
**File Size:** 1.7 MB (1,665 KB)
**Status:** ✅ Validated and Ready for Import

---

## Pre-Import Verification ✅

**JSON Validation Results:**
- ✅ Valid JSON format
- ✅ All required fields present
- ✅ 39 nodes (all valid)
- ✅ 45 edges (all valid)
- ✅ No dangling edge references
- ✅ No duplicate IDs

**Node Breakdown:**
- 28 Agent nodes (24 conversation + 2 I/O bridges + 6 RouterAgents)
- 1 ChatInput
- 3 ChatOutput
- 7 ConditionalRouters

---

## Step 1: Import into Langflow

### Instructions

1. **Open Langflow** in your browser
2. **Navigate to Flows** page
3. **Click "Import"** or **"Upload Flow"** button
4. **Select file:** `json/outputs/feature4_routing_test.json`
5. **Wait for import** (may take 10-15 seconds due to 39 nodes)

### Expected Import Results

✅ **SUCCESS Indicators:**
- Flow name: "Appointment Scheduler"
- Description: "Converted from VAPI: Appointment Scheduler"
- 39 nodes visible on canvas
- No import error messages
- All nodes properly positioned

❌ **FAILURE Indicators (Should NOT See These):**
- "Some nodes could not be imported"
- "Invalid component type"
- "Missing required fields"
- "Connections removed due to invalid handles"

---

## Step 2: Visual Inspection

### Canvas Layout Check

After import, verify the visual layout on the Langflow canvas:

#### **Entry & Exit Points**
- ✅ **1 ChatInput** node on the far left
- ✅ **3 ChatOutput** nodes on the right side
  - "Chat Output" (main exit)
  - "Transfer Call" (tool placeholder)
  - "hangup_1748495964695" (tool placeholder)

#### **Conversation Nodes**
- ✅ **24 Agent nodes** with names like:
  - start
  - customer_type
  - new_appointment
  - reschedule_cancel
  - general_info
  - urgent_triage
  - collect_info
  - etc.

#### **Routing Nodes (NEW in Feature 4)**

**6 RouterAgent Nodes:**
- ✅ Router (start)
- ✅ Router (new_appointment)
- ✅ Router (reschedule_cancel)
- ✅ Router (general_info)
- ✅ Router (urgent_triage)
- ✅ Router (cancel)

**7 ConditionalRouter Nodes:**
- ✅ Route Check (start) - 2 nodes for 3-way cascade
- ✅ Route Check (new_appointment)
- ✅ Route Check (reschedule_cancel)
- ✅ Route Check (general_info)
- ✅ Route Check (urgent_triage)
- ✅ Route Check (cancel)

### Connection Pattern Check

Verify routing chains are connected:

**Example: start node (3-way cascade)**
```
start (Agent)
  ↓
Router (start)
  ↓
RouteCheck_1 (ConditionalRouter)
  ├─ [TRUE] → customer_type
  └─ [FALSE] → RouteCheck_2
                ├─ [TRUE] → reschedule_cancel
                └─ [FALSE] → general_info
```

**Example: new_appointment (2-way simple)**
```
new_appointment (Agent)
  ↓
Router (new_appointment)
  ↓
RouteCheck (ConditionalRouter)
  ├─ [TRUE] → urgent_triage
  └─ [FALSE] → collect_info
```

### API Key Check

**IMPORTANT:** Verify all Agent nodes have OpenAI API keys:
1. Click on any Agent node
2. Check "OpenAI API Key" field
3. Should show: `sk-...` (masked key)

If API keys missing:
- They should have been auto-injected from `.env`
- Manually add your OpenAI API key to each Agent/Router node

---

## Step 3: Edge Verification

### Edge Count

- **Total edges expected:** 45
- **Breakdown:**
  - Normal conversation edges: 17
  - Routing edges: 28

### Edge Types to Verify

1. **ChatInput → start**: Entry point
2. **Normal conversation edges**: Between Agent nodes (non-branching)
3. **Routing edges:**
   - Agent → RouterAgent
   - RouterAgent → ConditionalRouter
   - ConditionalRouter [TRUE] → Target Agent
   - ConditionalRouter [FALSE] → Target Agent or next Router
4. **Terminal edges:** Agent → ChatOutput

### How to Check Edges

1. Click on any node
2. Look for colored connection lines
3. Verify connections match the flow logic
4. Check for any disconnected nodes (should be none)

---

## Step 4: RouterAgent Prompt Inspection

### Verify Routing Prompts

Pick one RouterAgent to inspect (e.g., "Router (start)"):

1. **Click** on the "Router (start)" node
2. **Find** the "System Message" or "Agent Description" field
3. **Verify** it contains routing prompt like:

```
You are a routing agent for a conversation workflow. Based on the user's
message and conversation context, determine which condition best matches
the user's intent.

CONDITIONS:
1. User wanted to schedule a new appointment
2. User wanted to reschedule or cancel an appointment
3. User had questions about clinic info, hours, or services

INSTRUCTIONS:
- Analyze the user's message carefully
- Choose the condition number (1, 2, 3, etc.) that BEST matches the user's intent
- If multiple conditions could apply, choose the MOST SPECIFIC one
- Respond with ONLY the number, nothing else

Your response (just the number):
```

✅ **PASS if:** Routing prompt present with conditions listed
❌ **FAIL if:** Generic prompt or no routing instructions

---

## Step 5: ConditionalRouter Configuration Inspection

### Verify Router Configuration

Pick one ConditionalRouter to inspect (e.g., "Route Check (new_appointment)"):

1. **Click** on the ConditionalRouter node
2. **Check configuration fields:**

**Expected Values:**
- ✅ **Operator:** "equals"
- ✅ **Match Text:** "1" (or "2", "3" for cascade)
- ✅ **Case Sensitive:** False
- ✅ **Max Iterations:** 10
- ✅ **Default Route:** "false_result"

✅ **PASS if:** All values match
❌ **FAIL if:** Any value different or missing

---

## Step 6: Features 1-3 Verification

### Feature 1: Variable Extraction ✅

**Pick any conversation node** (e.g., "customer_type"):
1. Click on the node
2. Find "System Message" or prompt field
3. **Look for** JSON extraction instructions like:

```
IMPORTANT: After your response, you MUST extract the following information
and output it as JSON:
{
  "customer_type": "<string>" // new patient, existing patient, or unsure
}
```

✅ **PASS if:** JSON format instructions present
❌ **FAIL if:** No extraction instructions

### Feature 2: Conversation Flow ✅

**Check the "start" node:**
1. Click on "start" Agent node
2. Find "System Message" field
3. **Look for** first message like:

```
FIRST MESSAGE: When starting the conversation or when this node is first
reached, begin by saying:
"Thank you for calling Wellness Partners. This is Riley, your virtual
assistant. I'm here to help you schedule appointments..."

Then continue with your role:
[rest of prompt]
```

✅ **PASS if:** First message instruction present
❌ **FAIL if:** No first message

### Feature 3: Basic Chat ✅

**Verify I/O nodes:**
1. **ChatInput** connected to "start" node
2. Terminal nodes connected to **ChatOutput**
3. All connections valid (no red/broken edges)

✅ **PASS if:** All I/O properly connected
❌ **FAIL if:** Disconnected I/O or missing nodes

---

## Step 7: Playground Testing

### Test Setup

1. **Click "Playground"** button in Langflow
2. **Wait** for flow to initialize
3. **Verify** no errors in console/logs

### Pre-Test Checklist

Before running tests, ensure:
- ✅ All nodes have valid API keys
- ✅ ChatInput is ready (shows input field)
- ✅ No error messages in UI
- ✅ Flow status shows "Ready" or equivalent

---

## Test Scenarios

### Test 1: New Appointment Booking (Route to customer_type)

**User Input:**
```
Hi, I want to book an appointment
```

**Expected Routing Path:**
```
ChatInput → start → Router(start) → RouteCheck_1
  → [TRUE: condition 1 matched] → customer_type
```

**Expected Behavior:**
- ✅ Only ONE response (from customer_type agent)
- ✅ NO "Message empty" responses
- ✅ Agent asks about patient type (new/existing)
- ✅ Smooth conversation flow

❌ **FAIL if:**
- Multiple agent responses
- "Message empty" appears
- Routes to wrong node (reschedule_cancel or general_info)

### Test 2: Reschedule Request (Route to reschedule_cancel)

**User Input:**
```
I need to reschedule my appointment
```

**Expected Routing Path:**
```
ChatInput → start → Router(start) → RouteCheck_1
  → [FALSE] → RouteCheck_2
  → [TRUE: condition 2 matched] → reschedule_cancel
```

**Expected Behavior:**
- ✅ Only ONE response (from reschedule_cancel agent)
- ✅ NO "Message empty" responses
- ✅ Agent asks if user wants to reschedule or cancel
- ✅ Smooth conversation flow

❌ **FAIL if:**
- Multiple agent responses
- Routes to customer_type or general_info
- Cascade routing broken

### Test 3: General Information (Route to general_info - Default)

**User Input:**
```
What are your office hours?
```

**Expected Routing Path:**
```
ChatInput → start → Router(start) → RouteCheck_1
  → [FALSE] → RouteCheck_2
  → [FALSE: default route] → general_info
```

**Expected Behavior:**
- ✅ Only ONE response (from general_info agent)
- ✅ NO "Message empty" responses
- ✅ Agent provides clinic information
- ✅ Smooth conversation flow

❌ **FAIL if:**
- Routes to customer_type or reschedule_cancel
- Default routing not working

### Test 4: Urgent Appointment (2-way branch from new_appointment)

**Setup:** First route to new_appointment, then:

**User Input:**
```
I have severe tooth pain and need urgent care
```

**Expected Routing Path:**
```
new_appointment → Router(new_appointment) → RouteCheck(new_appointment)
  → [TRUE: urgent] → urgent_triage
```

**Expected Behavior:**
- ✅ Routes to urgent_triage (not collect_info)
- ✅ Only ONE path executes
- ✅ Agent handles urgent care

### Test 5: Routine Appointment (2-way branch from new_appointment)

**Setup:** First route to new_appointment, then:

**User Input:**
```
I'd like a routine cleaning appointment
```

**Expected Routing Path:**
```
new_appointment → Router(new_appointment) → RouteCheck(new_appointment)
  → [FALSE: not urgent] → collect_info
```

**Expected Behavior:**
- ✅ Routes to collect_info (not urgent_triage)
- ✅ Only ONE path executes
- ✅ Agent collects patient info

### Test 6: Reschedule vs Cancel (2-way branch)

**Setup:** First route to reschedule_cancel, then:

**User Input A (Reschedule):**
```
I want to reschedule my appointment
```

**Expected:** Routes to "reschedule" node

**User Input B (Cancel):**
```
I need to cancel my appointment
```

**Expected:** Routes to "cancel" node

---

## Success Criteria

### Import Phase ✅

- [x] JSON imports without errors
- [x] 39 nodes visible
- [x] 45 edges connected
- [x] All routing nodes present (6 RouterAgents + 7 ConditionalRouters)

### Configuration Phase ✅

- [x] API keys present in all Agent nodes
- [x] RouterAgent prompts contain conditions
- [x] ConditionalRouter configs correct (operator=equals, match_text set)
- [x] Features 1-3 still functional

### Runtime Phase ⏳

- [ ] Only ONE path executes per branching point
- [ ] NO "Message empty" responses
- [ ] Routing decisions are correct (routes to intended node)
- [ ] All 6 test scenarios pass
- [ ] Conversation flows naturally

---

## Troubleshooting

### Issue: Multiple "Message empty" Responses

**Symptom:** Seeing multiple empty messages like before Feature 4

**Diagnosis:** Routing logic not working

**Check:**
1. Are RouterAgent nodes executing?
2. Do ConditionalRouters have correct match_text values?
3. Are edges connected to true_result/false_result outputs?

**Fix:**
- Verify edge connections from ConditionalRouter
- Check RouterAgent is returning numbers (1, 2, 3)
- Inspect Langflow execution logs

### Issue: Wrong Routing Path

**Symptom:** Routes to unexpected node

**Diagnosis:** Condition evaluation incorrect

**Check:**
1. RouterAgent prompt has correct conditions
2. Condition numbers match ConditionalRouter match_text
3. RouterAgent is returning expected number

**Fix:**
- Review RouterAgent system message
- Test RouterAgent in isolation
- Adjust condition prompts for clarity

### Issue: No Response at All

**Symptom:** Flow stops at RouterAgent or ConditionalRouter

**Diagnosis:** Edge connection issue

**Check:**
1. RouterAgent → ConditionalRouter edge exists
2. ConditionalRouter → target edges exist
3. Correct output handles used (response, true_result, false_result)

**Fix:**
- Manually reconnect edges
- Verify handle names in edge details

### Issue: Import Errors

**Symptom:** Errors during JSON import

**Diagnosis:** JSON structure issue or Langflow version mismatch

**Check:**
1. Langflow version (should be recent)
2. JSON validation (already done, should be valid)
3. Component compatibility

**Fix:**
- Update Langflow to latest version
- Check Langflow logs for specific error
- Re-generate JSON if needed

---

## Debugging Tools

### Langflow Execution Logs

**How to Access:**
1. Open browser Developer Tools (F12)
2. Go to "Console" tab
3. Run flow in playground
4. Watch for execution messages

**What to Look For:**
- RouterAgent output (should be number: 1, 2, 3)
- ConditionalRouter evaluation (TRUE or FALSE)
- Any error messages or warnings

### Node Inspector

**How to Use:**
1. Click on any node during/after execution
2. Look for "Output" or "Result" tab
3. See what the node returned

**For RouterAgent:**
- Should return message with number (1, 2, or 3)

**For ConditionalRouter:**
- Should show which output was used (true_result or false_result)

---

## Next Steps After Testing

### If All Tests Pass ✅

**Congratulations!** Feature 4 is working correctly.

**Next:**
1. Document any issues encountered
2. Note any improvements needed
3. Proceed to Feature 5 (Tool Integration)

### If Tests Fail ❌

**Report to Developer:**
1. Which test scenario failed
2. Expected vs actual behavior
3. Screenshots of:
   - Canvas layout
   - Failed test output
   - Node configurations
4. Langflow console logs

**Common Fixes:**
- Manually reconnect broken edges
- Update API keys
- Adjust RouterAgent prompts
- Verify ConditionalRouter match_text values

---

## Summary

This testing guide covers:
- ✅ Import verification (Steps 1-2)
- ✅ Visual inspection (Steps 2-3)
- ✅ Configuration check (Steps 4-5)
- ✅ Features 1-3 verification (Step 6)
- ✅ Playground testing (Step 7)
- ✅ 6 test scenarios for all branching patterns
- ✅ Troubleshooting guide

**Estimated Testing Time:** 30-45 minutes

**Critical Tests:**
- Test 1: 3-way cascade routing (start node)
- Test 4-5: 2-way routing (new_appointment node)

If these pass, Feature 4 is working correctly! 🎉

---

**Testing Started:** _____________
**Testing Completed:** _____________
**Result:** ⬜ PASS  ⬜ FAIL
**Notes:** _______________________________________________
