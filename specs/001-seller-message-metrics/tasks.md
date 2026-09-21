---

description: "Implementation tasks for seller message usage metrics"
---

# Tasks: Metricas de utilizacao por vendedor

**Input**: Design documents from `/specs/001-seller-message-metrics/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/dashboard-ui.md`, `quickstart.md`

**Tests**: Automated tests are included because the plan requires pytest coverage for the new business rules. Write each story's tests first and confirm they fail for the expected reason before implementing that story.

**Organization**: Tasks are grouped by user story so each increment can be implemented and validated before the next priority.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel without incomplete dependencies or file conflicts
- **[Story]**: Maps the task to US1, US2, or US3 from `spec.md`
- Every task includes an exact repository-relative file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the existing project for automated business-rule tests without adding unrelated tooling.

- [X] T001 Add a pinned pytest dependency compatible with Python 3.13 to `requirements.txt`, install it in the active environment, and verify `python -m pytest --version` succeeds

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Expose the persisted sender identity needed by every story without changing schema or synchronization.

- [X] T002 Add `mensagem.user_id AS usuario_id_mensagem` to the existing dashboard projection in `src/dashboard_repository.py`, preserving all joins and read-only behavior; enforce the model constraint "Deve estar preenchido para comprovar remetente humano; valores vazios excluem automacoes"

**Checkpoint**: The dashboard dataset contains stable message identity, sender identity, direction, date, channel, and the current `vendedor_responsavel`; no migration or synchronization file changed.

---

## Phase 3: User Story 1 - Consultar utilizacao por vendedor (Priority: P1) MVP

**Goal**: Let the CEO choose a period and see the number of messages actually sent by each currently identified seller, excluding received messages, automation, and duplicates.

**Independent Test**: With a deterministic dataframe containing `TO_HUB`, `FROM_HUB`, automation, repeated IDs, identified sellers, and a missing seller, select a period and verify that only eligible unique messages are counted under the correct seller or `Não identificado`.

### Tests for User Story 1

- [X] T003 [US1] Create failing pytest cases in `tests/test_seller_metrics.py` for inclusive period boundaries, exclusion of `FROM_HUB`, exclusion of empty `usuario_id_mensagem`, one count per repeated `mensagem_id`, fallback to `Não identificado`, input immutability, missing message identity, and conflicting duplicate seller assignments; enforce verbatim constraints "Identidade logica usada para deduplicacao; nao pode estar vazia nas mensagens elegiveis", "Somente `TO_HUB` e elegivel para utilizacao do vendedor", and "Duplicatas com o mesmo ID e vendedores conflitantes sao erro de integridade"

### Implementation for User Story 1

- [X] T004 [US1] Implement the pure period-based eligibility, integrity validation, deduplication, seller normalization, and per-seller counting function in `src/seller_metrics.py`, returning a stable empty result when no messages qualify and never mutating the input dataframe
- [X] T005 [US1] Build the metric input from the unmodified loaded dataframe and the existing inclusive period control in `app.py`, call `src/seller_metrics.py`, and render the basic per-seller sent-message counts in the existing `Vendedores` tab without changing `src/vendedor_service.py` or any synchronization path
- [X] T006 [US1] Handle incomplete/invalid periods and aggregation integrity failures in `app.py` with safe user guidance and module logging that excludes message text, personal data, credentials, and payloads; do not display partial metric results after an integrity failure

**Checkpoint**: US1 passes `python -m pytest tests/test_seller_metrics.py -q` and the dashboard shows period-based counts that exclude received, automated, and duplicate messages.

---

## Phase 4: User Story 2 - Comparar participacao dos vendedores (Priority: P2)

**Goal**: Present a deterministic ranking, reconciled total, and percentage participation for every seller in the current period.

**Independent Test**: With known message volumes for three sellers, verify descending volume order, alphabetical tie-break, exact reconciliation between row counts and total, full-precision percentages, and 100% participation for an all-unidentified dataset.

### Tests for User Story 2

- [X] T007 [US2] Add failing pytest cases in `tests/test_seller_metrics.py` for total reconciliation, full-precision percentage calculation, deterministic sort by count descending then seller ascending, empty-result semantics, and all-unidentified participation; enforce verbatim constraints "Soma exata de `mensagens_enviadas` de todas as linhas", "`mensagens_enviadas / total_geral * 100`, sem arredondamento interno", and "Verdadeiro quando `total_geral == 0`; nao ha percentuais nesse estado"

### Implementation for User Story 2

- [X] T008 [US2] Extend the result from `src/seller_metrics.py` with `total_geral`, ordered seller rows, full-precision `participacao_percentual`, and presentation position while guaranteeing that row counts reconcile exactly with the total
- [X] T009 [US2] Replace the basic US1 presentation in `app.py` with the `Mensagens enviadas por vendedores` total and ranking columns `Posicao`, `Vendedor`, `Mensagens enviadas`, and `Participacao`, formatting percentages to one decimal only at the Streamlit presentation boundary

