# Feature 4: Test Scenarios
## Comprehensive Routing Test Cases

**Purpose:** Verify all 6 branching points route correctly
**File:** `feature4_routing_test.json`

---

## Quick Reference: All 6 Branching Points

| Branch # | Source Node | Pattern | Paths | ConditionalRouters |
|----------|-------------|---------|-------|-------------------|
| 1 | start | Cascade (3-way) | customer_type, reschedule_cancel, general_info | 2 |
| 2 | new_appointment | Simple (2-way) | urgent_triage, collect_info | 1 |
| 3 | reschedule_cancel | Simple (2-way) | reschedule, cancel | 1 |
| 4 | general_info | Simple (2-way) | customer_type_from_info, hangup | 1 |
| 5 | urgent_triage | Simple (2-way) | emergency_redirect, collect_info_urgent | 1 |
| 6 | cancel | Simple (2-way) | reschedule_from_cancel, hangup | 1 |

---

## Branch 1: Start Node (3-Way Cascade)

### Overview
**Source:** start
**Pattern:** Cascade (3-way)
**RouterAgent:** Router (start)
**ConditionalRouters:** RouteCheck_1 (start), RouteCheck_2 (start)

### Routing Logic
```
start
  ↓
Router(start) → evaluates and returns 1, 2, or 3
  ↓
RouteCheck_1
  ├─ [TRUE if input="1"] → customer_type (new appointment)
  └─ [FALSE] → RouteCheck_2
                ├─ [TRUE if input="2"] → reschedule_cancel
                └─ [FALSE if input="3"] → general_info (default)
```

### Test Scenario 1.1: Route to customer_type

**User Input:**
```
Hi, I'd like to schedule an appointment
```

**Alternative Inputs:**
- "I want to book an appointment"
- "Can I make an appointment?"
- "I need to schedule a visit"

**Expected VAPI Condition:** "User wanted to schedule a new appointment"

**Expected Routing:**
- RouterAgent returns: `1`
- RouteCheck_1 evaluates: `TRUE` (1 == 1)
- Routes to: `customer_type`

**Success Criteria:**
- ✅ ONLY customer_type responds
- ✅ NO reschedule_cancel or general_info responses
- ✅ NO "Message empty" errors
- ✅ Agent asks about patient type (new/existing)

### Test Scenario 1.2: Route to reschedule_cancel

**User Input:**
```
I need to reschedule my appointment
```

**Alternative Inputs:**
- "Can I change my appointment time?"
- "I want to cancel my appointment"
- "I need to move my appointment to another day"

**Expected VAPI Condition:** "User wanted to reschedule or cancel an appointment"

**Expected Routing:**
- RouterAgent returns: `2`
- RouteCheck_1 evaluates: `FALSE` (2 != 1)
- Passes to RouteCheck_2
- RouteCheck_2 evaluates: `TRUE` (2 == 2)
- Routes to: `reschedule_cancel`

**Success Criteria:**
- ✅ ONLY reschedule_cancel responds
- ✅ NO customer_type or general_info responses
- ✅ NO "Message empty" errors
- ✅ Agent asks if user wants to reschedule or cancel

### Test Scenario 1.3: Route to general_info (Default)

**User Input:**
```
What are your office hours?
```

**Alternative Inputs:**
- "Where are you located?"
- "Do you accept my insurance?"
- "What services do you offer?"
- "Can you tell me about your clinic?"

**Expected VAPI Condition:** "User had questions about clinic info, hours, or services"

**Expected Routing:**
- RouterAgent returns: `3`
- RouteCheck_1 evaluates: `FALSE` (3 != 1)
- Passes to RouteCheck_2
- RouteCheck_2 evaluates: `FALSE` (3 != 2)
- Routes to: `general_info` (default path)

**Success Criteria:**
- ✅ ONLY general_info responds
- ✅ NO customer_type or reschedule_cancel responses
- ✅ NO "Message empty" errors
- ✅ Agent provides clinic information

---

## Branch 2: New Appointment Node (2-Way Simple)

### Overview
**Source:** new_appointment
**Pattern:** Simple (2-way)
**RouterAgent:** Router (new_appointment)
**ConditionalRouter:** RouteCheck (new_appointment)

