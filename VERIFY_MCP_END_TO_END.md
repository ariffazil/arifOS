# MCP Server End-to-End Verification Plan

**Date:** 2026-01-16
**Status:** Ready for testing
**Goal:** Verify MCP server works with all 3 agents before test unification

---

## ✅ Pre-Verification Status

**Import Chain:** FIXED ✅
**Server Module:** READY ✅
**Agent Configs:** CREATED ✅
**Documentation:** COMPLETE ✅

**All prerequisites met - ready to verify!**

---

## 🎯 Verification Steps (Follow in Order)

### **Step 1: Start the MCP Server**

**Action:**
```cmd
start_mcp.bat
```

**Expected Output:**
```
================================================================================
arifOS Unified MCP Server v47.0.0
================================================================================

Environment:
  ARIFOS_ALLOW_LEGACY_SPEC=1
  ARIFOS_PHYSICS_DISABLED=1

Starting MCP server...
Press Ctrl+C to stop

ARIFOS_ALLOW_LEGACY_SPEC=1: Using default ledger config (bypass mode)
```

**Server State:** Waiting for stdio input (this is correct!)

**If you see errors:** Check `MCP_QUICKSTART_GUIDE.md` Troubleshooting section

---

### **Step 2: Verify Server Process is Running**

**In a NEW terminal window:**
```cmd
tasklist | findstr python
```

**Expected:** You should see a `python.exe` process

---

### **Step 3: Test Agent Connection**

**Choose ONE agent to test first** (recommend Codex for engineering work):

#### **Option A: Test with Codex (Engineer)**

**1. Locate config file:**
```
.codex\mcp_config.json
```

**2. Verify config contents:**
```json
{
  "mcpServers": {
    "arifos-unified-codex": {
      "command": "python",
      "args": ["scripts/unified_mcp_entry.py"],
      "cwd": "C:\\Users\\User\\OneDrive\\Documents\\GitHub\\arifOS",
      "env": {
        "ARIFOS_ALLOW_LEGACY_SPEC": "1",
        "ARIFOS_USER_ID": "codex_engineer",
        ...
      }
    }
  }
}
```

**3. Configure your Codex agent to use this MCP server**

Exact steps depend on how you run Codex:
- **If using Claude Desktop:** Add server config to Claude Desktop settings
- **If using MCP CLI client:** Point client to config file
- **If using custom integration:** Use the config as reference for connection params

---

#### **Option B: Test with Kimi (Reflexes)**

**Config file:** `.kimi\mcp_config.json`
**User ID:** `kimi_reflexes`
**Role:** High-speed constitutional validation

---

#### **Option C: Test with Antigravity (Architect)**

**Config file:** `.antigravity\mcp_config.json`
**User ID:** `antigravity_architect`
**Role:** Strategic architectural decisions

---

### **Step 4: Test a Simple Tool Call**

Once agent is connected, try the simplest tool first:

**Tool:** `constitutional_health`
**Purpose:** Get system vitality metrics
**Risk:** Low (read-only)

**Example request from agent:**
```
"Check the constitutional health of the arifOS system"
```

**Expected Response:**
```json
{
  "status": "operational",
  "floors_active": 12,
  "trinity_status": {
    "agi": "operational",
    "asi": "operational",
    "apex": "operational"
  },
  "verdict": "SEAL"
}
```

---

### **Step 5: Test a Core Pipeline Tool**

**Tool:** `agi_think`
**Purpose:** AGI reasoning engine
**Input:** Simple question

**Example request:**
```
"Use agi_think to analyze: What is 2+2?"
```

**Expected Response:**
```json
{
  "reasoning": "Mathematical evaluation...",
  "verdict": "SEAL",
  "floors": {
    "F1": "LOCK",
    "F2": 0.99,
    "F4": 0.0
  }
}
```

---

### **Step 6: Test Constitutional Validation**

**Tool:** `apex_seal`
**Purpose:** Full constitutional judgment
**Input:** Sample text to validate

**Example request:**
```
"Use apex_seal to validate this text: 'The sky is blue.'"
```

**Expected Response:**
```json
{
  "verdict": "SEAL",
  "reason": "All 12 constitutional floors passed",
  "floors": {
    "F1": "LOCK",
    "F2": 0.99,
    "F3": 0.95,
    ...
    "F12": 0.50
  },
  "pulse": 0.92
}
```

---

## ✅ Success Criteria

Mark each as you complete it:

- [ ] **Server starts** without errors
- [ ] **Server process** visible in task list
- [ ] **Agent connects** to MCP server
- [ ] **Tool call 1** (`constitutional_health`) succeeds
- [ ] **Tool call 2** (`agi_think`) succeeds
- [ ] **Tool call 3** (`apex_seal`) succeeds
- [ ] **Verdict returned** (SEAL/VOID/PARTIAL/etc.)
- [ ] **No crashes** or unexpected errors

**If ALL checked:** MCP server is VERIFIED ✅
**If ANY failed:** See Troubleshooting section below

---

## 🔧 Troubleshooting

### **Problem: Server won't start**

**Symptom:** `start_mcp.bat` shows errors or exits immediately

**Solutions:**

1. **Check environment variables:**
   ```cmd
   echo %ARIFOS_ALLOW_LEGACY_SPEC%
   echo %ARIFOS_PHYSICS_DISABLED%
   ```
   Both should show `1`

2. **Test import manually:**
   ```cmd
   python -c "from arifos_core.mcp.unified_server import main; print('OK')"
   ```
   Should print `OK`

3. **Check Python version:**
   ```cmd
   python --version
   ```
   Should be Python 3.8+

