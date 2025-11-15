# API Key Authentication Error - Fix Guide

**Issue**: "Incorrect API key provided" error in Langflow
**Status**: ❌ Your current API key is invalid/revoked/expired
**Solution**: Get a new valid API key from OpenAI

---

## Root Cause

Your OpenAI API key has been **rejected by OpenAI's servers**. This was confirmed through direct API testing.

**Current key** (in `.env`):
```
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
```

**Status**: ❌ INVALID (rejected by OpenAI)

---

## What's NOT Broken ✅

Good news! The converter code is working perfectly:
- ✅ API key injection logic is correct
- ✅ All 28 Agent nodes have API keys populated
- ✅ JSON structure is valid
- ✅ No truncation or encoding issues
- ✅ Import process works fine

The ONLY issue is the API key itself is invalid.

---

## Step-by-Step Fix

### Step 1: Get New API Key from OpenAI 🔑

1. **Visit OpenAI Platform:**
   - Go to: https://platform.openai.com/api-keys
   - Login to your account

2. **Check Current Key Status:**
   - Your current key will likely show as "Revoked" or "Expired"
   - If not visible, it has been deleted

3. **Create New Key:**
   - Click **"Create new secret key"**
   - Give it a name (e.g., "Langflow Voxhive")
   - **IMPORTANT**: Copy the entire key immediately
   - Key format: `sk-proj-...` (project key) or `sk-...` (user key)

4. **Test the New Key:**
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer YOUR_NEW_KEY_HERE"
   ```

   **Expected**: JSON response with list of models
   **Failure**: Error message about invalid key

---

### Step 2: Update .env File

1. **Open the .env file:**
   ```bash
   cd /Users/muhammad/Personal/Projects/Personal\ Projects/pawel/Voxhive/langflow
   nano .env
   ```
   (or use your preferred editor)

2. **Replace the API key:**
   ```env
   OPENAI_API_KEY=sk-proj-YOUR_NEW_VALID_KEY_HERE
   ```

   **Important**:
   - No quotes around the key
   - No spaces before or after the =
   - Paste the complete key

3. **Save and exit**

---

### Step 3: Clear Langflow's Cached Key

Langflow stores an encrypted copy of your API key in its database. Clear it:

```bash
# Delete the cached API key
sqlite3 ~/.langflow/data/database.db "DELETE FROM variable WHERE name='OPENAI_API_KEY';"

# Verify deletion
sqlite3 ~/.langflow/data/database.db "SELECT name FROM variable WHERE name='OPENAI_API_KEY';"
```

**Expected**: Empty result (no output)

---

### Step 4: Regenerate JSON with New Key

The converter now includes **automatic API key validation**!

```bash
cd /Users/muhammad/Personal/Projects/Personal\ Projects/pawel/Voxhive/langflow

python3 vapi_to_langflow_realnode_converter.py \
  json/inputs/daniel_dental_agent.json \
  -o json/outputs/feature4_VALID_KEY.json
```

**What you'll see:**

If key is **VALID** ✅:
```
Initializing converter...
  ✓ OpenAI API key loaded from environment
  ⏳ Validating API key with OpenAI...
  ✅ API key is valid and working
  ... (continues normally)
```

If key is **INVALID** ❌:
```
Initializing converter...
  ✓ OpenAI API key loaded from environment
  ⏳ Validating API key with OpenAI...
  ❌ API key validation FAILED
     The key may be invalid, revoked, or expired
     Please check your key at: https://platform.openai.com/api-keys

  ⚠️  WARNING: Generated JSON will contain an invalid API key!
     You can continue, but Langflow will fail with authentication errors.

  Continue anyway? (yes/no):
```

**Type `no` and get a new valid key!**

---

### Step 5: Import to Langflow

1. **Open Langflow** in your browser
2. **Delete old flow** (if exists) to avoid conflicts
3. **Import new JSON**:
   - Click "Import"
   - Select `feature4_VALID_KEY.json`
   - Wait for import to complete

4. **Verify nodes have keys:**
   - Click on any Agent node
   - Check "OpenAI API Key" field
   - Should show dots (masked key)

5. **Test in Playground:**
   - Click "Playground"
   - Send test message: "Hi I want to book appointment"
   - **Expected**: Proper response from Agent (no auth errors)

---

## Skip Validation (Advanced)

If you want to skip API key validation (not recommended):

```bash
python3 vapi_to_langflow_realnode_converter.py \
  json/inputs/daniel_dental_agent.json \
  -o output.json \
  --skip-validation