### Routing Logic
```
new_appointment
  ↓
Router(new_appointment) → returns 1 or 2
  ↓
RouteCheck(new_appointment)
  ├─ [TRUE if input="1"] → urgent_triage (urgent care)
  └─ [FALSE if input="2"] → collect_info (routine)
```

### Test Scenario 2.1: Route to urgent_triage

**Setup:** First complete conversation to reach new_appointment node

**User Input:**
```
I have severe tooth pain and need urgent care
```

**Alternative Inputs:**
- "It's an emergency, I need to see someone today"
- "I have a dental emergency"
- "I'm in a lot of pain, can I get urgent care?"

**Expected VAPI Condition:** "User indicated urgent care need"

**Expected Routing:**
- RouterAgent returns: `1`
- RouteCheck evaluates: `TRUE` (1 == 1)
- Routes to: `urgent_triage`

**Success Criteria:**
- ✅ ONLY urgent_triage responds
- ✅ NO collect_info response
- ✅ Agent handles urgent case

### Test Scenario 2.2: Route to collect_info

**Setup:** First complete conversation to reach new_appointment node

**User Input:**
```
I need a routine cleaning
```

**Alternative Inputs:**
- "I'd like a regular checkup"
- "Can I schedule a cleaning appointment?"
- "I need a routine dental exam"

**Expected VAPI Condition:** "User needed routine appointment"

**Expected Routing:**
- RouterAgent returns: `2`
- RouteCheck evaluates: `FALSE` (2 != 1)
- Routes to: `collect_info`

**Success Criteria:**
- ✅ ONLY collect_info responds
- ✅ NO urgent_triage response
- ✅ Agent collects patient information

---

## Branch 3: Reschedule/Cancel Node (2-Way Simple)

### Overview
**Source:** reschedule_cancel
**Pattern:** Simple (2-way)
**RouterAgent:** Router (reschedule_cancel)
**ConditionalRouter:** RouteCheck (reschedule_cancel)

### Routing Logic
```
reschedule_cancel
  ↓
Router(reschedule_cancel) → returns 1 or 2
  ↓
RouteCheck(reschedule_cancel)
  ├─ [TRUE if input="1"] → reschedule
  └─ [FALSE if input="2"] → cancel
```

### Test Scenario 3.1: Route to reschedule

**Setup:** First route to reschedule_cancel node

**User Input:**
```
I want to reschedule
```

**Alternative Inputs:**
- "I need to change my appointment time"
- "Can I move my appointment to next week?"
- "I'd like to reschedule for a different day"

**Expected VAPI Condition:** "User wanted to reschedule appointment"

**Expected Routing:**
- RouterAgent returns: `1`
- RouteCheck evaluates: `TRUE` (1 == 1)
- Routes to: `reschedule`

**Success Criteria:**
- ✅ ONLY reschedule responds
- ✅ NO cancel response
- ✅ Agent helps reschedule

### Test Scenario 3.2: Route to cancel

**Setup:** First route to reschedule_cancel node

**User Input:**
```
I want to cancel
```

**Alternative Inputs:**
- "Please cancel my appointment"
- "I need to cancel"
- "I won't be able to make it, cancel please"

**Expected VAPI Condition:** "User wanted to cancel appointment"

**Expected Routing:**
- RouterAgent returns: `2`
- RouteCheck evaluates: `FALSE` (2 != 1)
- Routes to: `cancel`

**Success Criteria:**
- ✅ ONLY cancel responds
- ✅ NO reschedule response
- ✅ Agent processes cancellation

---

## Branch 4: General Info Node (2-Way Simple)

### Overview
**Source:** general_info
**Pattern:** Simple (2-way)
**RouterAgent:** Router (general_info)
**ConditionalRouter:** RouteCheck (general_info)

### Routing Logic
```
general_info
  ↓
Router(general_info) → returns 1 or 2
  ↓
RouteCheck(general_info)
  ├─ [TRUE if input="1"] → customer_type_from_info
  └─ [FALSE if input="2"] → hangup_1748495964695
```

### Test Scenario 4.1: Route to customer_type_from_info

**Setup:** First route to general_info node

**User Input:**
```
Actually, I'd like to schedule an appointment now
```