4. **Run with verbose errors:**
   ```cmd
   python scripts\unified_mcp_entry.py
   ```
   (Shows full error stack trace)

---

### **Problem: Agent can't connect**

**Symptom:** Agent shows "Connection refused" or "Server not found"

**Solutions:**

1. **Verify server is running:**
   ```cmd
   tasklist | findstr python
   ```

2. **Check config file path:**
   ```cmd
   dir .codex\mcp_config.json
   ```
   File must exist

3. **Verify working directory in config:**
   ```json
   "cwd": "C:\\Users\\User\\OneDrive\\Documents\\GitHub\\arifOS"
   ```
   Must point to actual arifOS directory

4. **Test server manually:**
   ```cmd
   echo {} | python scripts\unified_mcp_entry.py
   ```
   Should process empty JSON input without crashing

---

### **Problem: Tool call fails**

**Symptom:** Tool returns error or unexpected response

**Solutions:**

1. **Check tool name spelling:**
   ```
   ✅ Correct: constitutional_health
   ❌ Wrong: Constitutional_Health
   ```

2. **Verify tool is enabled in agent config:**
   ```json
   "enabledTools": [
     "constitutional_health",
     "agi_think",
     ...
   ]
   ```

3. **Check server logs:**
   Server prints errors to stderr - look for `[FAIL]` or `Error:` messages

4. **Test tool in isolation:**
   ```python
   from arifos_core.mcp.unified_server import UNIFIED_TOOLS
   print([t['name'] for t in UNIFIED_TOOLS])
   ```

---

### **Problem: Verdict is always VOID**

**Symptom:** All responses get VOID verdict regardless of input

**Cause:** Floor thresholds too strict or misconfigured

**Solutions:**

1. **Check floor configuration in agent config:**
   ```json
   "constitutionalSettings": {
     "f2_truth": 0.99,
     "f4_clarity": 0.0,
     ...
   }
   ```

2. **Lower thresholds temporarily for testing:**
   ```json
   "f2_truth": 0.80  # Lower from 0.99
   ```

3. **Check for F9 (Anti-Hantu) violations:**
   Avoid anthropomorphic language in test inputs

---

## 📊 Verification Checklist

### **Before Starting**
- [x] Import fixes applied (8 total)
- [x] Agent configs created (3 agents)
- [x] Documentation written
- [x] Batch files created

### **During Testing**
- [ ] Server starts successfully
- [ ] No import errors shown
- [ ] Server waits for input (correct behavior)
- [ ] Agent connects to server
- [ ] First tool call succeeds
- [ ] Verdict returned correctly

### **After Success**
- [ ] Document which agent(s) work
- [ ] Note any issues encountered
- [ ] Ready to proceed to test unification
- [ ] Server can be stopped/restarted reliably

---

## 🎯 Next Steps After Verification

### **If MCP Server Works End-to-End:**

1. ✅ **Document success** - Note which tools work, any issues
2. ⏭️ **Proceed to Test Unification** - Option 1 (Full Import Audit)
3. ⏭️ **Fix test suite systematically** - 210+ tests with proper imports
4. ⏭️ **Achieve 85% coverage** - Complete kernel testing

### **If Issues Found:**

1. Document specific failure
2. Check troubleshooting section above
3. Review `MCP_SERVER_ACTIVATION_REPORT_v47.md` for details
4. Request assistance if needed

---

## 📝 Test Log Template

**Copy this to record your verification:**

```
=== MCP Server End-to-End Verification ===
Date: 2026-01-16
Time: _______
Agent Tested: [ ] Kimi  [ ] Codex  [ ] Antigravity

Step 1 - Server Start:
[ ] SUCCESS  [ ] FAILED
Notes: _______________

Step 2 - Process Running:
[ ] SUCCESS  [ ] FAILED
Process ID: ___________

Step 3 - Agent Connection:
[ ] SUCCESS  [ ] FAILED
Connection Method: _______________

Step 4 - constitutional_health tool:
[ ] SUCCESS  [ ] FAILED
Response: _______________

Step 5 - agi_think tool:
[ ] SUCCESS  [ ] FAILED
Response: _______________

Step 6 - apex_seal tool:
[ ] SUCCESS  [ ] FAILED
Verdict: _______________

Overall Result:
[ ] ALL PASSED - Ready for test unification
[ ] PARTIAL - Document issues above
[ ] FAILED - Review troubleshooting

Next Action:
_______________
```

---

## 🏛️ Constitutional Reminder

**During testing, the 12 floors are actively enforcing:**

- F1 (Amanah): LOCK - Every operation verified
- F2 (Truth): ≥0.99 - Factual accuracy required
- F9 (Anti-Hantu): 0 - No consciousness claims
- F10-F12: Hypervisor active

**This is production-grade governance**, not test mode!

---

`★ Insight ─────────────────────────────────────`
**End-to-End Verification Philosophy**: We're testing the **full stack** - not just imports, but actual agent→server→tool→verdict flow.

**Why this matters**: Import tests tell you modules load. End-to-end tests tell you the **system works as designed**.

**The difference**:
- Import test: "Can I load the gun?"
- E2E test: "Can I fire the gun and hit the target?"

Both are necessary. We've done imports. Now we verify the full cycle.
`─────────────────────────────────────────────────`

---

**Ready to verify!** Start with `start_mcp.bat` and work through the steps above.

**DITEMPA BUKAN DIBERI** - Verification through execution, not assumption.

**Status:** `[v47.0.0 | 12F | READY FOR E2E TESTING]` ✅
