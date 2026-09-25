---
name: domain-modeling
description: >-
  Use this skill when defining, refining, or challenging domain terminology, bounded contexts, ubiquitous language in CONTEXT.md, or recording architectural decisions in docs/adr/.
---

# Domain Modeling Workflow

The `domain-modeling` skill maintains the integrity of the project's ubiquitous language, domain boundaries, and architectural decision records. It prevents term drift, resolves naming ambiguity, and documents durable design choices.

---

## 1. Core Principles

1. **Ubiquitous Language**: Every domain concept used in code, issue titles, test names, and specifications MUST match the canonical terms defined in `CONTEXT.md`.
2. **Single Source of Truth**: The project uses a single-context model centered on `CONTEXT.md` at the repository root.
3. **Durable Architecture Decisions**: Structural choices, trade-offs, and technology selection MUST be documented as ADRs in `docs/adr/`.

---

## 2. When to Invoke Domain Modeling

Trigger this skill whenever:
- A new business concept, entity, or process is introduced into the project.
- Multiple conflicting terms are being used for the same concept (e.g., "ticket" vs "sessão", "atendente" vs "vendedor").
- An architectural decision is made (e.g., adopting a new database strategy, isolation model, or authentication pattern).
- An output or specification contradicts an existing ADR in `docs/adr/`.

---

## 3. Workflow Steps

### Step 1: Challenge Terminology
1. Check `CONTEXT.md` for existing definitions.
2. If a proposed term conflicts with `CONTEXT.md`, challenge it:
   > *The term "ticket" is used in this proposal, but CONTEXT.md explicitly defines this as "Sessão". Updating proposal to align with ubiquitous language.*
3. If a term is missing from `CONTEXT.md`, determine if it represents a genuine new domain concept or a synonym that should be avoided.

### Step 2: Update `CONTEXT.md`
When a new domain term or boundary is agreed upon:
1. Open `CONTEXT.md`.
2. Add the term, definition, and explicit "avoid" synonyms to the Glossary table:
   ```markdown
   | Termo | Definição no Domínio | Termos a Evitar |
   | :--- | :--- | :--- |
   | **[Novo Termo]** | [Definição precisa] | *[Sinônimo 1]*, *[Sinônimo 2]* |
   ```

### Step 3: Record Architectural Decisions (ADR)
When making an architectural or design choice:
1. Determine the next sequential number in `docs/adr/` (e.g., `docs/adr/0002-title.md`).
2. Copy the structure from `docs/adr/0000-template.md`.
3. Fill out the ADR fields completely:
   - **Status**: [Proposto | Aceito | Substituído]
   - **Contexto e Problema**: Requirements, constraints, and operational context.
   - **Decisão Considerada**: Chosen architecture and rationale.
   - **Consequências**: Positive outcomes and trade-offs/risks.
4. Save the file and reference it in specifications or relevant PRs.

---

## 4. Conflict Resolution Protocol

If new work contradicts an existing ADR:
1. Surface the contradiction explicitly:
   > ⚠️ *Attention: This change contradicts ADR-0001 (Production Runtime Architecture). Reason for reopening: [Justification]*
2. Do not silently override an ADR. Update the existing ADR status to "Substituído por ADR-XXXX" only after formal alignment.