**Alternative Inputs:**
- "Can I book an appointment after hearing that?"
- "I want to make an appointment"
- "Let me schedule a visit"

**Expected VAPI Condition:** "User wanted to schedule after getting info"

**Expected Routing:**
- RouterAgent returns: `1`
- RouteCheck evaluates: `TRUE` (1 == 1)
- Routes to: `customer_type_from_info`

**Success Criteria:**
- ✅ ONLY customer_type_from_info responds
- ✅ NO hangup response
- ✅ Agent continues to scheduling

### Test Scenario 4.2: Route to hangup

**Setup:** First route to general_info node

**User Input:**
```
Thank you, that's all I needed
```

**Alternative Inputs:**
- "No thanks, just wanted info"
- "That answers my questions, goodbye"
- "I'm all set, thank you"

**Expected VAPI Condition:** "User's questions answered, no further help needed"

**Expected Routing:**
- RouterAgent returns: `2`
- RouteCheck evaluates: `FALSE` (2 != 1)
- Routes to: `hangup_1748495964695`

**Success Criteria:**
- ✅ ONLY hangup node triggers
- ✅ NO customer_type_from_info response
- ✅ Conversation ends

---

## Branch 5: Urgent Triage Node (2-Way Simple)

### Overview
**Source:** urgent_triage
**Pattern:** Simple (2-way)
**RouterAgent:** Router (urgent_triage)
**ConditionalRouter:** RouteCheck (urgent_triage)

### Routing Logic
```
urgent_triage
  ↓
Router(urgent_triage) → returns 1 or 2
  ↓
RouteCheck(urgent_triage)
  ├─ [TRUE if input="1"] → emergency_redirect
  └─ [FALSE if input="2"] → collect_info_urgent
```

### Test Scenario 5.1: Route to emergency_redirect

**Setup:** First route to urgent_triage node

**User Input:**
```
I'm bleeding heavily and in extreme pain
```

**Alternative Inputs:**
- "This is a medical emergency"
- "I think my jaw is broken"
- "I have severe swelling and can't breathe well"

**Expected VAPI Condition:** "Symptoms indicate medical emergency"

**Expected Routing:**
- RouterAgent returns: `1`
- RouteCheck evaluates: `TRUE` (1 == 1)
- Routes to: `emergency_redirect`

**Success Criteria:**
- ✅ ONLY emergency_redirect responds
- ✅ NO collect_info_urgent response
- ✅ Agent redirects to emergency services

### Test Scenario 5.2: Route to collect_info_urgent

**Setup:** First route to urgent_triage node

**User Input:**
```
I have a toothache that's getting worse
```

**Alternative Inputs:**
- "My tooth hurts but I can manage"
- "I need same-day care for tooth pain"
- "It's urgent but not an emergency"

**Expected VAPI Condition:** "Urgent but not emergency, can schedule same-day"

**Expected Routing:**
- RouterAgent returns: `2`
- RouteCheck evaluates: `FALSE` (2 != 1)
- Routes to: `collect_info_urgent`

**Success Criteria:**
- ✅ ONLY collect_info_urgent responds
- ✅ NO emergency_redirect response
- ✅ Agent schedules urgent appointment

---

## Branch 6: Cancel Node (2-Way Simple)

### Overview
**Source:** cancel
**Pattern:** Simple (2-way)
**RouterAgent:** Router (cancel)
**ConditionalRouter:** RouteCheck (cancel)

### Routing Logic
```
cancel
  ↓
Router(cancel) → returns 1 or 2
  ↓
RouteCheck(cancel)
  ├─ [TRUE if input="1"] → reschedule_from_cancel
  └─ [FALSE if input="2"] → hangup_1748495964695
```

### Test Scenario 6.1: Route to reschedule_from_cancel

**Setup:** First route to cancel node

**User Input:**
```
Actually, can I reschedule instead?
```

**Alternative Inputs:**
- "Wait, I'd rather reschedule"
- "Can I move it to another time instead of canceling?"
- "Let me reschedule instead"

**Expected VAPI Condition:** "Patient wants to reschedule instead of cancel"

**Expected Routing:**
- RouterAgent returns: `1`
- RouteCheck evaluates: `TRUE` (1 == 1)
- Routes to: `reschedule_from_cancel`