**Checkpoint**: US1 and US2 tests pass, the displayed total equals the sum of all seller rows, and ties remain stable across reruns.

---

## Phase 5: User Story 3 - Refinar analise por canal (Priority: P3)

**Goal**: Reuse the existing channel filter so total, ranking, and percentages reflect selected channels and clearly report selections with no eligible messages.

**Independent Test**: Use messages from at least two channels, select one channel, and verify every output uses only that channel; then select a channel/period with no eligible messages and verify total zero plus the explicit empty state.

### Tests for User Story 3

- [X] T010 [US3] Add failing pytest cases in `tests/test_seller_metrics.py` for no channel selection meaning all channels, one and multiple selected channels, selected channel with no eligible messages, and isolation from unrelated filter columns; enforce the model constraint "Lista vazia significa todos os canais; valores devem vir das opcoes existentes"

### Implementation for User Story 3

- [X] T011 [US3] Extend the selection accepted by `src/seller_metrics.py` with channel labels, applying period and channel before eligibility and deduplication while preserving the US1 and US2 result contract
- [X] T012 [US3] Pass the existing `canais_selecionados` value to the independent metric pipeline in `app.py`, ensure seller/status/type/direction/origin/text filters do not change or suppress this metric, and render total zero plus `Nenhuma mensagem enviada por vendedores no periodo e canal selecionados.` without an empty ranking when no eligible rows exist

**Checkpoint**: All three stories pass automated tests and the dashboard metric changes only when period or channel changes.

---

## Phase 6: Polish & Cross-Cutting Validation

**Purpose**: Verify the complete feature against its quality, security, and performance contracts.

- [X] T013 Run `python -m pytest tests/test_seller_metrics.py -q` and a Python syntax check for `app.py`, `src/dashboard_repository.py`, and `src/seller_metrics.py`, resolving only feature-related failures in those files and `tests/test_seller_metrics.py`
- [X] T014 Execute every end-to-end and performance scenario in `specs/001-seller-message-metrics/quickstart.md`, confirm updates complete within 5 seconds at normal volume, and append a dated `Validation Results` section to `specs/001-seller-message-metrics/quickstart.md` without recording credentials, message text, or personal data

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Starts immediately.
- **Foundational (Phase 2)**: Depends on T001 and blocks all user stories.
- **US1 (Phase 3)**: Depends on T002 and delivers the MVP.
- **US2 (Phase 4)**: Depends on US1 because it extends the same aggregate with total, ordering, and percentages.
- **US3 (Phase 5)**: Depends on US2 because channel selection must update the completed total and ranking contract.
- **Polish (Phase 6)**: Depends on all selected stories.

### User Story Dependency Graph

```text
Setup -> Foundation -> US1 (P1 / MVP) -> US2 (P2) -> US3 (P3) -> Polish
```

### Within Each User Story

1. Add the story's tests and confirm they fail for the expected missing behavior.
2. Implement or extend the pure aggregation contract.
3. Integrate the completed contract into `app.py`.
4. Run all tests accumulated through that story before crossing its checkpoint.

### Parallel Opportunities

No implementation tasks are marked `[P]`. This feature is intentionally sequential: all stories extend the same pure function and Streamlit section, and each test task must precede its implementation to preserve the planned red-green workflow. Parallel work would create file conflicts or bypass a test dependency.

## Parallel Execution Examples

### User Story 1

No safe parallel execution. Complete `T003 -> T004 -> T005 -> T006` so eligibility tests define the contract before the metric and UI are written.

### User Story 2

No safe parallel execution. Complete `T007 -> T008 -> T009` because the UI depends on the tested summary shape.

### User Story 3

No safe parallel execution. Complete `T010 -> T011 -> T012` because channel wiring depends on the tested selection semantics.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001-T002.
2. Complete T003-T006.
3. Stop and validate the US1 checkpoint independently.
4. Demo period-based per-seller counts before adding comparative outputs.

### Incremental Delivery

1. **US1**: Correct seller usage counts for a period.
2. **US2**: Add management comparison through total, ranking, and percentage.
3. **US3**: Add channel analysis and the final empty-state/filter-isolation contract.
4. **Polish**: Run full regression, manual contract, and performance validation.

## Notes

- Do not alter `src/sync_*.py`, `src/botnext_client.py`, `src/message_repository.py`, or `src/vendedor_service.py` for this feature.
- Do not add a migration or new table; the required fields already exist in PostgreSQL.
- Keep `mensagem_id` as the sole deduplication identity and `vendedor_responsavel` as the seller attribution source.
- Keep full-precision percentages in business logic and round only for display.
- Commit after each completed task or cohesive red-green pair.
