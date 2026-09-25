---
name: to-spec
description: >-
  Use this skill when converting requirements, user requests, or Wayfinder investigation maps into a formal, structured specification set inside specs/XXX-feature/.
---

# To-Spec Workflow

The `to-spec` skill transforms raw requirements, feature requests, or exploration notes into a rigorous, standard specification package. It establishes clear scope, acceptance criteria, technical design, and validation requirements before code execution.

---

## 1. Specification Artifact Package

Every feature specification created with `to-spec` MUST reside in `specs/XXX-feature/` and include four core files:

```text
specs/XXX-feature/
├── spec.md          # User stories, requirements, acceptance criteria & non-goals
├── plan.md          # Technical approach, architecture impact & phase breakdown
├── tasks.md         # Granular, ordered task list with story tags & checkpoints
└── validation.md    # Test execution evidence, runtime verification & deploy gates
```

---

## 2. Step-by-Step Workflow

### Step 1: Directory Setup
1. Identify the next feature number (e.g., `004-new-feature`).
2. Create the directory `specs/00X-feature/`.

### Step 2: Draft `spec.md`
Define the functional and non-functional requirements:
- **Title & Overview**: Clear feature goal and business value.
- **User Stories**: Prioritized list (P1, P2, P3) with specific acceptance criteria.
- **Domain Alignment**: Verify all terms match `CONTEXT.md`. If new terms are needed, trigger `/domain-modeling`.
- **Non-Goals & Constraints**: Explicitly list out-of-scope items and security/isolation constraints.

### Step 3: Draft `plan.md`
Define the technical strategy:
- **Architecture Impact**: Affected modules (`src/`, `tests/`, `app.py`, `compose.yaml`).
- **Data Model & Schemas**: Verify if database changes are needed. (Zero-migration rule unless explicitly planned).
- **Security & Redaction**: Ensure sensitive values (DSNs, passwords, phones) are sanitized.
- **Phase Breakdown**: Setup, Foundational, User Stories, and Polish phases.

### Step 4: Draft `tasks.md`
Slice the plan into actionable tasks:
- Format: `- [ ] T001 [P?] [Story] Task description with exact target files`
- Tag parallelable tasks with `[P]`.
- Include clear checkpoints after each user story phase.

### Step 5: Draft `validation.md`
Establish verification requirements:
- Command line execution strings (e.g., `.venv\Scripts\python.exe -m pytest`).
- Required pass counts and evidence templates.
- Explicit production deployment gate status.

---

## 3. Quality & Completeness Rules

- Do not start writing application code during `to-spec`.
- Ensure all stories have measurable acceptance criteria.
- Maintain absolute alignment with `AGENTS.md` rules and existing ADRs in `docs/adr/`.