**Success Criteria:**
- ✅ ONLY reschedule_from_cancel responds
- ✅ NO hangup response
- ✅ Agent helps reschedule

### Test Scenario 6.2: Route to hangup

**Setup:** First route to cancel node

**User Input:**
```
Yes, please cancel it
```

**Alternative Inputs:**
- "No, just cancel please"
- "Confirm cancellation"
- "That's fine, cancel it"

**Expected VAPI Condition:** "Appointment canceled, no reschedule needed"

**Expected Routing:**
- RouterAgent returns: `2`
- RouteCheck evaluates: `FALSE` (2 != 1)
- Routes to: `hangup_1748495964695`

**Success Criteria:**
- ✅ ONLY hangup node triggers
- ✅ NO reschedule_from_cancel response
- ✅ Conversation ends

---

## Testing Checklist

### Priority 1: Critical Tests (Must Pass)

- [ ] **Test 1.1**: start → customer_type (3-way cascade TRUE)
- [ ] **Test 1.2**: start → reschedule_cancel (3-way cascade middle)
- [ ] **Test 1.3**: start → general_info (3-way cascade default)
- [ ] **Test 2.1**: new_appointment → urgent_triage (2-way TRUE)
- [ ] **Test 2.2**: new_appointment → collect_info (2-way FALSE)

**If Priority 1 passes**, Feature 4 core functionality is working!

### Priority 2: Additional Tests (Should Pass)

- [ ] **Test 3.1**: reschedule_cancel → reschedule
- [ ] **Test 3.2**: reschedule_cancel → cancel
- [ ] **Test 4.1**: general_info → customer_type_from_info
- [ ] **Test 4.2**: general_info → hangup
- [ ] **Test 5.1**: urgent_triage → emergency_redirect
- [ ] **Test 5.2**: urgent_triage → collect_info_urgent
- [ ] **Test 6.1**: cancel → reschedule_from_cancel
- [ ] **Test 6.2**: cancel → hangup

---

## Expected vs Actual Template

### For Each Test:

**Test Number:** _______________

**User Input:** _______________________________________________

**Expected Route:** _______________

**Actual Route:** _______________

**RouterAgent Output:** _______________

**ConditionalRouter Evaluation:** ⬜ TRUE  ⬜ FALSE

**Success:** ⬜ PASS  ⬜ FAIL

**Notes:** _______________________________________________

---

## Common Failure Patterns

### Pattern 1: Multiple Responses
**Symptom:** Multiple agents respond instead of one
**Cause:** Routing not working, reverting to Feature 3 behavior
**Fix:** Check edge connections, verify RouterAgent/ConditionalRouter

### Pattern 2: Wrong Path
**Symptom:** Routes to incorrect node
**Cause:** Condition mismatch or wrong match_text value
**Fix:** Verify RouterAgent conditions, check ConditionalRouter match_text

### Pattern 3: No Response
**Symptom:** Flow stops at router
**Cause:** Missing edge connection
**Fix:** Manually reconnect edges from ConditionalRouter outputs

### Pattern 4: RouterAgent Returns Text Instead of Number
**Symptom:** ConditionalRouter always evaluates FALSE
**Cause:** RouterAgent prompt not clear or model not following instructions
**Fix:** Adjust routing prompt, use stricter format requirements

---

## Debug Output Template

If any test fails, capture this information:

```
Test: _______________
User Input: _______________
Expected: _______________
Actual: _______________

RouterAgent Output:
[paste full response here]

ConditionalRouter Input:
[what text did it receive]

ConditionalRouter Match Text:
[configured value]

ConditionalRouter Output:
[which path: true_result or false_result]

Target Node:
[which node actually executed]

Error Messages:
[any errors in console]
```

---

## Summary

**Total Test Scenarios:** 13
- 3 for 3-way cascade (start)
- 10 for 2-way simple (remaining 5 branches × 2 paths each)

**Critical Tests:** 5 (Tests 1.1-1.3, 2.1-2.2)

**Testing Time:** ~45 minutes for all scenarios

**Pass Criteria:** All routing paths execute correctly with no "Message empty" errors

---

**Testing Date:** _______________
**Tester:** _______________
**Overall Result:** ⬜ PASS  ⬜ FAIL
**Pass Rate:** _____/13 tests passed
