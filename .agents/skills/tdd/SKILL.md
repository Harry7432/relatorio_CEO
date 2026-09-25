---
name: tdd
description: >-
  Use this skill when developing new features or fixing bugs using Test-Driven Development (Red -> Green -> Refactor).
  Enforces writing failing tests before writing production implementation.
---

# TDD (Test-Driven Development) Workflow

The `tdd` skill enforces the strict Test-Driven Development cycle (*Red -> Green -> Refactor*). It ensures that no production code is written without a pre-existing, failing test that defines the expected behavior.

---

## 1. The Three Rules of TDD

1. **Write NO production code** except to pass a failing unit/integration test.
2. **Write NO more of a test** than is sufficient to fail (compilation/import failures count as failures).
3. **Write NO more production code** than is sufficient to pass the one failing test.

---

## 2. The Red -> Green -> Refactor Cycle

```text
  +---------------------------------------------------+
  |                                                   |
  v                                                   |
[ RED ] ---> Run Test (Must Fail)                     |
  |                                                   |
  v                                                   |
[ GREEN ] -> Write Minimal Code -> Run Test (Passes)  |
  |                                                   |
  v                                                   |
[ REFACTOR ] -> Clean Code/Tests -> Re-verify (Passes)+
```

---

## 3. Step-by-Step Execution Guide

### Phase 1: RED (Write Failing Test)
1. Locate or create the target test file in `tests/` (e.g., `tests/test_runtime_api.py`).
2. Write a precise test function specifying the expected contract, assertions, or response formats.
3. Execute pytest:
   ```powershell
   .venv\Scripts\python.exe -m pytest tests/test_target.py -k test_name -vv
   ```
4. **VERIFY**: The test MUST fail. Read the failure output and stack trace to ensure it fails for the *right reason* (missing feature, assertion mismatch), not a syntax error.

### Phase 2: GREEN (Make Test Pass)
1. Write the minimal amount of code in `src/` needed to make the test pass.
2. Avoid over-engineering or implementing future requirements prematurely.
3. Re-run pytest:
   ```powershell
   .venv\Scripts\python.exe -m pytest tests/test_target.py -k test_name -vv
   ```
4. **VERIFY**: The test MUST pass with exit code 0.

### Phase 3: REFACTOR (Improve Code Quality)
1. Clean up duplicated code, improve variable names, and ensure sensitive data redaction (`src/runtime_security.py`).
2. Ensure domain terms align with `CONTEXT.md`.
3. Re-run the full test suite to confirm no regressions:
   ```powershell
   .venv\Scripts\python.exe -m pytest
   ```

---

## 4. Anti-Patterns & Prohibitions

- ❌ Writing production code first and tests afterwards.
- ❌ Testing implementation details instead of public behavior and contracts.
- ❌ Ignoring warnings or suppressing exceptions to force a pass.
- ❌ Deleting or commenting out existing tests to mask regressions.
