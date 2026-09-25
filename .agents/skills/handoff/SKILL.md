---
name: handoff
description: >-
  Use this skill when completing a working session, pausing a task, or transferring context to another agent or developer.
  Generates a clean, durable summary of current progress, active state, uncommitted changes, and clear next steps.
---

# Handoff Workflow

The `handoff` skill creates a durable, standardized session summary at the end of a work unit or conversation turn. It ensures seamless context transfers between human engineers and AI agents without loss of active state.

---

## 1. Handoff Structure

Every handoff report MUST include five essential sections:

1. **Task Overview & Objectives**: Summary of the original request and constraints.
2. **Current State & Progress**: What has been implemented, tested, and verified.
3. **Working Tree & Artifact Status**: Modified/untracked files, test results, and evidence files.
4. **Open Risks & Blockers**: Unresolved questions, pending deploy gates, or platform constraints.
5. **Clear Next Steps**: Explicit, ordered instructions for the next agent or session.

---

## 2. Handoff Template

```markdown
# Session Handoff Report

## 1. Summary of Accomplishments
- Implemented: [Feature / Task X]
- Verified: [Test suite status, e.g., 64 passed, 0 failed]

## 2. Environment & Working Tree State
- Branch: `[branch-name]`
- Uncommitted Changes:
  - Modified: `[list files]`
  - Untracked: `[list files]`
- Unsent Commits/Pushes: Zero (no git commit/push made).

## 3. Key Findings & Empirical Evidence
- Key test execution results or log paths.
- Active ADR references (`docs/adr/`).
- `validation.md` / `tasks.md` status.

## 4. Open Risks & Governance Gates
- Deploy Gate: Production deploy remains BLOQUEADO until Feature 002.

## 5. Next Steps for Next Session
1. Step 1...
2. Step 2...
```

---

## 3. Best Practices

- Always run `git status` before generating a handoff report to capture the exact working tree state.
- Never claim a task is completed if tests or verification steps are still pending.
- Ensure all sensitive data (passwords, DSNs) is redacted from handoff summaries.
