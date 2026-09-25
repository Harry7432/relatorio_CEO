---
name: to-tickets
description: >-
  Use this skill when converting a feature specification (from specs/XXX-feature/tasks.md) or roadmap into GitHub Issues using the gh CLI and the project's 5-label triage vocabulary.
---

# To-Tickets Workflow

The `to-tickets` skill converts feature tasks and specifications into actionable, independent units of work published as GitHub Issues via the `gh` CLI. It applies the repository's triage vocabulary and establishes clear task dependencies.

---

## 1. Issue Tracker Rules & Vocabulary

This project uses **GitHub Issues** managed exclusively via the `gh` CLI.

### Standard Triage Labels
Every created issue MUST be tagged with exactly one of the five default triage labels:
- `needs-triage`: Newly created issue requiring initial review and scope definition.
- `needs-info`: Blocked due to missing information, requirements, or reproduction steps.
- `ready-for-agent`: Fully specified and scoped, ready for automated agent implementation.
- `ready-for-human`: Requires human intervention, secret key provisioning, or manual approval.
- `wontfix`: Out of scope or declined.

---

## 2. Step-by-Step Ticket Creation Protocol

### Step 1: Read the Source Specification
1. Inspect `specs/XXX-feature/tasks.md` and `spec.md`.
2. Group related tasks into logical "tracer-bullet" tickets sized to fit cleanly within a single work unit.

### Step 2: Formulate Ticket Content
For each issue, define:
- **Title**: Clear, imperative summary (e.g., `[Feature 003] Add readiness probe with PostgreSQL healthcheck`).
- **Body**:
  - Context & Goal.
  - Linked User Story from `spec.md`.
  - Exact target files to be created or modified.
  - Acceptance Criteria & Verification Commands.
  - Dependencies (blocking issue numbers or prerequisites).

### Step 3: Publish via GitHub CLI (`gh`)
Execute the ticket creation using `gh`:

```bash
gh issue create \
  --title "[Feature-00X] Task description" \
  --body-file "path/to/issue_body.md" \
  --label "ready-for-agent"
```

If `gh` CLI is not authenticated or unavailable in the environment:
1. Log the formatted markdown for each ticket.
2. Provide explicit `gh issue create` commands for manual execution.

---

## 3. Verification & Mapping

- Update `tasks.md` with created GitHub Issue numbers (e.g., `#123`).
- Ensure no issue contains sensitive credentials, API keys, or raw connection strings.
