---
name: diagnosing-bugs
description: >-
  Use this skill when investigating bugs, runtime exceptions, failing test suites, or unexpected system behavior.
  Enforces empirical log inspection and root-cause analysis before changing code.
---

# Diagnosing-Bugs Workflow

The `diagnosing-bugs` skill provides a disciplined, empirical methodology for investigating software defects and runtime failures. It prevents diagnostic guesswork, superficial symptom patching, and blind code mutations.

---

## 1. Absolute Directives for Bug Diagnosis

1. **NEVER Guess Root Causes**: Form zero hypotheses without reading the exact un-truncated log files and stack traces.
2. **Inspect Logs FIRST**: Your very first action when a failure occurs MUST be fetching and viewing the full error log.
3. **No Superficial Symptom Patches**: Do NOT fix errors by swallowing exceptions (`try...except: pass`), returning dummy fallbacks (`return []`), or deleting broken assertions.
4. **Trace Upstream Data**: If an API or function returns `None` or missing data, trace the upstream provider instead of wrapping the caller in a silent try/except.
5. **Traceback Justification Required**: Every code or configuration edit during debugging MUST be justified by an explicit traceback line or verified root cause.

---

## 2. Step-by-Step Investigation Loop

### Step 1: Log & Traceback Extraction
1. Obtain the complete un-truncated error output from pytest, terminal, or background task log files (e.g., `.system_generated/tasks/task-XXX.log`).
2. Identify the exact file path, line number, exception type, and stack trace frames.

### Step 2: Empirical Reproduction
1. Isolate the failing test or command line:
   ```powershell
   .venv\Scripts\python.exe -m pytest tests/test_failing.py -k test_failing_function -vv
   ```
2. Verify if the error is deterministic or environment-dependent (e.g., Windows temp directory cleanup, IPv6 `localhost` probe timeout, missing environment variables).

### Step 3: Root-Cause Analysis
1. Examine the source code around the traceback lines (`view_file`).
2. Verify object initialization, non-null states, file paths, and parameter types.
3. Check for platform-specific edge cases (Windows paths, encoding, subprocess timeouts).

### Step 4: Minimum Root-Cause Fix
1. Formulate a targeted fix addressing the root cause contract break.
2. Apply the edit using `replace_file_content`.

### Step 5: Verification & Regression Check
1. Re-run the isolated failing test to confirm clean pass.
2. Re-run the complete test suite (`.venv\Scripts\python.exe -m pytest`) to confirm zero regressions.

---

## 3. Post-Mortem Report Format

```markdown
# Bug Diagnosis Report

## 1. Symptom & Traceback Summary
- Exception: `[ExceptionType: Error message]`
- Location: `[file.py:line_number]`

## 2. Root Cause Analysis
- Detailed technical explanation of why the failure occurred.

## 3. Root-Cause Fix
- Description of the contract/code fix applied.

## 4. Verification Evidence
- Test execution output proving clean pass (exit code 0).
```
