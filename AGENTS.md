## Agent skills

Local skills for this workspace are configured under `.agents/skills/`:
- `wayfinder`: Exploration, codebase mapping, and investigation before specification.
- `domain-modeling`: Ubiquitous language management in `CONTEXT.md` and ADR records in `docs/adr/`.
- `to-spec`: Specification package generation in `specs/XXX-feature/`.
- `to-tickets`: Slicing specs into GitHub Issues using `gh` CLI and default triage labels.
- `implement`: Test-driven execution of feature tasks and specifications.
- `tdd`: Strict Red-Green-Refactor development cycle.
- `code-review`: Dual-axis review against specs, quality, security, and test requirements.
- `diagnosing-bugs`: Empirical log inspection and root-cause bug diagnosis.
- `handoff`: Session state consolidation and context transfer.

### Issue tracker

Issues live as GitHub issues, worked via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.