```

**Use case**: When you know the key is valid but network is slow/blocked

---

## Common API Key Issues

### Issue: Key Works in Other Apps but Not Langflow

**Possible causes:**
1. Langflow is using cached old key from database
2. Different key in Langflow's settings
3. Key permissions don't include the required models

**Solution:**
- Clear Langflow database (Step 3)
- Check Langflow settings for override keys
- Verify key permissions on OpenAI platform

---

### Issue: Project Key vs User Key

**Project keys** (`sk-proj-...`):
- Associated with specific OpenAI project
- Can have restrictions
- May have expiration dates
- More secure for team use

**User keys** (`sk-...`):
- Associated with your account
- Broader permissions
- Typically no expiration
- Simpler for personal use

**Recommendation**: If project keys cause issues, try a user-level key.

---

### Issue: Key Revoked Immediately

**Reasons:**
1. Key exposed publicly (GitHub, logs, etc.)
2. Billing/payment failure
3. Account suspension
4. Violated OpenAI terms

**Solution**:
- Check OpenAI account status
- Verify billing information
- Review usage limits
- Contact OpenAI support if needed

---

## Verification Checklist

After following all steps, verify:

- [ ] New API key obtained from OpenAI
- [ ] Key tested with curl command (works)
- [ ] `.env` file updated with new key
- [ ] Langflow database cache cleared
- [ ] JSON regenerated (validation passed)
- [ ] JSON imported to Langflow (no errors)
- [ ] Playground test (no auth errors)
- [ ] Agent responds correctly

---

## Why This Enhancement Helps

**Before** (old behavior):
1. Invalid key in .env
2. Generate JSON (no warning)
3. Import to Langflow (looks fine)
4. Run in playground → ❌ Auth error!
5. Spend time debugging Langflow

**After** (new behavior):
1. Invalid key in .env
2. Try to generate JSON
3. → ⚠️ Immediate warning: "API key is invalid!"
4. Fix the key BEFORE wasting time
5. Generate with valid key → ✅ Works first try

---

## Troubleshooting

### Error: "requests module not found"

Install the requests library:
```bash
pip install requests
```

### Error: "Cannot connect to OpenAI"

Check your internet connection:
```bash
ping api.openai.com
```

If blocked, use `--skip-validation` flag.

### Error: "Timeout validating API key"

Network is slow. Options:
1. Wait and retry
2. Use `--skip-validation` flag
3. Validation will succeed anyway (doesn't block on timeout)

### Langflow Still Shows Auth Errors

1. **Verify new key in .env**:
   ```bash
   cat .env | grep OPENAI_API_KEY
   ```

2. **Check Langflow database was cleared**:
   ```bash
   sqlite3 ~/.langflow/data/database.db "SELECT * FROM variable WHERE name='OPENAI_API_KEY';"
   ```
   Should be empty.

3. **Restart Langflow completely**:
   - Stop Langflow server
   - Clear browser cache
   - Start Langflow fresh
   - Re-import JSON

4. **Check Langflow logs** for specific error messages

---

## Summary

**Problem**: Invalid/revoked OpenAI API key
**Solution**: Get new valid key from OpenAI
**Bonus**: Converter now validates keys automatically!

**Steps**:
1. Get new key → https://platform.openai.com/api-keys
2. Update `.env`
3. Clear Langflow cache
4. Regenerate JSON (validation will confirm it works)
5. Import and test

**Time required**: 5-10 minutes

---

## Need Help?

**OpenAI Platform Support:**
- Dashboard: https://platform.openai.com
- API Keys: https://platform.openai.com/api-keys
- Usage: https://platform.openai.com/usage
- Billing: https://platform.openai.com/account/billing
- Support: https://help.openai.com

**Check API Key Format:**
- Project key: `sk-proj-` followed by ~160 characters
- User key: `sk-` followed by ~48 characters
- Both are valid formats

**Test API Key:**
```bash
# Quick test
curl -s https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY" | head -20

# Expected: JSON with "object": "list" and model data
# Failure: JSON with "error" object
```

---

**Last Updated**: 2025-11-15
**Converter Version**: With automatic API key validation
**Status**: Ready to use with valid API key
