---
name: code-review
description: >-
  Use this skill when reviewing code changes, diffs, or working tree state against specifications, architecture rules, test coverage, and security requirements.
---

# Code-Review Workflow

The `code-review` skill performs a dual-axis review of uncommitted working tree changes, pull requests, or feature branches. It evaluates code against both documented feature specifications (`spec.md`) and repository quality standards.

---

## 1. Dual-Axis Review Principles

1. **Specification Axis**: Does the code fulfill all requirements, user stories, and acceptance criteria in `specs/XXX-feature/spec.md` without introducing unauthorized features or scope drift?
2. **Quality & Architecture Axis**: Does the code adhere to `AGENTS.md`, `CONTEXT.md`, existing ADRs (`docs/adr/`), test standards, and sensitive-data redaction?

---

## 2. Review Execution Steps

### Step 1: Gather Context & Diffs
1. Check git status and modified/untracked files:
   ```powershell
   git status
   git diff
   ```
2. Read the corresponding specification (`specs/XXX-feature/spec.md`, `plan.md`, `tasks.md`).
3. Read `CONTEXT.md` and relevant ADRs in `docs/adr/`.

### Step 2: Categorized Finding Evaluation
Examine the changes across 5 distinct categories:

1. **Desvios da Spec (Specification Deviations)**:
   - Missing acceptance criteria.
   - Out-of-scope additions or unapproved behavior changes.

2. **Problemas de Arquitetura e Design (Architecture & Design)**:
   - Contradictions with ADRs or `CONTEXT.md` terms.
   - Coupling between API, worker, and frontend.
   - Unauthorized database DDL/schema changes.

3. **Problemas de Segurança e Privacidade (Security & Privacy)**:
   - Exposure of DSNs, passwords, API keys, or raw phone numbers in logs, exceptions, or UI.
   - Non-root container execution violations (`USER app`).

4. **Problemas de Testes (Testing & Verification)**:
   - Skipped or missing tests.
   - Mocking without contract verification.
   - Flaky temp directory or network connection logic.

5. **Problemas de Empacotamento e Deploy (Packaging & Deploy)**:
   - Unpinned dependencies in `requirements.txt`.
   - Broken Docker build args or Compose defaults.
   - Deploy gate violations (e.g., activating production cron before Feature 002).

---

## 3. Findings Classification & Severity Matrix

Classify every finding using exact severity levels:

- **`CRITICAL`**: Security credential leaks, database corruption risks, broken production deploy gates, or failing core tests. Must be fixed before any commit.
- **`HIGH`**: Specification contract breaches, broken process isolation, or missing redaction in logs. Must be fixed before commit.
- **`MEDIUM`**: Test flakiness, missing edge-case handling, or unpinned dependencies. Recommend fixing before commit.
- **`LOW`**: Code style formatting, minor docstring typos, or non-blocking cleanup. Can wait.

---

## 4. Final Review Report Format

Structure the output report clearly:

```markdown
# Code Review: [Branch / Feature Name]

## 1. Findings por Categoria e Severidade
### Desvios da Spec
- [CRITICAL/HIGH/MEDIUM/LOW] Description and location.

### Arquitetura & Design
- [CRITICAL/HIGH/MEDIUM/LOW] Description and location.

### Segurança & Privacidade
- [CRITICAL/HIGH/MEDIUM/LOW] Description and location.

### Testes & Cobertura
- [CRITICAL/HIGH/MEDIUM/LOW] Description and location.

### Empacotamento & Deploy
- [CRITICAL/HIGH/MEDIUM/LOW] Description and location.

## 2. Resumo de Itens Corretos e Validados
- Feature/Module X correctly satisfies contract Y.

## 3. Conclusão e Prontidão para Commit
- **Findings a corrigir antes de commit**: [List or "Nenhum"]
- **Pronto para Commit/Validação**: [SIM / NÃO / BLOQUEADO POR GERAL]
```
