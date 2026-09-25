---
name: implement
description: >-
  Use this skill when executing planned tasks, implementing feature specs from specs/XXX-feature/tasks.md, or fulfilling GitHub issues.
  Guarantees test-driven, verifiable progress with empirical evidence before completion.
---

# Implement Workflow

The `implement` skill guides the step-by-step execution of technical tasks and feature specifications. It enforces strict adherence to contracts, continuous test verification, and documentation updating without skipping validation.

---

## 1. Execution Protocol & Core Principles

1. **Obey Explicit Directives**: Follow `spec.md`, `plan.md`, and `tasks.md` without altering quantitative limits or architectural boundaries.
2. **Never Guess Logic or Schemas**: Inspect source code (`src/`, `tests/`) and `CONTEXT.md` before writing code.
3. **No Superficial Symptom Patches**: Fix root causes; never swallow exceptions or comment out failing assertions.
4. **Empirical Verification Required**: NEVER claim a task is finished without executing tests/builds and gathering clean passing output.
5. **No Unsanctioned Commits/Pushes**: Perform no `git commit` or `git push` unless explicitly instructed.

---

## 2. Step-by-Step Implementation Loop

### Step 1: Context & Task Selection
1. Read the target task in `specs/XXX-feature/tasks.md` or the relevant GitHub Issue.
2. Verify prerequisites and dependent tasks are completed.
3. Review associated ADRs in `docs/adr/` and domain terms in `CONTEXT.md`.

### Step 2: Test First (TDD Integration)
1. Invoke `/tdd` to write failing characterization or contract tests in `tests/`.
2. Run `.venv\Scripts\python.exe -m pytest` to confirm the test fails for the expected reason.

### Step 3: Minimal Code Implementation
1. Write the minimum production code in `src/` or `app.py` necessary to satisfy the test.
2. Maintain sensitive data redaction (`src/runtime_security.py`).
3. Ensure no schema migrations or DDL edits are introduced unless explicitly mandated.

### Step 4: Empirical Verification
1. Run the test suite: `.venv\Scripts\python.exe -m pytest`.
2. If infrastructure or container changes are involved, run smoke tests with required environment flags (`$env:RUN_DOCKER_SMOKE="1"`, `$env:RUN_POSTGRES_INTEGRATION="1"`).
3. Confirm 100% clean exit (code 0) and zero unexpected skips or failures.

### Step 5: Update Task & Validation Evidence
1. Mark the completed task `[X]` in `specs/XXX-feature/tasks.md`.
2. Record execution logs, pass counts, and evidence in `specs/XXX-feature/validation.md`.
3. Provide a concise summary to the user.
