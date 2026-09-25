---
name: wayfinder
description: >-
  Use this skill when exploring, mapping, or breaking down a large, complex, or ambiguous objective before creating formal specifications or tickets.
  It coordinates investigation, domain clarification, and architecture discovery without modifying production code.
---

# Wayfinder Workflow

The Wayfinder skill is an orchestration and exploration workflow used to navigate large, complex, or ambiguous software challenges. It clears the fog before committing to implementation by exploring the codebase, clarifying domain concepts, and creating an investigation map.

---

## 1. Prerequisites & Context Gathering

Before initiating any exploration, review existing durable project context:

1. Read **`CONTEXT.md`** at the repository root to understand domain boundaries, non-goals, and the ubiquitous language glossary.
2. Read relevant Architectural Decision Records in **`docs/adr/`**.
3. Review **`AGENTS.md`** and **`docs/agents/`** for project guidelines and workflow rules.

If any of these files do not exist, proceed silently without suggesting their creation upfront unless triggered by domain modeling.

---

## 2. Exploration & Investigation Loop

When given a broad request or complex technical challenge:

1. **Map the Architecture**:
   * Search the codebase for entry points, data models, routes, and services (`src/api.py`, `src/sync_service.py`, `app.py`, `src/config.py`).
   * Identify key integration boundaries (e.g., BotNext API client, PostgreSQL repositories, Streamlit UI components).

2. **Domain Alignment**:
   * Verify whether the terms used in the request match the glossary in `CONTEXT.md`.
   * If ambiguous domain terms or unresolved architectural decisions are encountered, invoke the `domain-modeling` skill to resolve language or record an ADR in `docs/adr/`.

3. **Identify Unknowns & Risk Areas**:
   * Document technical risks, external API constraints, performance bottlenecks, or security requirements (e.g., data redaction).
   * Note any missing test coverage or environment requirements.

---

## 3. Investigation Artifact Generation

Summarize the exploration findings into a structured Wayfinder Map:

```markdown
# Wayfinder Map: [Objective Title]

## Objective Summary
Clear statement of what needs to be accomplished and why.

## Codebase Context & Touchpoints
- Core modules involved: [e.g., src/sync_service.py, src/api.py]
- Existing tests: [e.g., tests/test_runtime_processes.py]

## Key Findings & Architecture Constraints
- Finding 1: [Details]
- Finding 2: [Details]
- ADR References: [e.g., docs/adr/0001-production-runtime-architecture.md]

## Identified Domain Concepts
- [Terms matching CONTEXT.md or updates needed]

## Recommended Next Steps
1. Formalize specification using `/to-spec`.
2. Slice into tracer-bullet issues using `/to-tickets`.
```

---

## 4. Execution Guidance

- Do **not** modify business or application code during the Wayfinder phase.
- Pass the completed Wayfinder Map forward as input to `/to-spec` or `/to-tickets`.
